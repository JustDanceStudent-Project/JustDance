# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 16:18:26 2017

@author: avidr
"""
import numpy as np
import pandas as pd
from scipy import signal
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing

np.set_printoptions(threshold=np.nan)
windowSize = 100
overlap = 0.5
nNodes1 = 450
nNodes2 = 300

def segment_signal (data, window_size):
    # Segment m*n array into K*S*n given window size S
	N = data.shape[0]
	dim = data.shape[1]
	K = int(N/window_size)
	segments = np.empty((K, window_size, dim),dtype=float)
	for i in range(K):
		segment = data[i*window_size:i*window_size+window_size,:]
		segments[i] = np.vstack(segment)
	return segments

def segment_signal_sliding (data, window_size, overLap):
    # Segment m*n array into K*S*n given window size S with overlap
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
    # Flatten K*m*n nparray sensor input into K input vectors
    nWindows = data.shape[0]
    nSamples = data.shape[1]
    nFeatures = data.shape[2]
    segments = np.empty((nWindows,nSamples * nFeatures),dtype=float)
    for i in range(0, nWindows):
        segments[i] = data[i].flatten()
    return segments

def label(x):
    # List of datasets present in work folder
    return {
        0: "anniyastc", # Classifier can't reliably differentiate turn clap and squat turn clap
        1: "danastc",
                
        2: "YC_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        3: "Sneha_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        4: "Marini_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        
        5: "Anniya_Final_RAW",
        6: "BY_Final_RAW",
        7: "Dana_Final_RAW",
        
        8: "anniyatc",
        9: "bytc",
        10: "marinitc",
        11: "dawoodtc",
        
        12: "sneha_fb",
        13: "sneha_tc",
        14: "dana_tc",
        15: "yh_fb",
        16: "sneha_ss",        
        17: "yh_ss",        
        18: "sneha_win360",
        19: "anniya1_tc",
        #20: "yh_win", #confuses classifier
        20: "anniya1_fb",                
        21: "marini_jj",              
        21: "marini_ss",              
    }.get(x, "") 
    
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

finalListData = []
finalListTarget = []
for x in range(2,23):
    #consider moving datasets into separate folder
    print('Parsing {0}'.format(label(x)))
    ds1 = pd.read_excel(label(x)+'.xlsx', header=None, delim_whitespace=True)
    ds1.dropna(axis=0, how='any', inplace=True)
    ds1.columns = ["activity","body_yaw","body_pitch","body_roll","body_xAccel","body_yAccel","body_zAccel","hand_xAccel","hand_yAccel","hand_zAccel"]
    #print(ds1.shape)
    
    list_dataSet = []
    for y in range(1,12):
        #print("Parsing Activity {0} of {1}".format(y, label(x)))
        tempDf = pd.DataFrame(ds1[ds1.activity == y].as_matrix())
        tempDf = tempDf.iloc[100:-100]
        #print(tempDf.shape)
        list_dataSet.append(tempDf)
        
    list_dataSetInput = []
    list_target = []
    for y in range(1,12):
        #print("Sorting data and target for Activity {0} of {1}".format(y, label(x)))
        filtered_data = list_dataSet[y-1].iloc[:,4:10].as_matrix()
        #filtered_data = filter_data(list_dataSet[y-1].iloc[:,4:10].as_matrix())
        
        arrData = window_input(segment_signal_sliding(filtered_data, windowSize,overlap))
        list_dataSetInput.append(arrData)
        #print(list_dataSetInput[x-1].shape)
        list_target.append(np.full(arrData.shape[0], y))
    
    #print('Merging sorted activity data for {0}'.format(label(x)))
    arrayDataTmp = np.concatenate((list_dataSetInput[0],list_dataSetInput[1]),axis=0)
    arrayTargetTmp = np.concatenate((list_target[0],list_target[1]),axis=0)
    for y in range(2,len(list_target)):
        arrayDataTmp = np.concatenate((arrayDataTmp,list_dataSetInput[y]),axis=0)
        arrayTargetTmp = np.concatenate((arrayTargetTmp,list_target[y]),axis=0)
    finalListData.append(arrayDataTmp)
    finalListTarget.append(arrayTargetTmp)
    #print(arrayDataTmp.shape)
    #print(arrayTargetTmp.shape)
    
print('Merging parsed datasets')
arrayData = np.concatenate((finalListData[0],finalListData[1]),axis=0)
arrayTarget = np.concatenate((finalListTarget[0],finalListTarget[1]),axis=0)

for x in range(2,len(finalListData)):
    arrayData = np.concatenate((arrayData,finalListData[x]),axis=0)
    arrayTarget = np.concatenate((arrayTarget,finalListTarget[x]),axis=0)

#arrayData = preprocessing.scale(arrayData,axis=1)
'''
print(arrayData)
print(arrayTarget)
print(arrayData.shape)
print(arrayTarget.shape)

#print(arrayData.shape)
#print(arrayTarget.shape)
'''
kfold = KFold(n_splits=10, shuffle=True)
fold_index = 0
accuracyNN = []
for train, test in kfold.split(arrayData):
    print('Starting NN fold %i' %fold_index)
    mlpclf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(nNodes1,nNodes2,),random_state=1)
    mlpclf.fit(arrayData[train], arrayTarget[train])
    nn_predictions = mlpclf.predict(arrayData[test])
    accuracyNN.append(mlpclf.score(arrayData[test],arrayTarget[test]))
    cmNN = confusion_matrix(arrayTarget[test],nn_predictions)

    print('The classification accuracy for NN is %f' %accuracyNN[fold_index])
    print('And the confusion matrix is:')
    print(cmNN)
    print(cmNN.shape)
        
    fold_index += 1
