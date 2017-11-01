import serial
import sys
import string
import json

HELLO = b"\x02"
ACK = b"\x00"

port=serial.Serial('/dev/ttyS0',9600)

flag = True
while(flag):
    #time.sleep(1)
    print('Yo')
    port.write(HELLO)
    
    response = int(port.readline())

    if (response == 0):
        flag = False
        port.write(ACK)
        print("Handshake is done")

while (True):
    readings = str(port.readline())
    print (ord(readings[0])
        

