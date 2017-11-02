# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 13:33:57 2017

@author: avidr
"""

import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
from scipy import signal
from sklearn import preprocessing

def label(x):
    # List of datasets present in work folder
    return {
        0: "Anniya_Final_RAW",
        1: "BY_Final_RAW",
        2: "Dana_Final_RAW",
        3: "Marini_Final_RAW",
        4: "Sneha_Final_RAW",
        5: "YC_Final_RAW",
    }.get(x, "") 
normalise = True

filename = label(1)

removeDataStart = False
dataStart = 100
removeDataEnd = True
dataEnd = -100

setAxis = True
rowStart = 1550
rowEnd= 1790
yMin = -200
yMax = 200

def label(x):
    return {
        1: "body_yaw",
        2: "body_pitch",
        3: "body_roll",
        4: "body_xAccel",
        5: "body_yAccel",
        6: "body_zAccel",
        7: "hand_xAccel",
        8: "hand_yAccel",
        9: "hand_zAccel",
    }.get(x, "")
    
def filter_data(data):
    # Takes in m * n nparray containing only sensor data and filters them, 1 sensor channel per column
    if data.size != 0 :
        list_filtered = []
        n = 1000
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

if (normalise):
    filepath = os.getcwd()+'/graph/'+filename+'_normalised'
else:
    filepath = os.getcwd()+'/graph/'+filename

if not os.path.exists(filepath):
    os.makedirs(filepath)
    print('Folder "{0}" created\n'.format(filepath))

dataSet = pd.read_excel(filename + '.xlsx', header=None, delim_whitespace=True)
dataSet.dropna(axis=0, how='any', inplace=True)
dataSet.columns = ["activity","body_yaw","body_pitch","body_roll","body_xAccel","body_yAccel","body_zAccel","hand_xAccel","hand_yAccel","hand_zAccel"]

list_dataSet = []
for x in range(1,12):
    tempDf = dataSet[dataSet.activity == x]
    if(removeDataStart): tempDf = tempDf.iloc[dataStart:]
    if(removeDataEnd): tempDf = tempDf.iloc[:dataEnd]
    if (normalise and not tempDf.empty):
        tempDf1 = tempDf.iloc[:,1:10]
        tempArr = tempDf1.as_matrix()
        tempDf1 = pd.DataFrame(preprocessing.scale(tempArr))
        frames = [pd.DataFrame(tempDf.iloc[:,0:1].as_matrix()),tempDf1]
        #print(tempDf.iloc[:,0:1].shape)
        #print(tempDf1.shape)
        tempDf = pd.concat(frames,axis=1)
    print(tempDf.shape)
    if (x == 11): print()
    list_dataSet.append(tempDf)
'''
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(list_dataSet[1])
print(list_dataSet[1].shape)
'''


for nActivity in range(1,12):
    for nSensor in range(1,10):
        if(list_dataSet[nActivity-1].empty): break
        print('Activity %d' %nActivity)
        print('{0}'.format(label(nSensor)))
        #print(list_dataSet[nActivity-1].iloc[:,nSensor:nSensor+1].as_matrix())
        plt.plot(list_dataSet[nActivity-1].iloc[:,nSensor:nSensor+1].as_matrix())
        if (setAxis):
            plt.xlim(rowStart, rowEnd)
            #plt.ylim(yMin, yMax)
        plt.ylabel('Activity {0} {1}'.format(nActivity,label(nSensor)))
        filereference = filepath + '/activity' + str(nActivity) + label(nSensor) + '.pdf'
        plt.savefig(filereference, bbox_inches='tight')
        plt.show()
