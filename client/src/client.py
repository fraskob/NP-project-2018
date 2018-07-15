#!/usr/bin/env python3

import sys
import os
import socket
import threading
import glob

from time import sleep

CONST_HEARTBEAT_RATE = 5
CONST_HEARTBEAT = '/lifetime.reset()'
CONST_CHUNK_SIZE = 8 * 1024

installed_pakets = []

def update_installed_pakets():
	os.chdir('./pakets')
	for paket in glob.glob('*'):
		installed_pakets.append(paket)
	os.chdir('../')


def install_paket(paket_name, server_msg):
	update_installed_pakets()
	paket = ''
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		msg = '/install %s' % paket_name
		server_msg.send(msg.encode())
	else:
		print('Paket %s is already installed' % paket_name)


def upgrade_paket(paket_name, server_msg):
	update_installed_pakets()
	paket = ''
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		print('Paket %s is not installed' % paket_name)
	else:
		msg = '/upgrade %s' % paket
		server_msg.send(msg.encode())



def update_paket(paket_name, server_msg):
	update_installed_pakets()
	paket = ''
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		print('Paket %s is not installed' % paket_name)
	else:
		msg = '/update %s' % paket
		server_msg.send(msg.encode())

		answer = server_msg.recv(1023).decode('utf-8')
		print(answer)

		while 1:
			msg = input()
			server_msg.send(msg.encode())
			if msg == 'y':
				# TODO RECEIVE FILE
				break
			elif msg == 'n':
				break


def heartbeat(server_heartbeat):
	while 1:
		try:
			server_heartbeat.send(CONST_HEARTBEAT.encode())
		except Exception as e:
			# Not connected anymore
			server_heartbeat.close()
			break
		sleep(CONST_HEARTBEAT_RATE)
	os._exit(1)

# commandline input
target_host = sys.argv[1]
target_port = int(sys.argv[2])

# connect to server
socket_address = (target_host, target_port)

server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
server_msg.connect(socket_address)
server_msg.send('msg'.encode())

server_heartbeat = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
server_heartbeat.connect(socket_address)
server_heartbeat.send('heartbeat'.encode())

threading.Thread(target=heartbeat, args=(server_heartbeat,)).start()

try:
	while 1:
		# wait for command line input
		cmd_line_input = input()
		if cmd_line_input[:7] == '/update':
			paket_name = cmd_line_input[8:]
			update_paket(paket_name, server_msg)
		elif cmd_line_input[:8] == '/upgrade':
			paket_name = cmd_line_input[9:]
			upgrade_paket(paket_name, server_msg)
		elif cmd_line_input[:8] == '/install':
			paket_name = cmd_line_input[9:]
			install_paket(paket_name, server_msg)
		elif cmd_line_input == 'close':
			break
		else:
			server_msg.send(cmd_line_input.encode())
finally:
	# close connection
	server_msg.close()
	server_heartbeat.close()