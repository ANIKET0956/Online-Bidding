
import socket                   # Import socket module

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto import Random
import cPickle
import utility


s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
port = 8888                   # Reserve a port fo
BYTES = 1024
s.connect((host, port))
OFFSET = 128

filename = 'tender_doc.txt'
auth = '../auth/authority.txt'

def receive_bid_server(socket, filename):
	# Send opcode to server.
	socket.send("3".ljust(BYTES))
	# Check permit paramter.
	permit_data = int(socket.recv(BYTES).replace(" ",""))
	if permit_data:	
		# Receive file from server in string.
		string = utility.data_receive(socket)
		str_arr = []
		start_in = 0
		length = len(string)
		while length:
			str_arr.append(string[start_in:start_in+OFFSET])
			length -= OFFSET
			start_in += OFFSET
		# Read private key.
		private_key_doc = utility.read_data(auth)
		private_key_doc = RSA.importKey(private_key_doc)
		print str_arr,' FIRST'
		print len(str_arr)
		# Decrypt the string using key.
		dec_arr = [  private_key_doc.decrypt(x) for x in str_arr ] 
		print dec_arr, 'SECOND'
		decrypt = ''
		for x in dec_arr:
			decrypt += x + '\n'
		print decrypt
		filepdf = filename + '.txt'
		f = open(filepdf, 'wb')
		# Write decypt string in pdf file/
		f.write(decrypt)
		f.close() 
	else:
		print 'Not suitable time for downloading, Wait !!!'	

receive_bid_server(s,'result')
s.close()