import os
import numpy as np
from sklearn import preprocessing
from sklearn.externals import joblib

winSize = 120
mlp_filepath = os.getcwd() + '/mlp/'
mlp_filename = 'mlpclf1.pk1'
cache_filename = 'cache.csv'
cache_filepath = os.getcwd() + '/cache/'

print("Loading MLP")
mlpclf = joblib.load(mlp_filepath + mlp_filename)
print("MLP loaded")

for x in range(1,101):
    print("Predicting with input from last 120 lines of {0}".format(cache_filename))
    with open(cache_filepath + cache_filename,'rb') as f:
        lines = f.readlines()
    arrInput = np.genfromtxt(lines[-winSize:],delimiter=',')
    arrInput = arrInput.flatten()
    arrInput = preprocessing.normalize(arrInput).reshape(1,-1)
    print(arrInput.shape)
    result = mlpclf.predict(arrInput)
    print(result)
