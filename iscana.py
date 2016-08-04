"""
"iscana" - programm for usage wireless mobile scanner "mustek iScanAir Go"

(c) 2016 Krylov D. V. 
jointr@rambler.ru

    "iscana" is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    "iscana" is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with "iscana".  If not, see <http://www.gnu.org/licenses/>.

1. power on scanner
2. connect by wifi to scanner
3. run programm ( python iscana )
4. after "i read: scanner ready" - click "scan" button
5. after "scanning please" - scan image
6. click "scan" button 
7. wait "image data ok, bye" - after 1-3 minute if not see "image data ok, bye" or "i read: previewend", please ctrl+c and repeat

"""


import socket
import time

HOST = '192.168.19.33'
PORT = 23

def debugD2( data1 ):
	print  "receive %s bytes from scanner"%( len(data1) )
	if len(data1) < 50:
		print data1
		for c1 in data1: print hex(ord(c1))

def GetJS( hbs1 ):
	prefixC = 0
	hs1 = ""
	for c1 in hbs1:
		prefixC += 1
		if prefixC < 9: continue
		if c1 == "\x00": break 
		hs1 = c1 + hs1
	return sum(ord(c) << (i * 8) for i, c in enumerate(hs1[::-1]))




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print "i connect to scanner on 192.168.19.33"
s.send('\x00\x60\x00\x50')
print "i send: hello scaner, how are you?"
time.sleep(1)
data = s.recv(1024)
s.close()
debugD2( data )

if data == '\x64\x65\x76\x62\x75\x73\x79\x00\x00\x00\x48':
	print "i read: scanner busy, program exit!"
	exit()

if data == '\x62\x61\x74\x74\x6c\x6f\x77\x00\x00\x00\x44':
	print "i read: scanner battery low, program exit!"
	exit()


if data == '\x73\x63\x61\x6e\x72\x65\x61\x64\x79\x00\x48': 
	print "i read: scanner ready"
else:
	print "i read: unknown answer, program exit"
	exit()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
data = s.recv(1024)
debugD2( data )

if data == '\x73\x63\x61\x6e\x67\x6f\x00\x00\x00\x00\x48':
	print "i read: scango"
	time.sleep( 1 )
	s.send( '\x40\x40\x30\x30' )
	print "i send: scanning please"


tmpF = None
jpegCounter = 0
jpegSize = 0

while True:
	data = s.recv(1024)
	if not data:
		break
	if not tmpF == None: jpegCounter += len( data )
	#print " =jpegCounter = %s " % jpegCounter  
	#debugD2(data)
	if data[:10] == '\x70\x72\x65\x76\x69\x65\x77\x65\x6e\x64':
		print "i read: previewend"
		time.sleep( 1 )
		s.send( '\x00\xd0\x00\xc0' )
		print "i send: give me jpegsize"
		continue
	if data[:8] == '\x6a\x70\x65\x67\x73\x69\x7a\x65':
		jpegSize = GetJS( data )
		print "i read: jpegsize = %s" % jpegSize
		time.sleep( 1 ) 
		s.send( '\x00\xf0\x00\xe0' )
		print "i send: give me image data"
		tmpF = open( "data.jpeg", 'wb' )
		continue
	if not tmpF == None: tmpF.write( data )
	if not tmpF == None:
		if jpegCounter == jpegSize: break

print "image data ok, bye"
s.close()
tmpF.close()