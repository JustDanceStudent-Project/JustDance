import threading
import os
import serial
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib

HELLO = b'\x02'
ACK = b'\x00'
winSize = 120
mlp_filepath = os.getcwd() + '/mlp/'
mlp_filename = 'mlpclf1.pk1'
cache_filename = 'anniyacache2.csv'
cache_filepath = os.getcwd() + '/cache/'
sensorData = []
threadLock = threading.Lock()

class processData (threading.Thread):
    def __init__(self, winSize, mlp_filepath, mlp_filename):
        threading.Thread.__init__(self)
        self.winSize = winSize
        print("Loading MLP")
        self.mlpclf = joblib.load(mlp_filepath + mlp_filename)
        print("MLP loaded")
        self.daemon = True
        self.start()
      
    def run(self):
        while(True):
            threadLock.acquire()
            #if(len(sensorData)>=winSize):
            with open(cache_filepath + cache_filename,'rb') as f:
                lines = f.readlines()
            if(winSize < len(lines)):
                arrInput = np.genfromtxt(lines[-(self.winSize):],delimiter=',')
                arrInput = arrInput.flatten()
                arrInput = preprocessing.normalize(arrInput).reshape(1,-1)
                result = int(self.mlpclf.predict(arrInput))
                with open('results.txt', 'a') as f:
                    f.write('{0}\n'.format(result))
            threadLock.release()
      
class readData (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.port = serial.Serial('/dev/ttyS0', 9600)
        #port.write(2)
        #response = port.readlines()
        #print (response)
        
        initFlag = True
        while(initFlag):
            #time.sleep(1)
            print('Yo')
            self.port.write(HELLO)
            
            response = self.port.readline()
            #print(len(response))
            
            if (len(response) > 0):
                initFlag = False
                self.port.write(ACK)
                print("Handshake is done")
                
            self.port.flushInput()

    def run(self):
        while (True):
            threadLock.acquire()
            self.port.write(HELLO)
            readings = self.port.readline()
            if 'MPU' in readings:
                sensorData.append('MPU:')
                for j in range(10):
                    readings = self.port.readline()
                    readings = readings.replace("\r\n", "")
                    sensorData.append(readings)
            threadLock.release()

#thread_readData = readData()          
thread_processData = processData(winSize, mlp_filepath, mlp_filename)

#thread_readData.start()
#thread_processData.start()