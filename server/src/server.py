#!/usr/bin/env python3

import socket
import sys
import threading
import os
import glob

from time import sleep
from socket import SHUT_RDWR

CONST_INIT_LIFETIME = 10
CONST_HEARTBEAT = '/lifetime.reset()'
CONST_INSTALL = '/install'
CONST_UPDATE = '/update'
CONST_UPGRADE = '/upgrade'
CONST_BUFFER = 4096


registrations = []
threads = []
pakets = []
upgrades = []
updates = []


def update_paket_lists():
	"""
	Updates the lists with currently aviable pakets, upgrades and updates
	on the server by iterating over corresponding directories.
	"""
	global pakets
	global upgrades
	global updates
	# pakets
	os.chdir('./client pakets')
	for file in glob.glob('*py'):
		pakets.append(file)
	# upgrades
	os.chdir('../upgrades')
	for paket in glob.glob('*'):
		os.chdir(paket)
		for file in glob.glob('*.py'):
			upgrades.append(file)
		os.chdir('../')
	# updates
	os.chdir('../updates')
	for paket in glob.glob('*'):
		os.chdir(paket)
		for file in glob.glob('*.py'):
			updates.append(file)
		os.chdir('../')
	os.chdir('../')


def send_paket(paket, client_msg):
	"""
	Sends a requested paket to the client if aviable.

	:paket:
		Requested paket
	:client_msg:
		Socket of client which has requested the paket
	"""
	paket_exists = False
	for p in pakets:
		if p[:-8] == paket:
			paket = p
			paket_exists = True
			break
	if paket_exists:
		msg = 'Do you want to install %s? (y/n)' % paket
		client_msg.send(msg.encode())
		while 1:
			answer = client_msg.recv(CONST_BUFFER).decode('utf-8')
			if answer == 'y':
				client_msg.send(paket.encode())
				os.chdir('./client pakets/')
				with open(paket, 'rb') as file:
					data = file.read(CONST_BUFFER)
					while data:
						client_msg.send(data)
						data = file.read(CONST_BUFFER)
				os.chdir('../')
				break
			elif answer == 'n':
				break
	else:
		msg = 'Paket %s does not exist.' % paket
		client_msg.send(msg.encode())

def send_update(paket, client_msg):
	"""
	Checks if an update for the given paket is aviable and sends
	the latest update to the client.

	:paket:
		Paket that should be updated
	:client_msg:
		Socket of the client that has requested the update
	"""
	current_upgrade = int(paket[-6:-5])

	latest_update = paket
	for update in updates:
		if int(update[-6:-5]) == current_upgrade and int(update[-4:-3]) > int(latest_update[-4:-3]) and update[:-8] == paket[:-8]:
			latest_update = update

	if latest_update != paket:
		msg = 'Your version:\t%s\nLatest version:\t%s\nDo you want to install the latest version of %s? (y/n)' % (paket, latest_update, paket[:-8])
		client_msg.send(msg.encode())
		while 1:
			answer = client_msg.recv(CONST_BUFFER).decode('utf-8')
			if answer == 'y':
				client_msg.send(latest_update.encode())
				os.chdir('./updates/%s/' % paket[:-8])
				with open(latest_update, 'rb') as file:
					data = file.read(CONST_BUFFER)
					while data:
						client_msg.send(data)
						data = file.read(CONST_BUFFER)
				os.chdir('../../')
				break
			elif answer == 'n':
				break
	else:
		msg = '%s is up-to-date' % paket[:-8]
		client_msg.send(msg.encode())


def send_upgrade(paket, client_msg):
	"""
	Checks if an upgrade for the given paket is aviable and sends
	the latest upgrade to the client.

	:paket:
		Paket that should be upgraded
	:client_msg:
		Socket of the client that has requested the upgrade
	"""
	current_upgrade = int(paket[-6:-5])
	current_update = int(paket[-4:-3])

	latest_upgrade = paket
	for upgrade in upgrades:
		if int(upgrade[-6:-5]) > int(latest_upgrade[-6:-5]) and upgrade[:-8] == paket[:-8]:
			latest_upgrade = upgrade

	if latest_upgrade != paket:
		msg = 'Your version:\t%s\nLatest version:\t%s\nDo you want to install the latest version of %s? (y/n)' % (paket, latest_upgrade, paket[:-8])
		client_msg.send(msg.encode())
		while 1:
			answer = client_msg.recv(CONST_BUFFER).decode('utf-8')
			if answer == 'y':
				client_msg.send(latest_upgrade.encode())
				os.chdir('./upgrades/%s/' % paket[:-8])
				with open(latest_upgrade, 'rb') as file:
					data = file.read(CONST_BUFFER)
					while data:
						client_msg.send(data)
						data = file.read(CONST_BUFFER)
				os.chdir('../../')
				break
			elif answer == 'n':
				break
	else:
		msg = '%s is up-to-date' % paket[:-8]
		client_msg.send(msg.encode())


def client_killer():
	"""
	Continuous decreases the life time of clients by one every second. If
	the life time is equals zero the corresponding client will be ejected.
	"""
	while 1:
		sleep(1)
		for registration in registrations:
			registrations.remove(registration)
			client_msg, client_heartbeat, time = registration
			if time > 0:
				time -= 1
				registration = (client_msg, client_heartbeat, time)
				registrations.append(registration)
			else:
				client_heartbeat.close()
				client_msg.close()


def listen_to_hearbeat(client_hb):
	"""
	Continuous listen on heartbeat socket of connected client for
	heartbeat messages. If a heartbeat is received the life time of the
	corresponding client will be reset to initial life time.

	:client_hb:
		Seperate client socket for heartbeat messages
	"""
	while 1:
		heartbeat = client_hb.recv(CONST_BUFFER).decode('utf-8')
		if heartbeat == CONST_HEARTBEAT:
			for registration in registrations:
				client_msg, client_heartbeat, time = registration
				if client_heartbeat == client_hb:
					time = CONST_INIT_LIFETIME
				registrations.remove(registration)
				registrations.append((client_msg, client_heartbeat, time))


def listen_to_client(client_msg):
	"""
	Continuous listens to given client socket for messages. Deals with
	commands for the server and prints other received messages.

	:clients_msg:
		Message socket of corresponding client
	"""
	try:
		while 1:
			msg = client_msg.recv(CONST_BUFFER).decode('utf-8')

			if msg == CONST_HEARTBEAT:
				for registration in registrations:
					rclient, time = registration
					if rclient == client_msg:
						registrations.remove(registration)
						registrations.append((client_msg, CONST_INIT_LIFETIME))
			elif len(msg) >= 7 and msg[:7] == CONST_UPDATE:
				update_paket_lists()
				paket = msg[8:]
				send_update(paket, client_msg)
			elif len(msg) >= 8 and msg[:8] == CONST_UPGRADE:
				update_paket_lists()
				paket = msg[9:]
				send_upgrade(paket, client_msg)
			elif len(msg) >= 8 and msg[:8] == CONST_INSTALL:
				update_paket_lists()
				paket = msg[9:]
				send_paket(paket, client_msg)
			elif msg != '':
				print(msg)
	finally:
		client_msg.close()


def client_handler(sock):
	"""
	Accepts new client connections by setting up a message and a heartbeat
	socket for every client.

	:sock:
		Main sock of server which receives connection requests from clients
	"""
	thread1 = threading.Thread(target=client_killer)
	thread1.start()
	threads.append(thread1)
	try:
		while 1:
			# Accept connection request from client
			client_msg, addr_msg = sock.accept()
			flag1 = client_msg.recv(CONST_BUFFER).decode('utf-8')
			print("Server: Connected with %s via port %d [msg]" % addr_msg)
			
			client_heartbeat, addr_heartbeat = sock.accept()
			flag2 = client_heartbeat.recv(CONST_BUFFER).decode('utf-8')
			print("Server: Connected with %s via port %d [heartbeat]" % addr_heartbeat)
			if flag1 == 'msg' and flag2 == 'heartbeat':
				registrations.append((client_msg, client_heartbeat, CONST_INIT_LIFETIME))
				
				thread2 = threading.Thread(target=listen_to_hearbeat, args=(client_heartbeat,))
				thread2.start()

				thread3 = threading.Thread(target=listen_to_client, args=(client_msg,))
				thread3.start()
				threads.append(thread2)
	finally:
		sys.exit()


# command line input
host = sys.argv[1]
port = int(sys.argv[2])

# opens a listening socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
socket_address = (host, port)
sock.bind(socket_address)
sock.listen(socket.SOMAXCONN)


try:
	while 1:
		thread = threading.Thread(target=client_handler, args=(sock,))
		thread.start()
		threads.append(thread)

		# wait for command line input
		cmd_line_input = input()
		if cmd_line_input == 'close':
			break
finally:
	for registration in registrations:
		client, time = registration
		client.shutdown(SHUT_RDWR)
		client.close()
	# close socket
	sock.close()

	os._exit(1)
	
