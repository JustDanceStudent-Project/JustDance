import os
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing
from sklearn.externals import joblib

np.set_printoptions(threshold=np.nan)
windowSize = 100
overlap = 0.5
nNodes1 = 450
nNodes2 = 300
mlp_savepath = os.getcwd() + '/mlp/'


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
    # List of datasets present in work folder
    return {
        #0: "anniyastc", # Classifier can't reliably differentiate turn clap and squat turn clap
        #1: "danastc",
        
        #12: "anniya1_tc", #Bad data
        #16: "anniya1_fb",
        #18: "yh_ss", 

                
        0: "YC_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        1: "Sneha_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        2: "Marini_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        
        3: "Anniya_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        4: "BY_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        5: "Dana_Final_RAW", #Front Back, Side Step misclassification (Relevant actions removed)
        
        6: "anniyatc",
        7: "bytc",
        8: "marinitc",

        9: "dana_tc",
        10: "dawoodtc",
        11: "sneha_tc",
        
        12: "anniya!_fbss",
        13: "by!_fbss",
        14: "dana!_fbss",
        
        15: "sneha_fb",
        16: "yh_fb",
        
        17: "sneha_ss",
        18: "marini_ss",

        19: "dana_jj",                      
        20: "marini_jj",                      
        
        21: "sneha_win360",
        22: "marini_win360",
        
        23: "yh_win", 
        24: "marini_win", 
        25: "sneha_win", 
        
        26: "sneha_stc",
        27: "marini_stc",

        28: "dana_14",
        29: "sneha_finalmove",

        
    }.get(x, "")     
    
finalListData = []
finalListTarget = []
for x in range(0,3)    :
    print("Parsing {0}".format(label(x)))
    ds1 = pd.read_excel(label(x)+'.xlsx', header=None, delim_whitespace=True)
    ds1.dropna(axis=0, how='any', inplace=True)
    ds1.columns = ["activity","body_yaw","body_pitch","body_roll","body_xAccel","body_yAccel","body_zAccel","hand_xAccel","hand_yAccel","hand_zAccel"]
    #print(ds1.shape)

    list_dataSet = []
    for y in range(1,13):
        print("Parsing Activity {0} of {1}".format(y, label(x)))
        tempDf = pd.DataFrame(ds1[ds1.activity == y].as_matrix())
        tempDf = tempDf.iloc[100:-100]
        #print(tempDf.shape)
        list_dataSet.append(tempDf)

    list_dataSetInput = []
    list_target = []
    for y in range(1,13):
        print("Sorting data and target for Activity {0} of {1}".format(y, label(x)))
        arrData = window_input(segment_signal_sliding(list_dataSet[y-1].iloc[:,4:10].as_matrix(), windowSize,overlap))
        list_dataSetInput.append(arrData)
        #print(list_dataSetInput[x-1].shape)
        list_target.append(np.full(arrData.shape[0], y))
        #print(list_target[x-1].shape)

    print('Merging sorted activity data for {0}'.format(label(x)))
    arrayDataTmp = np.concatenate((list_dataSetInput[0],list_dataSetInput[1]),axis=0)
    arrayTargetTmp = np.concatenate((list_target[0],list_target[1]),axis=0)
    for y in range(2,len(list_target)):
        arrayDataTmp = np.concatenate((arrayDataTmp,list_dataSetInput[y]),axis=0)
        arrayTargetTmp = np.concatenate((arrayTargetTmp,list_target[y]),axis=0)
    finalListData.append(arrayDataTmp)
    finalListTarget.append(arrayTargetTmp)
    #print(arrayDataTmp.shape)
    #print(arrayTargetTmp.shape)

print("Merging parsed datasets")

arrayData = np.concatenate((finalListData[0],finalListData[1]),axis=0)
arrayTarget = np.concatenate((finalListTarget[0],finalListTarget[1]),axis=0)
for x in range(2,len(finalListData)):
    arrayData = np.concatenate((arrayData,finalListData[x]),axis=0)
    arrayTarget = np.concatenate((arrayTarget,finalListTarget[x]),axis=0)
#arrayData = preprocessing.scale(arrayData)

'''
arrayData = preprocessing.normalize(finalListData[0])
arrayTarget = finalListTarget[0]


print(arrayData)
print(arrayTarget)
print(arrayData.shape)
print(arrayTarget.shape)
'''
print("Creating MLPCLF")
mlpclf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(nNodes1,nNodes2,),random_state=1)
print("Training MLPCLF")
mlpclf.fit(arrayData, arrayTarget)
if not os.path.exists(mlp_savepath):
    os.makedirs(mlp_savepath)
    print('Folder "{0}" created\n'.format(mlp_savepath))
print("Saving MLPCLF")
joblib.dump(mlpclf, mlp_savepath + 'mlpclf3.pk1',protocol=0)
print("MLPCLF saved")
