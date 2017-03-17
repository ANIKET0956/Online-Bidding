# WebServer Functions
# 

import socket
import time
import os
import utility
import cPickle

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto import Random


PORT = 8888
REQUEST_QUEUE_SIZE = 5
BYTES = 1024

filedetail = dict()

#	Defining OpCode for each operation on server.
#	Code 				Instruction
#	 0  				Authorised persons send server the document details
#    1					Client tries to access the document public key
#    2 					Client send encrypted bid document to server
#    3 					Authorised persons can download the file from server
#   ---------------------------------------------


common_filename = 'enc_doc.txt'
filename = 'tender_doc.txt'


f = open(common_filename,'wb')
f.write('')
f.close()

# Receive file from server.
def file_receive(socket, name):
	# Open the file to write.
    f = open(name,'wb')
    while True:
    	print('recieving data ....')
    	# Receive data in 1024 size buffer.
    	data = socket.recv(1024)
    	if not data:
    		break
    	# Write data to a file.
    	f.write(data)
    f.close()

# Send file from server.
def file_send(socket, name):
	# Open file to read.
	f = open(name,'rb')
	# Read total data from file.
	data = f.read()
	# Send using utility function.
	utility.send_data(socket,data)


# Receive document information from authorised persons.
def document_store_inform(socket):
	global filedetail
	# Get the filename.
	filename = socket.recv(1024).replace(" ","")
	# Get start and end time separated by tab.
	(t1,t2) = [ x.replace(" ","") for x in socket.recv(1024).split('\t') ]
	# Public key of document.
	public_key_doc = utility.data_receive(socket)
	# Add detail to database.
	data = t1 + '\t' + t2 + '\t' + public_key_doc
	# Dump this in server file.
	utility.dump_data(filename,data)


# Send public key to client which want to bid for document.
def document_send_inform(socket, filename):
	# Get the document public key.
	public_key_doc = utility.read_data(filename).split('\t')[2]
	print public_key_doc,'public'
	# Send the key to client side.
	utility.send_data(socket,public_key_doc)


def verify_and_store(client_socket):
	# Receive public key.
	public_key_dsa_dump = utility.data_receive(client_socket)
	# Load the dump data.
	public_key_dsa = cPickle.loads(public_key_dsa_dump)
	# Receive digital signature.
	signature = utility.data_receive(client_socket)
	# Receive enc data.
	enc_data = utility.data_receive(client_socket)
	# Calculate hash function.
	hash_data = SHA512.new(enc_data).hexdigest()
	# Verify the message.
	validity  = public_key_dsa.verify(hash_data,(long(signature),))
	print validity, 'VALID'
	if validity == True:
		utility.add_data_file(common_filename,enc_data)
	else:
		print 'Wrong Message attack !!!'


def query_timeserver(time, op):
	times = socket.socket()
	timehost = socket.gethostname()
	timeport = 20000
	times.connect((timehost,timeport))
	timedata = float(times.recv(BYTES))
	print timedata,'timedata'
	if not(op):				# When client wants to bid.
		if timedata < time:
			return True
		else:
			return False
	elif op:		    # When authority wants to view.
		if timedata > time:
			return True
		else:
			return False
	times.close()


def handle_request(client_socket):
	# Get opcode on first message instruction
	opcode = client_socket.recv(1024)
	opcode = opcode.replace(" ","")
	print opcode
	if   opcode == "0":      # Get doc information.
		document_store_inform(client_socket)
	elif opcode == "1":	  
		# Check if message obtained before time t1
		read_fdata = utility.read_data(filename).split('\t')
		deadline  = float(read_fdata[0])
		print deadline,'Deadline'
		permit = query_timeserver(deadline,0)
		if permit:    
		    # Get public key.
		    client_socket.send("1".ljust(BYTES))
		    document_send_inform(client_socket, filename)
		    print 'done here document information send'
		    verify_and_store(client_socket)
		else:
			client_socket.send("0".ljust(BYTES))
			print 'Time expired for bidding'
	elif opcode == "3":
		# Check if time is already t2 or not.
		read_fdata = utility.read_data(filename).split('\t')
		start_time = float(read_fdata[1])
		print start_time,'start time'
		permit  = query_timeserver(start_time,1)
		print permit
		if permit:
			# Sending ACK.
			client_socket.send("1".ljust(BYTES))
			file_send(client_socket,common_filename)
		else:
			# Sending ACK.
			client_socket.send("0".ljust(BYTES))
			print 'Wait for some time to view document'


def serve_start():
	# Creating socket on server side.
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Getting hostname from local machine.
	HOST = socket.gethostname()
	# Binding server to (hostname,port).
	server_socket.bind((HOST,PORT))
	# Number of connections to keep.
	server_socket.listen(REQUEST_QUEUE_SIZE)
	print('Serving HTTP on port {port} ...'.format(port=PORT))

	# Main Loop.
	while True:
		# Check for incoming requests and create client socket.
		(client_socket, address) = server_socket.accept()
		# Call fork.
		pid = os.fork()
		if pid==0:  # Child Process.
			# Close the duplicate server socket in child process.
			server_socket.close()
			# Perform operation on client socket.
			handle_request(client_socket)
			# Close client socket after operation.
			client_socket.close()
			# Terminate the process.
			os._exit(0)
		else :      # Parent Process.
			# Close client socket in parent and loop over.
			client_socket.close()   



if __name__ == '__main__':
    serve_start()
