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
        1: "handx_accel",
        2: "handy_accel",
        3: "handz_accel",
        4: "chestx_gyro",
        5: "chesty_gyro",
        6: "chestz_gyro",
    }.get(x, "")  

dataSet = pd.read_excel('danadata.xlsx', header=None, delim_whitespace=True)
dataSet.dropna(axis=0, how='any', inplace=True)
dataSet.columns = ["activity","handx_accel","handy_accel","handz_accel","chestx_gyro","chesty_gyro","chestz_gyro"]

list_dataSet = []
for x in range(1,12):
    list_dataSet.append(dataSet[dataSet.activity == x])
'''
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(list_dataSet[1])
print(list_dataSet[1].shape)
'''
for nActivity in range(1,12):
    for nSensor in range(1,2):
        rowStart = 400
        rowEnd= 700
        yMin = -150
        yMax = 150
        print('Activity %d' %nActivity)
        print('{0}'.format(label(nSensor)))
        #print(list_dataSet[nActivity-1].iloc[:,nSensor:nSensor+1].as_matrix())
        plt.plot(list_dataSet[nActivity-1].iloc[:,nSensor:nSensor+1].as_matrix())
        plt.axis([rowStart,rowEnd,yMin, yMax])

        plt.ylabel('Activity {0} {1}'.format(nActivity,label(nSensor)))
        plt.show()
