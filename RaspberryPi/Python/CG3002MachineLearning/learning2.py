import numpy as np 
import pandas as pd 
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier

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

def segment_signal_sliding (data, window_size, overlap):
    N = data.shape[0]
    dim = data.shape[1]
    L = int(window_size * (1 - overlap))
    K = int((N - window_size) / L) + 1
    segments = np.empty((K, window_size, dim),dtype=float)
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
    
dataSet = pd.read_excel('P1Data.xlsx', header=None, delim_whitespace=True)

'''
readings = dataSet.iloc[:, 1:7]
target = dataSet.iloc[:, 0]
arrReadings = readings.as_matrix()
arrTarget = np.reshape(target.as_matrix(), -1)

norm_Data = preprocessing.normalize(arrReadings)
arr_norm_Data = segment_signal(norm_Data, 100)
print(arr_norm_Data.shape)
'''

dataSet = dataSet.iloc[:,:7]
dataSet.columns = ["activity","handx_accel","handy_accel","handz_accel","chestx_gyro","chesty_gyro","chestz_gyro"]
list_dataSet = []
list_dataSetFlat = []
list_target = []
for nActivity in range(1,12):
    print('nActivity: {0}'.format(nActivity))
    tempdf = dataSet[dataSet.activity == nActivity]
    list_dataSet.append(segment_signal_sliding(tempdf.iloc[:,1:7].as_matrix(), windowSize,0))
    print(list_dataSet[nActivity-1].shape)
    list_target.append(np.ones((list_dataSet[nActivity-1].shape[0],1)))
    print(list_target[nActivity-1].shape)
    segments = window_input(list_dataSet[nActivity-1])
    #print(segments)
    list_dataSetFlat.append(segments)
    print(list_dataSetFlat[nActivity-1].shape)
    
'''    
for nActivity in range(1,12):
    print('nActivity: {0}'.format(nActivity))
    print(list_dataSetFlat[nActivity-1])        
    print(list_target[nActivity-1])
'''
'''
for nNodes in range(6,101):
    print('Implementing {0} nodes'.format(nNodes))
    kfold = KFold(n_splits=10, shuffle=True)
    fold_index = 0
    for train, test in kfold.split(norm_Data):
        print('Starting NN fold %i' %fold_index)
        mlpclf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(nNodes,),random_state=1)
        mlpclf.fit(norm_Data[train], arrTarget[train])
        nn_predictions = mlpclf.predict(norm_Data[test])
        accuracyNN = mlpclf.score(norm_Data[test],arrTarget[test])
        cmNN = confusion_matrix(arrTarget[test],nn_predictions)
        with open('evaluation.txt', 'a') as f:
         f.write('For %i fold\n' %fold_index)
         f.write('The classification accuracy for NN is %f\n' %accuracyNN)
         f.write('And the confusion matrix is:\n')
         f.write(np.array2string(cmNN))
         f.write('\n\n')
        
        print('The classification accuracy for NN is %f' %accuracyNN)
        print('And the confusion matrix is:')
        print(cmNN)
        fold_index += 1
'''