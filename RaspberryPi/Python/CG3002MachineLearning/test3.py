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
from sklearn import preprocessing

np.set_printoptions(threshold=np.nan)
windowSize = 120
overlap = 0.5

def segment_signal (data, window_size):
	N = data.shape[0]
	dim = data.shape[1]
	K = int(N/window_size)
	segments = np.empty((K, window_size, dim),dtype=float)
	for i in range(K):
		segment = data[i*window_size:i*window_size+window_size,:]
		segments[i] = np.vstack(segment)
	return segments

def segment_signal_sliding (data, window_size, overLap):
    N = data.shape[0]
    dim = data.shape[1]
    L = int(window_size * (1 - overLap))
    K = int((N - window_size) / L) + 1
    #print("{0} {1} {2} {3}".format(N, dim, L, K))
    segments = np.empty((K if K > 0 else 0, window_size, dim),dtype=float)
    for i in range(K):
        segment = data[i*L:i*L+window_size,:]
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

def label(x):
    return {
        0: "BingYouMoveMerged",
        1: "MariniMoveMerged",
        2: "YCMoveMerged",
    }.get(x, "")  

finalListData = []
finalListTarget = []
for x in range(0,3)    :
    ds1 = pd.read_excel(label(x)+'.xlsx', header=None, delim_whitespace=True)
    ds1.dropna(axis=0, how='any', inplace=True)
    ds1.columns = ["activity","body_yaw","body_pitch","body_roll","body_xAccel","body_yAccel","body_zAccel","hand_xAccel","hand_yAccel","hand_zAccel"]
    #print(ds1.shape)
    
    list_dataSet = []
    for x in range(1,12):
        tempDf = pd.DataFrame(ds1[ds1.activity == x].as_matrix())
        tempDf = tempDf.iloc[1000:6000]
        #print(tempDf.shape)
        list_dataSet.append(tempDf)
        
    list_dataSetInput = []
    list_target = []
    for x in range(1,12):
        arrData1 = window_input(segment_signal_sliding(list_dataSet[x-1].iloc[:,2:4].as_matrix(), windowSize,overlap))
        #print(arrData1.shape)
        arrData2 = window_input(segment_signal_sliding(list_dataSet[x-1].iloc[:,7:10].as_matrix(), windowSize,overlap))
        #print(arrData2.shape)
        arrData = np.concatenate((arrData1, arrData2),axis=1)
        list_dataSetInput.append(arrData)
        #print(list_dataSetInput[x-1].shape)
        list_target.append(np.full(arrData.shape[0], x))
        #print(list_target[x-1].shape)
        
    arrayDataTmp = np.concatenate((list_dataSetInput[0],list_dataSetInput[1]),axis=0)
    arrayTargetTmp = np.concatenate((list_target[0],list_target[1]),axis=0)
    for x in range(2,len(list_target)):
        arrayDataTmp = np.concatenate((arrayDataTmp,list_dataSetInput[x]),axis=0)
        arrayTargetTmp = np.concatenate((arrayTargetTmp,list_target[x]),axis=0)
    finalListData.append(arrayDataTmp)
    finalListTarget.append(arrayTargetTmp)
    #print(arrayDataTmp.shape)
    #print(arrayTargetTmp.shape)
    

arrayData = np.concatenate((finalListData[0],finalListData[1]),axis=0)
arrayTarget = np.concatenate((finalListTarget[0],finalListTarget[1]),axis=0)
for x in range(2,len(finalListData)):
    arrayData = np.concatenate((arrayData,finalListData[x]),axis=0)
    arrayTarget = np.concatenate((arrayTarget,finalListTarget[x]),axis=0)
arrayData = preprocessing.normalize(arrayData)

'''
print(arrayData)
print(arrayTarget)
print(arrayData.shape)
print(arrayTarget.shape)
'''

avgAcc = []
for nNodes in range(11,arrayData.shape[1]+1):
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
        
        with open('test_result3.txt', 'a') as f:
            f.write('For %i fold\n' %fold_index)
            f.write('The classification accuracy for NN is %f\n' %accuracyNN[fold_index])
            f.write('And the confusion matrix is:\n')
            f.write(np.array2string(cmNN))
            f.write('\n\n')
        
        print('The classification accuracy for NN is %f' %accuracyNN[fold_index])
        print('And the confusion matrix is:')
        print(cmNN)
        print(cmNN.shape)
        
        fold_index += 1
    avg = 0
    for x in range(0,len(accuracyNN)):
        avg += accuracyNN[x]
    print("Average accuracy for {0} nodes: {1}".format(nNodes,avg/len(accuracyNN)))
    with open('test_result3.txt','a') as f:
        f.write("Average accuracy for {0} nodes: {1}\n".format(nNodes,avg/len(accuracyNN)))
    avgAcc.append(avg/len(accuracyNN))

highest = avgAcc[0]
numNode = 11
for x in range(1,len(avgAcc)):
    numNode = (x + 11) if avgAcc[x] > highest else numNode
    highest = avgAcc[x] if avgAcc[x] > highest else highest
    
print("Highest average accuracy: {0}".format(highest))
print("with {0} number of nodes in first hidden layer".format(numNode))    
with open('test_result3.txt', 'a') as f:
    f.write("\nHighest average accuracy: {0}\n".format(highest))
    f.write("with {0} number of nodes in first hidden layer\n".format(numNode))

