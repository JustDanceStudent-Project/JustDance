import os
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib

winSize = 120
mlp_filepath = os.getcwd() + '/mlp/'
mlp_filename = 'mlpclf1.pk1'
cache_filename = 'anniyacache2.csv'
cache_filepath = os.getcwd() + '/cache/'

print("Loading MLP")
mlpclf = joblib.load(mlp_filepath + mlp_filename)
print("MLP loaded")

for x in range(1,101):
    with open(cache_filepath + cache_filename,'rb') as f:
        lines = f.readlines()
    if(x*winSize < len(lines)):
        print("Predicting with input from {0}th {2} lines of {1}".format(x,cache_filename,winSize))
        arrInput = np.genfromtxt(lines[(x-1)*winSize:x*winSize],delimiter=',')
        arrInput = arrInput.flatten()
        arrInput = preprocessing.normalize(arrInput).reshape(1,-1)
        #print(arrInput.shape)
        result = mlpclf.predict(arrInput)
        print(int(result))
    else:
        print("End of cache file")
        break