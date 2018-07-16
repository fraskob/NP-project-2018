#!/usr/bin/env python3

"""
client :host: :port:

A simple client script which can connect to a server by given host
and port. It is able to send Messages and download pakets and
corresponding updates from the server.
"""

import sys
import os
import socket
import threading
import glob

from time import sleep

# constants
CONST_HEARTBEAT_RATE = 5
CONST_HEARTBEAT = '/lifetime.reset()'
CONST_BUFFER = 4096

# list of all installed pakets
installed_pakets = []

def update_installed_pakets():
	"""
	Updates list of installed pakets.
	"""
	# Clear list
	global installed_pakets
	os.chdir('./pakets')
	# Iterate over all pakets in the paket directory of the client
	for paket in glob.glob('*'):
		# Add pakets to list
		installed_pakets.append(paket)
	os.chdir('../')


def install_paket(paket_name, server_msg):
	"""
	Requests a paket which is not installed on the client from the server,
	recveives it and installs it on the client. Does nothing if the paket
	is already installed.

	:type packet_name: string
	:param packet_name: Name of the paket to install

	:type server_msg: socket
	:param server_msg: Socket of server which provides the paket
	"""
	update_installed_pakets()
	paket = ''
	# Look if paket is already installed by iterating over installed pakets
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		# Paket is not installed

		# Request paket from server
		msg = '/install %s' % paket_name
		server_msg.send(msg.encode())

		# Receive response from server
		answer = server_msg.recv(CONST_BUFFER).decode('utf-8')
		print(answer)

		while 1:
			if answer == 'Paket %s does not exist.' % paket_name:
				# Server does not provide requested paket
				break

			# If server provides paket, decide if it should be installed
			msg = input()
			server_msg.send(msg.encode())
			if msg == 'y':
				# Install paket

				# Receive name full file name of the paket from server
				file_name = server_msg.recv(CONST_BUFFER).decode('utf-8')

				# Receive paket file
				answer = server_msg.recv(CONST_BUFFER).decode('utf-8')
				os.chdir('./pakets')
				# Remove all older versions of paket
				for file in glob.glob('%s*' % paket_name):
					os.remove(file)
				# Save received paket to paket directory (install)
				with open(file_name, 'w') as file:
					file.write(answer)
				os.chdir('../')
				break
			elif msg == 'n':
				# Do not install paket
				break


	else:
		# Paket is already installed
		print('Paket %s is already installed' % paket_name)


def upgrade_paket(paket_name, server_msg):
	"""
	Asks server if a newer version of the given paket is aviable. If the
	server provides a newer version it sends the latest upgrade of paket.
	This function does not update the loaded upgrade.

	:type paket_name: string
	:param paket_name: Name of paket to upgrade

	:type server_msg: socket
	:param server_msg: Socket of server which provides upgrade
	"""
	update_installed_pakets()
	paket = ''
	# Look if paket is already installed by iterating over installed pakets
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		# Paket is not installed

		print('Paket %s is not installed' % paket_name)
	else:
		# Paket is installed

		# Send upgrade request for given paket to server
		msg = '/upgrade %s' % paket
		server_msg.send(msg.encode())

		# Receiving response from server
		answer = server_msg.recv(CONST_BUFFER).decode('utf-8')
		print(answer)

		while 1:
			if answer == '%s is up-to-date' % paket_name:
				# Server does not provide any newer upgrade than currently installed
				break

			# Decide if aviable upgrade should be installed and send answer to server
			msg = input()
			server_msg.send(msg.encode())

			if msg == 'y':
				# Install latest upgrade

				# Receive full file name of upgrade from server
				file_name = server_msg.recv(CONST_BUFFER).decode('utf-8')

				# Receive upgrade file from server
				answer = server_msg.recv(CONST_BUFFER).decode('utf-8')
				
				os.chdir('./pakets')
				# Remove all old versions of paket
				for file in glob.glob('%s*' % paket_name):
					os.remove(file)

				# Save latest upgrade into paket directory (install)
				with open(file_name, 'w') as file:
					file.write(answer)
				os.chdir('../')
				break
			elif msg == 'n':
				# Do not install latest upgrade
				break


def update_paket(paket_name, server_msg):
	"""
	Asks server if a newer version of the given paket upgrade is aviable.
	If the server provides a newer version it sends the latest update of
	current paket upgrade. This function does only update the current
	upgrade.

	:type paket_name: string
	:param paket_name: Name of paket to update
	
	:type server_msg: socket
	:param server_msg: Socket of server which provides update
	"""
	update_installed_pakets()
	paket = ''
	# Look if given paket is installed by iterating over all paket files in paket
	# directory
	for pkt in installed_pakets:
		if pkt[:len(paket_name)] == paket_name:
			paket = pkt
	if paket == '':
		# Paket is not installed

		print('Paket %s is not installed' % paket_name)
	else:
		# Paket is installed

		# Send request for update to server
		msg = '/update %s' % paket
		server_msg.send(msg.encode())

		# Receive response from server
		answer = server_msg.recv(CONST_BUFFER).decode('utf-8')
		print(answer)

		while 1:
			if answer == '%s is up-to-date' % paket_name:
				# No update for given paket aviable on the server 
				break

			# Decide if aviable update should be installed and send answer to server
			msg = input()
			server_msg.send(msg.encode())

			if msg == 'y':
				# install latest update

				# Receive full file name of update from server
				file_name = server_msg.recv(CONST_BUFFER).decode('utf-8')

				# Receive update file from server
				answer = server_msg.recv(CONST_BUFFER).decode('utf-8')
				
				# Delete older pakets
				os.chdir('./pakets')
				for file in glob.glob('%s*' % paket_name):
					os.remove(file)

				# Save latest update in paket directory (install)
				with open(file_name, 'w') as file:
					file.write(answer)
				os.chdir('../')
				break
			elif msg == 'n':
				# Do not install latest update
				break


def heartbeat(server_heartbeat):
	"""
	Sends a heartbeat message to the server in regulary intervalls.

	:type server_heartbeat: socket
	:param server_heartbeat:Seperate socket to send heartbeat messages to server.
	"""
	while 1:
		try:
			# Send heartbeat to server
			server_heartbeat.send(CONST_HEARTBEAT.encode())
		except Exception as e:
			# Not connected anymore
			server_heartbeat.close()
			break
		sleep(CONST_HEARTBEAT_RATE)


# commandline parameters
target_host = sys.argv[1]
target_port = int(sys.argv[2])

# connect to server
socket_address = (target_host, target_port)

# Opens connection for messages
server_msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
server_msg.connect(socket_address)
server_msg.send('msg'.encode())

# Opens seperate connection for hearbeats only
server_heartbeat = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
server_heartbeat.connect(socket_address)
server_heartbeat.send('heartbeat'.encode())

# Starts hearbeat function in seperate thread
threading.Thread(target=heartbeat, args=(server_heartbeat,)).start()


try:
	while 1:
		# wait for command line input and parse over client functions
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
			# Close this client
			break
		else:
			# If the input is no command it will be send as normal message to the server
			server_msg.send(cmd_line_input.encode())
finally:
	# close connections
	server_msg.close()
	server_heartbeat.close()
	os._exit(1)