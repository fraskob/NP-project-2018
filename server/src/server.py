#!/usr/bin/env python3

import socket
import sys
import threading


def listen_to_client(client, addr):
	try:
		while 1:
			msg = client.recv(1023).decode('utf-8')
			if msg != '':
				print(msg)
	finally:
		client.close()
		print("Server: %s has disconected" % client)

def client_handler(sock):
	while 1:
		# Accept connection request from client
		client, addr = sock.accept()
		print("Server: Connected with %s via port %d" % addr, flush=True)
		threading.Thread(target=listen_to_client, args=(client, addr)).start()

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
		threading.Thread(target=client_handler, args=(sock,)).start()
		# wait for command line input
		cmd_line_input = input()
		if cmd_line_input == 'close':
			break
finally:
	# close socket
	sock.close()