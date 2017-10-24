# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 13:33:57 2017

@author: avidr
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

dataSet = pd.read_excel('BingYouMoveMerged.xlsx', header=None, delim_whitespace=True)
dataSet.dropna(axis=0, how='any', inplace=True)
dataSet.columns = ["activity","body_yaw","body_pitch","body_roll","body_xAccel","body_yAccel","body_zAccel","hand_xAccel","hand_yAccel","hand_zAccel"]

list_dataSet = []
for x in range(1,12):
    list_dataSet.append(dataSet[dataSet.activity == x])
'''
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(list_dataSet[1])
print(list_dataSet[1].shape)
'''
rowStart = 500
rowEnd= 5500
yMin = -200
yMax = 200
        
for nActivity in range(1,12):
    for nSensor in range(1,10):
        print('Activity %d' %nActivity)
        print('{0}'.format(label(nSensor)))
        #print(list_dataSet[nActivity-1].iloc[:,nSensor:nSensor+1].as_matrix())
        plt.plot(list_dataSet[nActivity-1].iloc[:,nSensor:nSensor+1].as_matrix())
        plt.xlim(rowStart, rowEnd)
        #plt.ylim(yMin, yMax)

        plt.ylabel('Activity {0} {1}'.format(nActivity,label(nSensor)))
        plt.show()
