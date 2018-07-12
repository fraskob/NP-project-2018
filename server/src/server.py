#!/usr/bin/env python3

import socket
import sys
import threading

def listen_to_commands(sock):
	try:
		while 1:
			# wait for command line input
			cmd_line_input = input()
			if cmd_line_input == 'close':
				break
	finally:
		sock.close()

def listen_to_client(client, addr):
	try:
		while 1:
			msg = client.recv(1023).decode('utf-8')
			if msg != '':
				print(msg)
	finally:
		client.close()
		print("Server: %s has disconected" % client)

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
		threading.Thread(target=listen_to_commands, args=(sock,)).start()

		# Accept connection request from client
		client, addr = sock.accept()
		print("Server: Connected with %s via port %d" % addr, flush=True)
		threading.Thread(target=listen_to_client, args=(client, addr)).start()

		
finally:
	# close socket
	sock.close()