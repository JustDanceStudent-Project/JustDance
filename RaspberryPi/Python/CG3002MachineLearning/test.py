# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 16:18:26 2017

@author: avidr
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier

np.set_printoptions(threshold=np.nan)
windowSize = 100

def segment_signal (data, window_size):
	N = data.shape[0]
	dim = data.shape[1]
	K = int(N/window_size)
	segments = np.empty((K, window_size, dim),dtype=float)
	for i in range(K):
		segment = data[i*window_size:i*window_size+window_size,:]
		segments[i] = np.vstack(segment)
	return segments

def window_input (data):
    # Data in K by m by n ndarray
    nWindows = data.shape[0]
    nSamples = data.shape[1]
    nFeatures = data.shape[2]
    segments = np.empty((nWindows,nSamples * nFeatures),dtype=float)
    for i in range(0, nWindows):
        segments[i] = data[i].flatten()
    return segments
    
dataSet = pd.read_excel('danadata.xlsx', header=None, delim_whitespace=True)
dataSet.dropna(axis=0, how='any', inplace=True)
dataSet.columns = ["activity","handx_accel","handy_accel","handz_accel","chestx_gyro","chesty_gyro","chestz_gyro"]

list_dataSet = []
for x in range(1,12):
    list_dataSet.append(dataSet[dataSet.activity == x])
    
list_dataSetInput = []
list_target = []
for x in range(1,12):
    arrData = window_input(segment_signal(list_dataSet[x-1].iloc[:,1:7].as_matrix(), windowSize))
    list_dataSetInput.append(arrData)
    #print(list_dataSetInput[x-1].shape)
    list_target.append(np.full(arrData.shape[0], x))
    #print(list_target[x-1].shape)
    
arrayData = np.concatenate((list_dataSetInput[0],list_dataSetInput[1]),axis=0)
arrayTarget = np.concatenate((list_target[0],list_target[1]),axis=0)
for x in range(2,11):
    arrayData = np.concatenate((arrayData,list_dataSetInput[x]),axis=0)
    arrayTarget = np.concatenate((arrayTarget,list_target[x]),axis=0)

'''
print(arrayData)
print(arrayTarget)
print(arrayData.shape)
print(arrayTarget.shape)
'''

avgAcc = []
for nNodes in range(11,601):
    print('Implementing {0} nodes'.format(nNodes))
    kfold = KFold(n_splits=10, shuffle=True)
    fold_index = 0
    accuracyNN = []
    for train, test in kfold.split(arrayData):
        print('Starting NN fold %i' %fold_index)
        mlpclf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(nNodes,),random_state=1)
        mlpclf.fit(arrayData[train], arrayTarget[train])
        nn_predictions = mlpclf.predict(arrayData[test])
        accuracyNN.append(mlpclf.score(arrayData[test],arrayTarget[test]))
        cmNN = confusion_matrix(arrayTarget[test],nn_predictions)
        
        '''
        with open('evaluation.txt', 'a') as f:
            f.write('For %i fold\n' %fold_index)
            f.write('The classification accuracy for NN is %f\n' %accuracyNN[fold_index])
            f.write('And the confusion matrix is:\n')
            f.write(np.array2string(cmNN))
            f.write('\n\n')
        '''
        '''
        print('The classification accuracy for NN is %f' %accuracyNN[fold_index])
        print('And the confusion matrix is:')
        print(cmNN)
        print(cmNN.shape)
        '''
        fold_index += 1
    avg = 0
    for x in range(0,len(accuracyNN)):
        avg += accuracyNN[x]
    print("Average accuracy for {0} nodes: {1}".format(nNodes,avg/len(accuracyNN)))
    with open('test_result.txt','a') as f:
        f.write("Average accuracy for {0} nodes: {1}\n".format(nNodes,avg/len(accuracyNN)))
    avgAcc.append(avg/len(accuracyNN))

highest = avgAcc[0]
numNode = 11
for x in range(1,len(avgAcc)):
    numNode = (x + 11) if avgAcc[x] > highest else numNode
    highest = avgAcc[x] if avgAcc[x] > highest else highest
    
print("Highest average accuracy: {0}".format(highest))
print("with {0} number of nodes in first hidden layer".format(numNode))    
with open('test_result.txt', 'a') as f:
    f.write("\nHighest average accuracy: {0}\n".format(highest))
    f.write("with {0} number of nodes in first hidden layer\n".format(numNode))
            