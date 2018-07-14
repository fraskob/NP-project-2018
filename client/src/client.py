#!/usr/bin/env python3

import sys
import os
import socket
import threading
import glob

from time import sleep

CONST_HEARTBEAT_RATE = 5
CONST_HEARTBEAT = '/lifetime.reset()'

installed_pakets = []

def update_installed_pakets():
	os.chdir('./pakets')
	for paket in glob.glob('*'):
		installed_pakets.append(paket)
	os.chdir('../')


def install_paket(paket_name, sock):
	update_installed_pakets()
	paket = ''
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		msg = '/install %s' % paket_name
		sock.send(msg.encode())
	else:
		print('Paket %s is already installed' % paket_name)


def upgrade_paket(paket_name, sock):
	update_installed_pakets()
	paket = ''
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		print('Paket %s is not installed' % paket_name)
	else:
		msg = '/upgrade %s' % paket
		sock.send(msg.encode())



def update_paket(paket_name, sock):
	update_installed_pakets()
	paket = ''
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		print('Paket %s is not installed' % paket_name)
	else:
		msg = '/update %s' % paket
		sock.send(msg.encode())


def heartbeat(sock):
	while 1:
		try:
			sock.send(CONST_HEARTBEAT.encode())
		except Exception as e:
			# Not connected anymore
			sock.close()
			break
		sleep(CONST_HEARTBEAT_RATE)
	os._exit(1)

# commandline input
target_host = sys.argv[1]
target_port = int(sys.argv[2])

# connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
socket_address = (target_host, target_port)
sock.connect(socket_address)

threading.Thread(target=heartbeat, args=(sock,)).start()

try:
	while 1:
		# wait for command line input
		cmd_line_input = input()
		if cmd_line_input[:7] == '/update':
			paket_name = cmd_line_input[8:]
			update_paket(paket_name, sock)
		elif cmd_line_input[:8] == '/upgrade':
			paket_name = cmd_line_input[9:]
			upgrade_paket(paket_name, sock)
		elif cmd_line_input[:8] == '/install':
			paket_name = cmd_line_input[9:]
			install_paket(paket_name, sock)
		elif cmd_line_input == 'close':
			break
		else:
			sock.send(cmd_line_input.encode())
finally:
	# close connection
	sock.close()