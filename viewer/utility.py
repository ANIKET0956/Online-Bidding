
BYTES =  1024
key = 'abcdefgh12345678'
from pyDes import *


def encrypt_data(data):
	return triple_des(key).encrypt(data,padmode=2)

def decrypt_data(data):
	return triple_des(key).decrypt(data,padmode=2)

# Receive data in form of string
def data_receive(socket):
	# Get the length of data.
	length = int(socket.recv(1024).replace(" ",""))
	string = ''
	# Till the length of file =! zero.
	while length:
		if length < BYTES:
			string += socket.recv(length)
			length = 0
		else:
			string += socket.recv(BYTES)
			length -= BYTES
	string = decrypt_data(string)
	return string

def send_data(socket, data):
	# Send the length of data.
	data = encrypt_data(data)
	socket.send(str(len(data)).ljust(BYTES))
	start_ind = 0
	length = len(data)
	while length:
		if length < BYTES:
			socket.send(data[start_ind:start_ind+length])
			length = 0
		else :
			socket.send(data[start_ind:start_ind+BYTES])
			length -= BYTES



def dump_data(filename, data):
	f = open(filename,'wb')
	f.write(data)
	f.close()


def read_data(filename):
	f = open(filename,'rb')
	string = f.read()
	f.close()
	return string


def add_data_file(filename, data):
	f = open(filename,'rb')
	string  = f.read()
	f.close()
	f = open(filename,'wb')
	string = string +  data
	print string,'total string'
	f.write(string)
	f.close()
