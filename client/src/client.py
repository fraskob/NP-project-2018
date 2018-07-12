#!/usr/bin/env python3

import sys
import socket
import threading

from time import sleep

CONST_HEARTBEAT_RATE = 5
CONST_HEARTBEAT = '/lifetime.reset()'

def heartbeat(sock):
	while 1:
		sock.send(CONST_HEARTBEAT.encode())
		sleep(CONST_HEARTBEAT_RATE)
		print('hearbeat')

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
		if cmd_line_input == 'close':
			break
		else:
			sock.send(cmd_line_input.encode())
finally:
	# close connection
	sock.close()