# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 10:39:59 2017

@author: avidr
"""
import numpy as np
from filterpy.kalman import KalmanFilter

# Interval time
dt = 0.1
# Process noise standard deviation
sd_a = 1.

# Work identities
dt2 = 0.5*(dt**2)
dt3 = dt**2
dt4 = 0.5*(dt**3)
dt5 = 0.25*(dt**4)


kfil = KalmanFilter(dim_x = 9, dim_z = 3)


# Assuming initial values to be 0
# State estimate vector and initial values
kfil.x = np.array([0.],
                  [0.],
                  [0.],
                  [0.],
                  [0.],
                  [0.],
                  [0.],
                  [0.],
                  [0.])

# Kinematic equations array
# State transition matrix
kfil.F = np.array([1., 0., 0., dt, 0., 0., dt2, 0., 0.],
                  [0., 1., 0., 0., dt, 0., 0., dt2, 0.],
                  [0., 0., 1., 0., 0., dt, 0., 0., dt2],
                  [0., 0., 0., 1., 0., 0., dt, 0., 0.],
                  [0., 0., 0., 0., 1., 0., 0., dt, 0.],
                  [0., 0., 0., 0., 0., 1., 0., 0., dt],
                  [0., 0., 0., 0., 0., 0., 1., 0., 0.],
                  [0., 0., 0., 0., 0., 0., 0., 1., 0.],
                  [0., 0., 0., 0., 0., 0., 0., 0., 1.])

# Measuring only acceleration in the 3 axes
# Measurement function
kfil.H = np.array([0., 0., 0., 0., 0., 0., 1., 0., 0.],
                  [0., 0., 0., 0., 0., 0., 0., 1., 0.],
                  [0., 0., 0., 0., 0., 0., 0., 0., 1.])

# Process noise covariance matrix
kfil.Q = (sd_a ** 2) * np.array([dt5, dt5, dt5, dt4, dt4, dt4, dt2, dt2, dt2],
                              [dt5, dt5, dt5, dt4, dt4, dt4, dt2, dt2, dt2],
                              [dt5, dt5, dt5, dt4, dt4, dt4, dt2, dt2, dt2],
                              [dt4, dt4, dt4, dt3, dt3, dt3, dt, dt, dt],
                              [dt4, dt4, dt4, dt3, dt3, dt3, dt, dt, dt],
                              [dt4, dt4, dt4, dt3, dt3, dt3, dt, dt, dt],
                              [dt2, dt2, dt2, dt, dt, dt, 1., 1., 1.],
                              [dt2, dt2, dt2, dt, dt, dt, 1., 1., 1.],
                              [dt2, dt2, dt2, dt, dt, dt, 1., 1., 1.])


# Covariance Matrix
# Assuming intial values are nil, initial P are 0
# Provide variance values on main diagonal if initial values are not known perfectly
kfil.P = np.zeros(9, dtype=float)

# Measurement noise matrix
# Assuming variance in measurement noise is 1, check datasheet
# Diagonal is the varaiance in measurement noise
# Off-diagonal is correlation between the different respective noises
kfil.R = np.array([1., 0., 0.],
                  [0., 1., 0.],
                  [0., 0., 1.])
