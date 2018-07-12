#!/usr/bin/env python3

import sys
import socket

# commandline input
target_host = sys.argv[1]
target_port = int(sys.argv[2])

# connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
socket_address = (target_host, target_port)
sock.connect(socket_address)

try:
	while 1:
		# wait for input
		cmd_line_input = input()
		if cmd_line_input == 'close':
			break
finally:
	# close connection
	sock.close()