import serial
import sys
import string
import time

HELLO = b'\x02'
ACK = b'\x00'

port=serial.Serial('/dev/ttyAMA0', 115200)
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

#sensorData = []
     
while (True):
    #time.sleep(0.02)
    port.write(HELLO)
    
    data = []
    readings = port.readline()
    
    if 'MPU' in readings:
        
        readings = port.readline()
        readings = readings.replace("\r\n", "")
        data.append(readings)
            
        size = len(data)
        print("\r\n")
        if not('MPU') in data:
            print(data)
                

    data = []


