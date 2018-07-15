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

registrations = []
threads = []
pakets = []
updates = []
updates = []


def update_paket_lists():
	pakets = []
	upgrades = []
	updates = []
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
	print('Send paket: %s' % paket)


def send_update(paket, client_msg):
	print('Send update: %s' % paket)


def send_upgrade(paket, client_msg):
	print('Send upgrade: %s' % paket)


def client_killer():
	while 1:
		sleep(1)
		for registration in registrations:
			registrations.remove(registration)
			client_msg, client_heartbeat, time = registration
			print(time)
			if time > 0:
				time -= 1
				registration = (client_msg, client_heartbeat, time)
				registrations.append(registration)
			else:
				client_heartbeat.close()
				client_msg.close()

def listen_to_hearbeat(client_hb):
	while 1:
		heartbeat = client_hb.recv(1023).decode('utf-8')
		if heartbeat == CONST_HEARTBEAT:
			for registration in registrations:
				client_msg, client_heartbeat, time = registration
				if client_heartbeat == client_hb:
					time = CONST_INIT_LIFETIME
				registrations.remove(registration)
				registrations.append((client_msg, client_heartbeat, time))


def listen_to_client(client_msg):
	try:
		while 1:
			msg = client_msg.recv(1023).decode('utf-8')

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
	thread1 = threading.Thread(target=client_killer)
	thread1.start()
	threads.append(thread1)
	try:
		while 1:
			# Accept connection request from client
			client_msg, addr_msg = sock.accept()
			flag1 = client_msg.recv(1023).decode('utf-8')
			print("Server: Connected with %s via port %d [msg]" % addr_msg)
			
			client_heartbeat, addr_heartbeat = sock.accept()
			flag2 = client_heartbeat.recv(1023).decode('utf-8')
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
	
