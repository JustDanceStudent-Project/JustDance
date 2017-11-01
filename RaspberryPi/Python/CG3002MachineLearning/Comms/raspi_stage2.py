import serial
import sys
import string
import json
import time

HELLO = b'\x02'
ACK = b'\x00'

port=serial.Serial('/dev/ttyS0', 9600)
#port.write(2)
#response = port.readlines()
#print (response)

initFlag = True
while(initFlag):
    #time.sleep(1)
    print('Yo')
    port.write(HELLO)
    
    response = port.readline()
    #print(len(response))
    
    if (len(response) > 0):
        initFlag = False
        port.write(ACK)
        print("Handshake is done")
        
    port.flushInput()

sensorData = []
     
while (True):
    port.write(HELLO)
    
    for i in range(30):
        data = []
        readings = port.readline()
        if 'MPU' in readings:
            data.append('MPU:')
            for j in range(10):
                readings = port.readline()
                readings = readings.replace("\r\n", "")
                data.append(readings)
            print (data)
    
            
        sensorData.append(data)
