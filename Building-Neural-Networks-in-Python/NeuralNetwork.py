# -*- coding: utf-8 -*-
"""
Created on Sun May  1 17:01:32 2016

@author: matt
"""

import numpy as np
from scipy import optimize
from scipy.io import loadmat

def train_test_split(X, y, test_size = 0.3, seed = 666):
    '''
    Make a randon train test split
    '''
    np.random.seed(seed)    
    ylen = len(y)
    yrange = range(ylen); np.random.shuffle(yrange)
    newX = [X[i][:] for i in yrange]
    newy = [y[i] for i in yrange]
    
    trainIndex = int(round(ylen*(1-test_size)))
    train_y, test_y = np.asarray(newy[:trainIndex]),np.asarray(newy[trainIndex:])
    train_X, test_X = np.asarray(newX[:][:trainIndex]),np.asarray(newX[:][trainIndex:])
    return train_X, test_X, train_y, test_y

def sigmoid(x):
    '''
    Compute sigmoid function
    '''
    return 1 / (1 + np.exp(-x))

def sigmoid_prime(x):
    '''
    Compute derivative of sigmoid function
    '''
    sigm = sigmoid(x)
    return sigm * (1 - sigm)


def rand_init(l_in, l_out, epsilon_init = 0.12):
    '''
    Make inital random array
    '''
    return np.random.rand(l_out, l_in + 1) * 2 * epsilon_init - epsilon_init

def pack_thetas(theta1, theta2):
    '''
    reshape thetas to put into minimize function
    '''
    return np.concatenate((theta1.reshape(-1), theta2.reshape(-1)))

def unpack_thetas(thetas, input_layer_size, hidden_layer_size, num_labels):
    '''
    return thetas to original shape
    '''
    theta1_start = 0
    theta1_end = hidden_layer_size * (input_layer_size + 1)
    theta1 = thetas[theta1_start:theta1_end].reshape((hidden_layer_size, input_layer_size + 1))
    theta2 = thetas[theta1_end:].reshape((num_labels, hidden_layer_size + 1))
    return theta1, theta2

def debugInitializeWeights(fan_out, fan_in):
    W = np.zeros((fan_out, 1 + fan_in))
    W = np.reshape(np.sin(range(1,np.size(W)+1)),np.shape(W))/10
    return W
  
def accuracy(y_predict, y_test):
    '''
    Compute accuracy
    '''
    leny = len(y_predict)
    return (sum(y_predict == y_test)/float(leny)) * 100
    
# ============================================================================

class NNet(object):
    def __init__(self, reg_lambda = 0, epsilon_init = 0.12, hidden_layer_size = 25, opti_method = 'TNC', maxiter = 500):
        self.reg_lambda = reg_lambda
        self.epsilon_init = epsilon_init
        self.hidden_layer_size = hidden_layer_size
        self.activation_func = sigmoid
        self.activation_func_prime = sigmoid_prime
        self.method = opti_method
        self.maxiter = maxiter
       
    def forward_prop(self, X, theta1, theta2):
        '''
        Forward propagation function
        '''
        m = X.shape[0]
        ones = None
        if len(X.shape) == 1:
            ones = np.array(1).reshape(1,)
        else:
            ones = np.ones(m).reshape(m,1)
        
        # Input layer
        a1 = np.hstack((ones, X))
        
        # Hidden Layer
        z2 = np.dot(theta1, a1.T)
        a2 = self.activation_func(z2)
        a2 = np.hstack((ones, a2.T))
        
        # Output layer
        z3 = np.dot(theta2, a2.T)
        a3 = self.activation_func(z3)
        return a1, z2, a2, z3, a3
    
    def cost_function(self, thetas, input_layer_size, num_labels, X, y):
        '''
        Compute the cost function
        '''
        theta1, theta2 = unpack_thetas(thetas, input_layer_size, self.hidden_layer_size, num_labels)
        
        m = X.shape[0]
        Y = np.zeros((len(y), num_labels)) 
        for i in range(len(y)):
            Y[i, y[i]] = 1;
            
        a1, z2, a2, z3, h = self.forward_prop(X, theta1, theta2)
        costPositive = -Y * np.log(h).T
        costNegative = (1 - Y) * np.log(1 - h).T
        cost = costPositive - costNegative
        J = np.sum(cost) / m
        
        t1n, t2n = theta1, theta2
        t1n[:,0], t2n[:,0] = 0,0    
        st2 = sum(sum(t1n**2)) + sum(sum(t2n**2))
        st2 = self.reg_lambda/(2.*m)*st2
        
        J += st2
        
        return J
        
    def cost_function_prime(self, thetas, input_layer_size, num_labels, X, y):
        '''
        Compute the derivative of the cost function
        '''
        theta1, theta2 = unpack_thetas(thetas, input_layer_size, self.hidden_layer_size, num_labels)
        
        m = X.shape[0]
        theta1f = theta1[:, 1:]
        theta2f = theta2[:, 1:]
        Y = np.zeros((len(y), num_labels)) 
        for i in range(len(y)):
            Y[i, y[i]] = 1;
    
        Delta1, Delta2 = 0, 0
        for i, row in enumerate(X):
            a1, z2, a2, z3, a3 = self.forward_prop(row, theta1, theta2)
            
            # Backprop
            d3 = a3 - Y[i, :].T
            d2 = np.dot(theta2f.T, d3) * self.activation_func_prime(z2)
            
            Delta2 += np.dot(d3[np.newaxis].T, a2[np.newaxis])
            Delta1 += np.dot(d2[np.newaxis].T, a1[np.newaxis])
    #    print(Delta1)    
        Theta1_grad = (1.0 / m) * Delta1
        Theta2_grad = (1.0 / m) * Delta2
        
        if self.reg_lambda != 0:
            Theta1_grad[:, 1:] = Theta1_grad[:, 1:] + (self.reg_lambda / m) * theta1f
            Theta2_grad[:, 1:] = Theta2_grad[:, 1:] + (self.reg_lambda / m) * theta2f
        
        return pack_thetas(Theta1_grad, Theta2_grad)
    
    def fit(self, X, y, return_weights = False):
        '''
        Fit the model
        '''
        self.X = X
        self.y = y
        input_layer_size = X.shape[1]
        num_labels = len(set(y))
        
        theta1_0 = rand_init(input_layer_size, self.hidden_layer_size, self.epsilon_init)
        theta2_0 = rand_init(self.hidden_layer_size, num_labels, self.epsilon_init)
        thetas0 = pack_thetas(theta1_0, theta2_0)
        
        options = {'maxiter': self.maxiter}
        res = optimize.minimize(self.cost_function, thetas0, jac = self.cost_function_prime, 
                                method=self.method, args=(input_layer_size, 
                                                          num_labels, X, y), 
                                                          options=options)
        
        self.theta1, self.theta2 = unpack_thetas(res.x, input_layer_size, self.hidden_layer_size, num_labels)
        if return_weights:
            return self.theta1, self.theta2
        else: return None
        
    def checkNNgradients(self):
        '''
        Check numerically computed gradient and the gradient computed by the 
        cost function are roughly the same, should be ideally be within 1e-9
        '''
        input_layer_size = 3;
        hidden_layer_size = self.hidden_layer_size;
        num_labels = 10
        m = 5;
        Theta1 = debugInitializeWeights(hidden_layer_size, input_layer_size);
        Theta2 = debugInitializeWeights(num_labels, hidden_layer_size);
        X  = debugInitializeWeights(m, input_layer_size - 1);
        y  = 1 + np.mod(range(m), num_labels).T
        nn_params = pack_thetas(Theta1, Theta2)
        grad = self.cost_function_prime(nn_params, input_layer_size, num_labels, X, y)
        
        #Compute numerical gradient
        numgrad, perturb = np.zeros(np.shape(nn_params)), np.zeros(np.shape(nn_params))
        e1 = 1e-4
        for p in range(np.size(nn_params)):
            perturb[p] = e1
            loss1 = self.cost_function(nn_params - perturb, input_layer_size, num_labels, X, y)
            loss2 = self.cost_function(nn_params + perturb, input_layer_size, num_labels, X, y)
            numgrad[p] = (loss2-loss1)/(2.0*e1)
            perturb[p] = 0
        diff = np.linalg.norm(numgrad - grad)/np.linalg.norm(numgrad + grad)
        
        if diff < 1e-7:
            print "Difference between numerical gradient and gradient computed by cost function sufficiently small at %.6e" % (diff)
        else:
            print "Differnce between gradients are large at %.6e, consider checking" % (diff)
        return diff
                
    def predict_proba(self, X):
        '''
        Make a prediction on the model given features
        '''
        a1, z2, a2, z3, a3 = self.forward_prop(X, self.theta1, self.theta2)
        return a3
    
    def predict(self, X):
        '''
        Make a prediction on the model given features
        '''
        a1, z2, a2, z3, a3 = self.forward_prop(X, self.theta1, self.theta2)
        return np.argmax(a3, axis = 0)
    

# ============================================================================    


# load data
data = loadmat('digit_data.mat')
X, y = data['X'], data['y']
y = y.reshape(X.shape[0], )
y = y - 1  # convert to 0-9

num_labels = len(set(y))      # number of outputs
reg_lambda = 3.0              # regularization parameter
input_layer_size = X.shape[1] # Number of input (features)

# Generate train and test datasets with 70/30 split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3)

# Initialise model
nnet = NNet(reg_lambda = 3.0, epsilon_init = 0.12, hidden_layer_size = 25, 
            opti_method = 'TNC', maxiter = 500)
nnet.checkNNgradients()           # check gradients
nnet.fit(X_train, y_train)        # fit model
prediction = nnet.predict(X_test) # predict on tst set
accuracy(prediction, y_test)      # return accuracy
