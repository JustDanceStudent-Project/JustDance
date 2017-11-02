import threading
import os
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
ip_addr = '172.17.115.76'
port_num = 8080
portName = '/dev/ttyS0'
baudRate = 115200
winSize = 40
mlp_filepath = os.getcwd() + '/mlp/'
mlp_filename = 'mlpclf1.pk1'
cache_filename = 'anniyacache2.csv'
cache_filepath = os.getcwd() + '/cache/'
resultcache_filename = 'result.txt'
movecache_filename = 'MoveRaw.csv'
sensorData = []
arrMeasure = np.empty((3, 1),dtype=float)
result = None

newResultEvent = threading.Event()
newDataEvent = threading.Event()


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
        self.mlpclf = joblib.load(mlp_filepath + mlp_filename)
        print("MLP loaded")
        if(os.path.isfile(os.getcwd() + '/' + resultcache_filename)):
            os.remove(os.getcwd() + '/' + resultcache_filename)
            print('File {0} deleted'.format(os.getcwd() + '/' + resultcache_filename))
        self.daemon = True
        self.start()
      
    def run(self):
        global result
        global arrMeasure
        while(True):
            #print('Predictor check: {0}'.format(len(sensorData)))
            time.sleep(2)
            if(len(sensorData) > winSize * 1.5):
                arrInput = np.genfromtxt(sensorData[-winSize:],dtype='float',delimiter=',')
                arrMeasure = np.genfromtxt(sensorData[-1:],dtype='float',delimiter=',')
                arrMeasure = arrMeasure[-4:]
                print(arrMeasure)
                arrInput = np.delete(arrInput, np.s_[:3], axis=1)
                arrInput = np.delete(arrInput, np.s_[-4:], axis=1)
                print(arrInput.shape)
                arrInput = arrInput.flatten()
                arrInput = preprocessing.normalize(arrInput).reshape(1,-1)
                result = int(self.mlpclf.predict(arrInput))
                newResultEvent.set()
                print(time.ctime())
                print("Prediction: {0}".format(result))
                print("Writing to {0}".format(resultcache_filename))
                with open(resultcache_filename, 'a') as f:
                    f.write('{0}\n'.format(time.ctime()))
                    f.write('{0}\n'.format(result))

class client:
    def __init__(self, ip_addr, port_num):
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
        
        self.dataRcvTime = 2
        self.dataSendTime = 2
        

        self.datas = []
        
        thread = threading.Thread(target=self.generateData, args=())
        thread.daemon = True
        thread.start()
        print('Paused')

        
        i = 0
        time.sleep(10);
        while True:
            #print('newDataEvent check')
            time.sleep(self.dataSendTime)
            if newDataEvent.is_set():
                newDataEvent.clear()
                encrypted = self.auth.encryptText(self.datas[i], self.secret_key)
                self.sock.send(encrypted)
                    
                print(self.datas[i])
                i = i + 1            

    def generateData(self):
        global result
        global arrMeasure
        while True:
            #print('newResultEvent check')
            if newResultEvent.is_set():
                #print(result)
                action = actionStr(result)
                data = "#%s|%d|%d|%d|%d|" %(action, arrMeasure[0], arrMeasure[1], arrMeasure[2], arrMeasure[3])
                print("NEW DATA :: " + data)
                self.datas.append(data)
                newResultEvent.clear()
                newDataEvent.set()

            time.sleep(self.dataRcvTime)

class readData (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        '''
        port=serial.Serial(portName, baudRate)
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

        '''
        if(os.path.isfile(os.getcwd() + '/' + movecache_filename)):
            os.remove(os.getcwd() + '/' + movecache_filename)
            print('File {0} deleted'.format(os.getcwd() + '/' + movecache_filename))
        
        self.dataReadTime = 0.02
        self.daemon = True
        self.start()
        
    def run(self):
        global sensorData
        while (True):
            #port.write(HELLO)
            time.sleep(self.dataReadTime)
            #print('Reading Data')
            tempStr = b'0,1,2,3,4,5,6,7,8,9,10,11,12\n'
            #tempStr = bytearray()
            
            #readings = port.readline()
            '''
            if 'MPU' == readings:
                for j in range(13):
                    readings = port.readline()
                    readings = readings.replace("\r\n", "")
                    tempStr += b'{0}'.format(readings)
                    if j == 8 :
                        with open(movecache_filename, 'a') as f:
                            f.write((tempStr + b'\n').decode('utf-8'))
                    tempStr += b',' if j < 13 else b'\n'
            '''
            for j in range(13):
                a=1
                a=1
                a=1
                a=1

                
            sensorData.append(tempStr)
            with open(movecache_filename, 'a') as f:
                f.write((tempStr + b'\n').decode('utf-8'))
            


thread_readData = readData()
thread_processData = processData()
thread_client = client(ip_addr, port_num)


while True:
    pass
