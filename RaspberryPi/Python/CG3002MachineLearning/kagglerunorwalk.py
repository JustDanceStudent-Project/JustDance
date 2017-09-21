# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 17:26:19 2017

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
data = pd.read_csv('dataset.csv')

dfData = data.iloc[:,5:8]
dfTarget = data.iloc[:, 4:5]

arrData = dfData.as_matrix()
arrTarget = np.reshape(dfTarget.as_matrix(), -1)

norm_Data = preprocessing.normalize(arrData)

'''
norm_DataTrain = norm_Data[100:]
norm_DataTest = norm_Data[:100]

arrTargetTrain = arrTarget[100:]
arrTargetTest = arrTarget[:100]
'''

'''
print(norm_Data.shape)
print(norm_Data)
print(norm_DataTrain.shape)
print(norm_DataTrain)
print(norm_DataTest.shape)
print(norm_DataTest)
print(arrTarget.shape)
print(arrTarget)
print(arrTargetTrain.shape)
print(arrTargetTrain)
print(arrTargetTest.shape)
print(arrTargetTest)
'''

'''
svm_model_linear = SVC(kernel='linear',C=1).fit(norm_DataTrain, arrTargetTrain)
print(svm_model_linear.predict(norm_DataTest))

mlpclf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5,2),random_state=1)
mlpclf.fit(norm_DataTrain, arrTargetTrain)
MLPClassifier(activation='relu', alpha=1e-05, batch_size='auto',
       beta_1=0.9, beta_2=0.999, early_stopping=False,
       epsilon=1e-08, hidden_layer_sizes=(5, 2), learning_rate='constant',
       learning_rate_init=0.001, max_iter=200, momentum=0.9,
       nesterovs_momentum=True, power_t=0.5, random_state=1, shuffle=True,
       solver='lbfgs', tol=0.0001, validation_fraction=0.1, verbose=False,
       warm_start=False)
print(mlpclf.predict(norm_DataTest))
'''

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
