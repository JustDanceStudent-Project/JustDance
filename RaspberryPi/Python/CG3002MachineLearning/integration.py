import threading
import os
import serial
import time
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib

import warnings
warnings.filterwarnings('ignore')

HELLO = b'\x02'
ACK = b'\x00'
baudrate = 9600
winSize = 120
mlp_filepath = os.getcwd() + '/mlp/'
mlp_filename = 'mlpclf1.pk1'
cache_filename = 'anniyacache2.csv'
cache_filepath = os.getcwd() + '/cache/'
resultcache_filename = 'result.txt'
sensorData = []
threadLock = threading.Lock()

class processData (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Loading MLP")
        self.mlpclf = joblib.load(mlp_filepath + mlp_filename)
        print("MLP loaded")
        if(os.path.isfile(os.getcwd() + '/' + resultcache_filename)):
            os.remove(os.getcwd() + '/' + resultcache_filename)
            print('File {0} deleted'.format(os.getcwd() + '/' + resultcache_filename))
        self.daemon = True
        self.start()
      
    def run(self):
        while(True):
            threadLock.acquire()
            #if(len(sensorData)>=winSize):
            if(winSize < len(sensorData)):
                arrInput = np.genfromtxt(sensorData[-winSize:],delimiter=',')
                arrInput = arrInput.flatten()
                arrInput = preprocessing.normalize(arrInput).reshape(1,-1)
                result = int(self.mlpclf.predict(arrInput))
                print("Writing to {0}".format(resultcache_filename))
                with open(resultcache_filename, 'a') as f:
                    f.write('{0}\n'.format(result))
            threadLock.release()
            time.sleep(2)
      
class readData (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.port = serial.Serial('/dev/ttyS0', baudrate)
        
        initFlag = True
        while(initFlag):
            #time.sleep(1)
            print('Yo')
            #self.port.write(HELLO)
            
            #response = self.port.readline()
            response = HELLO
            #print(len(response))
            
            if (len(response) > 0):
                initFlag = False
                #self.port.write(ACK)
                print("Handshake is done")
                
            #self.port.flushInput()
            
        self.daemon = True
        self.start()

    def run(self):
        while (True):
            threadLock.acquire()
            
            self.port.write(HELLO)
            readings = self.port.readline()
            data = []
            if 'MPU' in readings:
                data.append('MPU:')
                for j in range(10):
                    readings = self.port.readline()
                    readings = readings.replace("\r\n", "")
                    data.append(readings)
            sensorData.append(data)
            print("Reading Data")
            threadLock.release()
            time.sleep(0.02)

thread_readData = readData()          
thread_processData = processData()

while True:
    pass