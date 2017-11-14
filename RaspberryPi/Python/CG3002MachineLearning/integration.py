import threading
import os
import sys
import time
import serial
import client_auth
import socket
import numpy as np
from scipy import signal
from sklearn import preprocessing
from sklearn.externals import joblib

import warnings
warnings.filterwarnings('ignore')

HELLO = b'\x02'
ACK = b'\x00'
ip_addr = '192.168.0.109'
port_num = 8080
portName = '/dev/ttyAMA0'
baudRate = 115200
winSize = 100
homepath = '/home/pi/CG3002MachineLearning'
mlp_filepath = '/mlp'
mlp_filename = '/mlpclf2.pk1'
cache_filename = '/anniyacache2.csv'
cache_filepath = '/cache'
resultcache_filename = '/result.txt'
movecache_filename = '/MoveRaw.csv'
result = []
sensorData = []
arrMeasure = np.ones((4, 1),dtype=float)


predictEvent = threading.Event()
newResultEvent = threading.Event()
newDataEvent = threading.Event()
sentEvent = threading.Event()


def actionStr(x):
    # Returns activity string associated with integer
    return {
        1: "Neutral",
        2: "Wave Hands",
        3: "Bus Driver",
        4: "Front & Back",
        5: "Side Step",
        6: "Window",
        7: "Window 360",
        8: "Turn & Clap",
        9: "Squat & Turn",
        10: "Jumping",
        11: "Jumping Jacks",
    }.get(x, "No Action")
    
def filter_data(data):
    # Takes in m * n nparray containing only sensor data and filters them, 1 sensor channel per column
    if data.size != 0 :
        list_filtered = []
        n = 15
        b = [1.0 / n] * n
        a = 1
        #print(data.shape)
        for x in range(data.shape[1]):
            #list_column.append(data[:,x:x+1])
            #print(data[:,x:x+1].reshape(-1).shape)
            yy = signal.lfilter(b,a,data[:,x:x+1])
            list_filtered.append(yy)
            #print(list_filtered[x].shape)
        data1 = np.concatenate(list_filtered, axis=1)
        #print(data1.shape)
        #print("Input size same as output size? {0}".format(True if data.shape == data1.shape else False))
        return data1
    else:
        return data


class processData (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Loading MLP")
        self.mlpclf = joblib.load(homepath + mlp_filepath + mlp_filename)
        print("MLP loaded")
        if(os.path.isfile(homepath + resultcache_filename)):
            os.remove(homepath + resultcache_filename)
            print('File {0} deleted'.format(homepath + resultcache_filename))
        #sentEvent.set()
        self.daemon = True
        self.start()
      
    def run(self):
        global result
        global arrMeasure
        global sensorData
        while(True):
            #print('Predictor check: {0}'.format(len(sensorData)))
            time.sleep(1)
            
            #if(len(sensorData) > winSize * 1.5 and sentEvent.is_set()):
            if(len(sensorData) >= winSize):
                #sentEvent.clear()
                #print(sensorData[-winSize:])
                arrInput = np.genfromtxt(sensorData[-100:],dtype='float',delimiter=',')
                arrMeasure = np.genfromtxt(sensorData[-1:],dtype='float',delimiter=',')
                sensorData = sensorData[-50:]
                #print(sensorData)
                #print(arrInput.shape)
                if np.isnan(arrInput).any():
                    print('Array has NaN')
                    continue
                #print(arrInput)
                #print(arrInput.shape)
                arrMeasure = arrMeasure[-4:]
                #print(arrMeasure.shape)
                arrInput = np.delete(arrInput, np.s_[:3], axis=1)
                arrInput = np.delete(arrInput, np.s_[-4:], axis=1)
                
                arrInput = arrInput.flatten()
                #arrInput = preprocessing.normalize(arrInput).reshape(1,-1)
                #print(arrInput)
                result.append(int(self.mlpclf.predict(arrInput)))
                #newResultEvent.set()
                #print(time.ctime())
                #print("Prediction: {0}".format(actionStr(result[len(result) - 1])))
                
                

class client(threading.Thread):
    def __init__(self, ip_addr, port_num):
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
        
        self.dataRcvTime = 1
        self.dataSendTime = 1
        

        self.datas = []
        
        thread = threading.Thread(target=self.generateData, args=())
        thread.daemon = True
        thread.start()
        self.daemon  = True
        self.start()
        
    def run(self):
        print('Paused')

            
        i = 0
        time.sleep(10);
        while True:
            #print('newDataEvent check')
            time.sleep(self.dataSendTime)
            if len(self.datas) - i > 0:
                #newDataEvent.clear()
                encrypted = self.auth.encryptText(self.datas[i], self.secret_key)
                self.sock.send(encrypted)
                #sentEvent.set()
                print(time.ctime())
                print(self.datas[i])
                i = len(self.datas)            

    def generateData(self):
        global result
        global arrMeasure
        i = 0
        while True:
            #print('newResultEvent check')
            if len(result) - i > 0:
                #print(result)
                action = actionStr(result[i])
                #print(arrMeasure.shape)
                data = "#%s|%f|%f|%f|%f|" %(action, arrMeasure[0], arrMeasure[1], arrMeasure[2], arrMeasure[3])
                #print(time.ctime())
                #print("NEW DATA :: " + data)
                self.datas.append(data)
                i = len(result)
                #newDataEvent.set()

            time.sleep(self.dataRcvTime)

thread_processData = processData()
thread_client = client(ip_addr, port_num)



dataReadTime = 0
port=serial.Serial(portName, baudRate)
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

list_tempStr = [] 
while (True):
    for x in range(2):
        #print(x)
        time.sleep(dataReadTime)
        port.write(HELLO)
        tempStr = bytearray()
               
        readings = port.readline()
        if b'MPU:\r\n' == readings:
            tempStr = port.readline()
            #print(tempStr)
            if len(tempStr.split(b',')) == 13:
                #print(tempStr)
                list_tempStr.append(tempStr)
                #print(tempStr)
                #print('String is ok')
    
    #print(len(list_tempStr))
    if len(list_tempStr) >= 2:
        arr_check = np.genfromtxt(list_tempStr[-2:],dtype='float',delimiter=',')
        
        bCheck = np.isnan(arr_check)
        #print(bCheck)
        if not bCheck.any():
            sensorData.append(list_tempStr[-2])
            sensorData.append(list_tempStr[-1])
            #print('1:{0}'.format(list_tempStr[-2]))
            #print('2:{0}'.format(list_tempStr[-1]))
        elif bCheck[0].any() and not bCheck[1].any():
            sensorData.append(list_tempStr[-1])
            #print('3:{0}'.format(list_tempStr[-1]))
        elif not bCheck[0].any() and bCheck[1].any():
            sensorData.append(list_tempStr [-2])
            #print('4:{0}'.format(list_tempStr[-2]))
        list_tempStr = []
        #port.flushOutput()
    
    
    
    #print('Generating dummy data')
    #sensorData.append(b'0,1,2,3,4,5,6,7,8,9,10,11,12\n')
    #print(time.ctime())
    #print(len(sensorData))
    #if(len(sensorData) >= winSize):
            #predictEvent.set()
        #print(tempStr.decode('utf-8'))
        