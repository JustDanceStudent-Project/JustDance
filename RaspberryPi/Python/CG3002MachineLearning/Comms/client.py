import socket
import client_auth
import time
import threading
import random

class client:
    def __init__(self, ip_addr, port_num):
        global action
        global action_set_time
        
        # init server
        self.auth = client_auth.client_auth()

        # creat socket 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to server
        self.sock.connect((ip_addr, port_num))

        self.actions = ['busdriver', 'frontback', 'jumping', 'jumpingjack', 'sidestep',
                'squatturnclap', 'turnclap', 'wavehands', 'windowcleaner360',
                'windowcleaning']
        action = None
        action_set_time = None
        # secret key
        self.secret_key = 'yaquan5156yaquan'
        
        self.dataRcvTime = 1
        self.dataSendTime = 2
        

        self.datas = []
        
        thread = threading.Thread(target=self.generateData, args=())
        thread.daemon = True
        thread.start()
        print('Paused')

        
        i = 0
        time.sleep(10);
        while True:
            time.sleep(self.dataSendTime)
            encrypted = self.auth.encryptText(self.datas[i], self.secret_key)
            self.sock.send(encrypted)
            print(self.datas[i])
            i = i + 1
            if(i == 20):
                break

    def generateData(self):
        while True:
            #action = random.choice(self.actions)
            data = "#%s|%d|%d|%d|%d|" %(action, 0, 1, 2, 3)
            print("NEW DATA :: " + data)
            self.datas.append(data)

            time.sleep(self.dataRcvTime)

#if len(sys.argv) != 3:
#    print('Invalid number of arguments')
#    print('python server.py [IP address] [Port]')
#    sys.exit()

#ip_addr = sys.argv[1]
#port_num = int(sys.argv[2])

#IP address = 'x.x.x.x'
#Port = 8888
'''
ip_addr = '127.0.0.1'
port_num = 8080

my_client = client(ip_addr,port_num)
'''