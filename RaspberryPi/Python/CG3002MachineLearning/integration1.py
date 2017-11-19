import threading
import os
import sys
import time
import serial
import client_auth
import socket
import re
import numpy as np
from scipy import stats
from scipy import signal
from sklearn import preprocessing
from sklearn.externals import joblib
import pickle

global bFlush

import warnings
warnings.filterwarnings('ignore')

bFlush = False
HELLO = b'\x02'
ACK = b'\x00'
ip_addr = '172.23.125.117'
#ip_addr = '172.17.112.1'
port_num = 8080
portName = '/dev/ttyAMA0'
baudRate = 115200
winSize = 100
homepath = '/home/pi/CG3002MachineLearning'
mlp_filepath = '/mlp'
mlp_filename = '/mlpclf5_1.pk1'
cache_filename = '/anniyacache2.csv'
cache_filepath = '/cache'
resultcache_filename = '/result.txt'
movecache_filename = '/MoveRaw.csv'
result = []
sensorData = []
arrMeasure = np.ones((4, 1),dtype=float)

def actionStr(x):
    # Returns activity string associated with integer
    return {
        1: "Neutral",
        2: "wavehands",
        3: "busdriver",
        4: "frontback",
        5: "sidestep",
        6: "windowcleaning",
        7: "windowcleaner360",
        8: "turnclap",
        9: "squatturnclap",
        10: "jumping",
        11: "jumpingjack",
        12: "logout",
        #13: "Time Out"
    }.get(x, "No Action")
    
def filter_data(data):
    # Takes in m * n nparray containing only sensor data and filters them, 1 sensor channel per column
    if data.size != 0 :
        list_filtered = []
        n = 15
        b = [1.0 / n] * n
        a = 1
        for x in range(data.shape[1]):
            yy = signal.lfilter(b,a,data[:,x:x+1])
            list_filtered.append(yy)
        data1 = np.concatenate(list_filtered, axis=1)
        return data1
    else:
        return data


class processData (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Loading MLP")
        #self.mlpclf = joblib.load(homepath + mlp_filepath + mlp_filename)
        with open(homepath + mlp_filepath + mlp_filename, 'rb') as f:
            self.mlpclf = pickle.load(f)
        print("MLP loaded")
        if(os.path.isfile(homepath + resultcache_filename)):
            os.remove(homepath + resultcache_filename)
            print('File {0} deleted'.format(homepath + resultcache_filename))
        self.daemon = True
        self.start()
      
    def run(self):
        global result
        global arrMeasure
        global sensorData
        global resultI
        global bFlush
        
        while(True):
            time.sleep(1)
           
            if(len(sensorData) >= winSize):
                arrInput = np.genfromtxt(sensorData[-100:],dtype='float',delimiter=',')
                arrMeasure = np.genfromtxt(sensorData[-1:],dtype='float',delimiter=',')
                sensorData = sensorData[-50:]
                if np.isnan(arrInput).any():
                    print('Array has NaN')
                    continue
                arrMeasure = arrMeasure[-4:]
                arrInput = np.delete(arrInput, np.s_[:3], axis=1)
                arrInput = np.delete(arrInput, np.s_[-4:], axis=1)
                '''
                if (time.monotonic() < t_end):
                    with open("data.csv","ab") as f:
                        np.savetxt(f,arrInput,delimiter=",")
                '''
                clfInput = arrInput.flatten()
                val = int(self.mlpclf.predict(clfInput))

                if val == 1:
                    sensorData = []
                    result = []
                    resultI = 0
                    bFlush = True
                    continue

                result.append(val)# if time.monotonic() < t_end else 13)
                print(time.ctime())
                print("Prediction: {0}".format(actionStr(result[len(result) - 1])))

class client(threading.Thread):
    def __init__(self, ip_addr, port_num):
        global bFlush
        threading.Thread.__init__(self)
        # init server
        
        self.auth = client_auth.client_auth()

        # creat socket 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to server
        self.sock.connect((ip_addr, port_num))

        self.actions = ['busdriver', 'frontback', 'jumping', 'jumpingjack', 'sidestep',
                'squatturnclap', 'turnclap', 'wavehands', 'windowcleaner360',
                'windowcleaning']
        # secret key
        self.secret_key = 'yaquan5156yaquan'
        
        self.dataRcvTime = 0.01
        self.dataSendTime = 0.01

        self.datas = []
        
        thread = threading.Thread(target=self.generateData, args=())
        thread.daemon = True
        thread.start()
        self.daemon  = True
        self.start()
        
    def run(self):
        global bFlush
        print('Paused')
        dataI = 0
        #time.sleep(10);
        while True:
            time.sleep(self.dataSendTime)
            if bFlush:
                self.datas = []
                dataI = 0
                bFlush = False
                
            if len(self.datas) - dataI > 0:
                encrypted = self.auth.encryptText(self.datas[dataI], self.secret_key)
                self.sock.send(encrypted)
                print(time.ctime())
                print(self.datas[dataI])
                dataI = len(self.datas)            

    def generateData(self):
        global result
        global arrMeasure
        global resultI
        resultI = 0
        count = 0
        while True:

            if len(result) - resultI > 9:
                agg = stats.mode(result[resultI:resultI+10],axis=None)
                action = actionStr(agg[0][0])
                #print(arrMeasure.shape)
                #if (count > 40): action = "logout"
                data = "#%s|%f|%f|%f|%f|" %(action, arrMeasure[0], arrMeasure[1], arrMeasure[2], arrMeasure[3])
                print(time.ctime())
                print("NEW DATA :: " + data)
                self.datas.append(data)
                #count = count + 1
                resultI = len(result)
            time.sleep(self.dataRcvTime)

thread_processData = processData()
thread_client = client(ip_addr, port_num)


#global port
dataReadTime = 0
port=serial.Serial(portName, baudRate)
initFlag = True
while(initFlag):
    print('Yo')
    port.write(HELLO)
    
    response = port.readline()
    
    if (len(response) > 0):
        initFlag = False
        port.write(ACK)
        print("Handshake is done")
        
    port.flushInput()
time.sleep(5)
t_end = time.monotonic() + 60 * 2
list_tempStr = []
while (True):
#while (time.monotonic()< t_end):
    time.sleep(dataReadTime)
    port.write(HELLO)
    tempStr = bytearray()

    readings = port.readline()
    if b'MPU:\r\n' == readings:
        tempStr = port.readline()
        tempStr = tempStr.replace(b"\r",b"")
        
        if re.match(b'((-?)\d{1,}\.\d{4}(,?)){13}\\n',tempStr) != None and len(tempStr.split(b',')) == 13:       
            sensorData.append(tempStr)
            #print(tempStr)

            #with open("data.csv","ab") as f:
                #f.write(tempStr)
