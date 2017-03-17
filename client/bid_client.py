import socket,time
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto import Random
from fpdf import FPDF
import cPickle
import utility

#reading user input
print "\n\n\n\n\n\n"
print "			Welcome to Online Bidding "
print "			------------------------- "
print "\n\n\n"
print "Plaese enter your name :",
name=raw_input()
print "Please enter your bid(in Rupees) :",
bid=raw_input()

#downloading reciept of bid
class PDF(FPDF):
    def header(self):
        self.image('logo.jpg', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Tender Doc', 1, 0, 'C')
        self.ln(20)
pdf = PDF()
pdf.add_page()
pdf.set_font('Times', '', 12)
pdf.cell(0, 10, 'Name   :' + name, 0, 1)
pdf.cell(0, 10, 'Bid   :' + bid, 0, 1)
file_name_download='ebid'+name+'.pdf'
pdf.output(file_name_download, 'F')

#creating txt file content
file_name='bid'+name+'.txt'
data='Name '+name+' Bid '+bid
open(file_name, 'wb').write(data)
print name
print bid

#getting authorised group public key
s = socket.socket()     
host = socket.gethostname()
port = 8888
s.connect((host, port))
op_code=str(1)
op_code.ljust(1024)
s.send(op_code)
permit_data = int(s.recv(1024).replace(' ',''))
if not(permit_data):
    print 'Time up for bidding'
    s.close()
    exit(0)
temp= utility.data_receive(s)

print 'temp' , temp


authorised_publickey=cPickle.loads(temp)

#encrypting txt file
file_to_encrypt = open(file_name, 'rb').read()
to_join = []
step = 0
while 1:
    # Read 128 characters at a time.
    s1 = file_to_encrypt[step*128:(step+1)*128]
    if not s1: break
    to_join.append(authorised_publickey.encrypt(s1,0)[0])
    step += 1
encrypted = ''.join(to_join)

# Write the encrypted file.
open('encrypted_file.txt', 'wb').write(encrypted)
tt=open("encrypted_file.txt").read()

#craeting signature
h1=SHA512.new(tt).hexdigest()
my_key = RSA.generate(1024)
signature=my_key.sign(h1,'')[0]

# #sending op code 2
# op_code=str(2)
# op_code.ljust(1024)
# s.send(op_code)

#sending public my_key
to_send=cPickle.dumps(my_key.publickey())
utility.send_data(s,to_send)

#sending signature
utility.send_data(s,str(signature))

#sending encrypted message
utility.send_data(s,tt)

s.close()
