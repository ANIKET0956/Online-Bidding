

import socket                   # Import socket module
import datetime

PORT = 20000
REQUEST_QUEUE_SIZE = 10
BYTES = 1024

# Start the time server
ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostname()
ssocket.bind((HOST,PORT))
ssocket.listen(REQUEST_QUEUE_SIZE)

print 'running on PORT',PORT


def handle_request(socket):
	total_second  = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()
	socket.send(str(total_second).ljust(BYTES))

while True:
	(csocket,addr) = ssocket.accept()
	handle_request(csocket)
	csocket.close()

			

