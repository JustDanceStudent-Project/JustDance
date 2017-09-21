# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 23:42:16 2017

@author: avidr
"""

import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier

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
data = pd.read_table('PAMAP2_Dataset/Protocol/subject101.dat',header=None,delim_whitespace=True)
'''
data2 = pd.read_table('PAMAP2_Dataset/Protocol/subject102.dat',header=None,delim_whitespace=True)
data3 = pd.read_table('PAMAP2_Dataset/Protocol/subject103.dat',header=None,delim_whitespace=True)
data4 = pd.read_table('PAMAP2_Dataset/Protocol/subject104.dat',header=None,delim_whitespace=True)
data5 = pd.read_table('PAMAP2_Dataset/Protocol/subject105.dat',header=None,delim_whitespace=True)
data6 = pd.read_table('PAMAP2_Dataset/Protocol/subject106.dat',header=None,delim_whitespace=True)
data7 = pd.read_table('PAMAP2_Dataset/Protocol/subject107.dat',header=None,delim_whitespace=True)
data8 = pd.read_table('PAMAP2_Dataset/Protocol/subject108.dat',header=None,delim_whitespace=True)
data9 = pd.read_table('PAMAP2_Dataset/Protocol/subject109.dat',header=None,delim_whitespace=True)
arr_data = [data1, data2, data3, data4, data5, data6, data7, data8, data9]
data = pd.concat(arr_data)
'''
data1 = data.iloc[:,1:2]
data2 = data.iloc[:,4:7]
data3 = data.iloc[:,21:24]
data4 = data.iloc[:,38:41]
arr_data = [data1, data2, data3, data4]
data = pd.concat(arr_data, axis=1)

data.columns = ["activity", 
                "handx_accel","handy_accel","handz_accel",
                "chestx_accel","chesty_accel","chestz_accel",
                "anklex_accel","ankley_accel","anklez_accel"]
data = data[data.activity != 0]
data.dropna(axis=0, how='any', inplace=True)
print('Data Processing From Dataset Done')

dfData = data.iloc[:,1:]
dfTarget = data.iloc[:,:1]

arrData = dfData.as_matrix()
arrTarget = np.reshape(dfTarget.as_matrix(), -1)

norm_Data = preprocessing.normalize(arrData)

print('Dataset Normalised')

kfold = KFold(n_splits=10, shuffle=True)
fold_index = 0
for train, test in kfold.split(norm_Data):
    print('Starting SVM fold %i' %fold_index)
    svm_model_linear = SVC(kernel = 'linear', C = 1).fit(norm_Data[train], arrTarget[train])
    svm_predictions = svm_model_linear.predict(norm_Data[test])
    accuracySVM = svm_model_linear.score(norm_Data[test],arrTarget[test])
    cmSVM = confusion_matrix(arrTarget[test],svm_predictions)
    
    print('Starting NN fold %i' %fold_index)
    mlpclf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(100,),random_state=1)
    mlpclf.fit(norm_Data[train], arrTarget[train])
    nn_predictions = mlpclf.predict(norm_Data[test])
    accuracyNN = mlpclf.score(norm_Data[test],arrTarget[test])
    cmNN = confusion_matrix(arrTarget[test],nn_predictions)
    
    print('In the %i fold,' %fold_index)
    print('The classification accuracy for SVM is %f' %accuracySVM)
    print('And the confusion matrix is:')
    print(cmSVM)
    print('The classification accuracy for NN is %f' %accuracyNN)
    print('And the confusion matrix is:')
    print(cmNN)
    fold_index += 1
