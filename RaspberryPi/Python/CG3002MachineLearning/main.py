# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 17:26:19 2017

@author: avidr
"""
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.datasets import load_iris

def segment_signal(data, window_size):
    N = data.shape[0]
    dim = data.shape[1]
    K = N/window_size
    segments = np.empty((K, window_size, dim))
    for i in range(K):
        segment = data[i*window_size:i*window_size+window_size,:]
        segments[i] = np.vstack(segment)
    return segments

#load dataset
data = pd.read_csv('dataset.csv')
#print(data.iloc[:,4:])
#print(data.iat[0,10])
'''
dataRun = data[data.activity == 1]

dataWalk = data[data.activity == 0]
dfWalkData = dataWalk.iloc[:,5:]
dfWalkTarget = dataWalk.iloc[:,4:5]

arrWalkData = dfWalkData.as_matrix()
arrWalkTarget = dfWalkTarget.as_matrix()
        
norm_WalkData = preprocessing.normalize(arrWalkData)

norm_WalkDataTrain = norm_WalkData[100:]
norm_WalkDataTest = norm_WalkData[:99]

arrWalkTargetTrain = np.reshape(arrWalkTarget[100:], -1)
arrWalkTargetTest = np.reshape(arrWalkTarget[:99], -1)

print(len(norm_WalkData[0]))
print(len(arrWalkTargetTrain))
print(arrWalkTargetTest)
'''

dfData = data.iloc[:,5:]
dfTarget = data.iloc[:, 4:5]

arrData = dfData.as_matrix()
arrTarget = dfData.as_matrix()

norm_Data = preprocessing.normalize(arrData)

norm_DataTrain = norm_Data[100:]
norm_DataTest = norm_Data[:99]

arrTargetTrain = np.reshape(arrTarget[100:], -1)
arrTargetTest = np.reshape(arrTarget[:99], -1)

svm_model_linear = SVC(kernel='linear',C=1).fit(norm_DataTrain, arrTargetTrain)
'''
iris = load_iris()
y=iris.target
print(y)
x = iris.data
print(x)
'''