# -*- coding: utf-8 -*-
"""
Created on Sun May  1 17:01:32 2016

@author: matt
"""

import numpy as np
from scipy import optimize
from scipy.io import loadmat

#make a random test/train split 
def train_test_split(X, y, test_size = 0.3):
    np.random.seed(666)    
    ylen = len(y)
    yrange = range(ylen); np.random.shuffle(yrange)
    newX = [X[i][:] for i in yrange]
    newy = [y[i] for i in yrange]
    
    trainIndex = int(round(ylen*(1-test_size)))
    train_y, test_y = np.asarray(newy[:trainIndex]),np.asarray(newy[trainIndex:])
    train_X, test_X = np.asarray(newX[:][:trainIndex]),np.asarray(newX[:][trainIndex:])
    return train_X, test_X, train_y, test_y

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_prime(z):
    sig = sigmoid(z)
    return sig * (1 - sig)

def sumsqr(a):
    return np.sum(a ** 2)

def rand_init(l_in, l_out, epsilon_init = 0.12):
    return np.random.rand(l_out, l_in + 1) * 2 * epsilon_init - epsilon_init

# reshape thetas to put into minimize function
def pack_thetas(t1, t2):
    return np.concatenate((t1.reshape(-1), t2.reshape(-1)))

# return thetas to original shape
def unpack_thetas(thetas, input_layer_size, hidden_layer_size, num_labels):
    t1_start = 0
    t1_end = hidden_layer_size * (input_layer_size + 1)
    t1 = thetas[t1_start:t1_end].reshape((hidden_layer_size, input_layer_size + 1))
    t2 = thetas[t1_end:].reshape((num_labels, hidden_layer_size + 1))
    return t1, t2

# forward propagation function
def forward_prop(X, t1, t2):
    m = X.shape[0]
    ones = None
    if len(X.shape) == 1:
        ones = np.array(1).reshape(1,)
    else:
        ones = np.ones(m).reshape(m,1)
    
    # Input layer
    a1 = np.hstack((ones, X))
    
    # Hidden Layer
    z2 = np.dot(t1, a1.T)
    a2 = sigmoid(z2)
    a2 = np.hstack((ones, a2.T))
    
    # Output layer
    z3 = np.dot(t2, a2.T)
    a3 = sigmoid(z3)
    return a1, z2, a2, z3, a3

def cost_function(thetas, input_layer_size, hidden_layer_size, num_labels, X, y, reg_lambda):
    t1, t2 = unpack_thetas(thetas, input_layer_size, hidden_layer_size, num_labels)
    
    m = X.shape[0]
    Y = np.zeros((len(y), num_labels)) 
    for i in range(len(y)):
        Y[i, y[i]] = 1;
        
    a1, z2, a2, z3, h = forward_prop(X, t1, t2)
    costPositive = -Y * np.log(h).T
    costNegative = (1 - Y) * np.log(1 - h).T
    cost = costPositive - costNegative
    J = np.sum(cost) / m
    
    t1n, t2n = t1, t2
    t1n[:,0], t2n[:,0] = 0,0    
    st2 = sum(sum(t1n**2)) + sum(sum(t2n**2))
    st2 = reg_lambda/(2.*m)*st2
    
    J = J + st2
    
    return J
    
# derivative of cost function
def cost_function_prime(thetas, input_layer_size, hidden_layer_size, num_labels, X, y, reg_lambda):
    t1, t2 = unpack_thetas(thetas, input_layer_size, hidden_layer_size, num_labels)
    
    m = X.shape[0]
    t1f = t1[:, 1:]
    t2f = t2[:, 1:]
    Y = np.zeros((len(y), num_labels)) 
    for i in range(len(y)):
        Y[i, y[i]] = 1;

    Delta1, Delta2 = 0, 0
    for i, row in enumerate(X):
        a1, z2, a2, z3, a3 = forward_prop(row, t1, t2)
        
        # Backprop
        d3 = a3 - Y[i, :].T
        d2 = np.dot(t2f.T, d3) * sigmoid_prime(z2)
        
        Delta2 += np.dot(d3[np.newaxis].T, a2[np.newaxis])
        Delta1 += np.dot(d2[np.newaxis].T, a1[np.newaxis])
#    print(Delta1)    
    Theta1_grad = (1.0 / m) * Delta1
    Theta2_grad = (1.0 / m) * Delta2
    
    if reg_lambda != 0:
        Theta1_grad[:, 1:] = Theta1_grad[:, 1:] + (reg_lambda / m) * t1f
        Theta2_grad[:, 1:] = Theta2_grad[:, 1:] + (reg_lambda / m) * t2f
    
    return pack_thetas(Theta1_grad, Theta2_grad)

def fit(X, y, maxiter):
    input_layer_size = X.shape[1]
    num_labels = len(set(y))
    
    theta1_0 = rand_init(input_layer_size, hidden_layer_size, epsilon_init)
    theta2_0 = rand_init(hidden_layer_size, num_labels, epsilon_init)
    thetas0 = pack_thetas(theta1_0, theta2_0)
    
    options = {'maxiter': maxiter}
    res = optimize.minimize(cost_function, thetas0, jac=cost_function_prime, method=method, 
                             args=(input_layer_size, hidden_layer_size, num_labels, X, y, 0), options=options)
    
    t1, t2 = unpack_thetas(res.x, input_layer_size, hidden_layer_size, num_labels)
    return t1, t2
    
def debugInitializeWeights(fan_out, fan_in):
    W = np.zeros((fan_out, 1 + fan_in))
    W = np.reshape(np.sin(range(1,np.size(W)+1)),np.shape(W))/10
    return W
    
# check gradients are roughly the same, should be within 1e-9
def checkNNgradients(reg_lambda):
    input_layer_size = 3;
    hidden_layer_size = 5;
    num_labels = 10
    m = 5;
    reg_lambda = float(reg_lambda)
    Theta1 = debugInitializeWeights(hidden_layer_size, input_layer_size);
    Theta2 = debugInitializeWeights(num_labels, hidden_layer_size);
    X  = debugInitializeWeights(m, input_layer_size - 1);
    y  = 1 + np.mod(range(m), num_labels).T
    nn_params = pack_thetas(Theta1, Theta2)
    grad = cost_function_prime(nn_params, input_layer_size, hidden_layer_size, num_labels, X, y, reg_lambda)
    
#    Compute numerical gradient
    numgrad, perturb = np.zeros(np.shape(nn_params)), np.zeros(np.shape(nn_params))
    e1 = 1e-4
    for p in range(np.size(nn_params)):
        perturb[p] = e1
        loss1 = cost_function(nn_params - perturb, input_layer_size, hidden_layer_size, num_labels, X, y, reg_lambda)
        loss2 = cost_function(nn_params + perturb, input_layer_size, hidden_layer_size, num_labels, X, y, reg_lambda)
        numgrad[p] = (loss2-loss1)/(2.0*e1)
        perturb[p] = 0
    diff = np.linalg.norm(numgrad - grad)/np.linalg.norm(numgrad + grad)
#    print(np.shape(grad))
    return diff
            
def predict(X, theta1, theta2):
    a1, z2, a2, z3, a3 = forward_prop(X, theta1, theta2)
    return a3

# determine accuracy
def accuracy(y_predict, y_test):
    leny = len(y_predict)
    return sum(y_predict == y_test)/float(leny)

# ============================================================================    

epsilon_init = 0.12    # random initialization parameter
hidden_layer_size = 35 # nodes in hidden layer
method = 'TNC'         # minimisation method
maxiter = 100          # max iterations of minisation function

# load data
data = loadmat('ex4data1.mat')
X, y = data['X'], data['y']
y = y.reshape(X.shape[0], )
y = y - 1  # convert to 0-9

num_labels = len(set(y))      # number of outputs
reg_lambda = 3.0              # regularization parameter
input_layer_size = X.shape[1] # Number of input (features)

# Initilise weights
initial_Theta1 = rand_init(input_layer_size, hidden_layer_size, epsilon_init)
initial_Theta2 = rand_init(hidden_layer_size, num_labels, epsilon_init)
initial_nn_params = pack_thetas(initial_Theta1, initial_Theta2)

# check difference in gradients
diff = checkNNgradients(reg_lambda)
print('Check gradients ',diff)

# Generate train and test datasets with 70/30 split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size = 0.3)

## Get optimal theta values
#Theta1Opt, Theta2Opt = fit(X_train, y_train, maxiter)
#
## predict on validation dataset
#prediction = np.argmax(predict(X_val, Theta1Opt, Theta2Opt), axis = 0)
#acc1 = accuracy(prediction, y_val)
#print('accuracy',acc1)
#
