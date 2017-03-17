import socket                   # Import socket module
import datetime

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto import Random
import cPickle
import utility


document_stime = datetime.datetime(2017,3,17,18,25)
document_etime = datetime.datetime(2017,3,17,18,30)

standard_time = datetime.datetime(1970,1,1)

s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
port = 8888                   # Reserve a port fo
BYTES = 1024
s.connect((host, port))

filename = 'tender_doc.txt'
auth = 'authority.txt'

private_key_doc = RSA.generate(1024)   # Random generator.
public_key_doc  = private_key_doc.publickey()


string  = private_key_doc.exportKey()
public_key_doc = cPickle.dumps(public_key_doc)

def give_document_inform(socket, filename, timespan, public_key_doc):
	# Send opcode to server.
	socket.send("0".ljust(BYTES))
	# Send document name with padding.
	socket.send(filename.ljust(BYTES))
	# Send timespan.
	socket.send(timespan.ljust(BYTES))
	# Send public key.
	utility.send_data(socket,public_key_doc)


t1 = str((document_stime-standard_time).total_seconds())
t2 = str((document_etime-standard_time).total_seconds())


utility.dump_data(auth,string)
give_document_inform(s,filename,t1+'\t'+t2,public_key_doc)


print('Done sending')
s.close()