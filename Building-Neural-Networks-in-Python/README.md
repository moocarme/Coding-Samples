# Neural Networks in Python

Since scikit-learn has no native neural networks I decided to make my own based on Andrew Ngs Coursera machine learning course.
The neural network has only one hidden layer, but the number of nodes in the layer is variable.

The neural network works well, and is tested on the digit recognizer dataset from Kaggle which is included here as a .mat file.

### Data Dictionary

- *epsilon_init* - parameter used to set boundary of random inital weights for the neural network (float)
- *hidden_layer_size* - number of nodes in hidden layer size, 35 is a good trade-off between speed and accuracy (int)
- *method* - minimisation method to use to minimise error on the weights via the cost function (least squares), (str)
- *maxiter* - maximum number of iterations for the minimisation method (int)
- *X* - training data for the digit recognizer, the pixel intensities of the image (matrix)
- *y* - results for the digit recognizer dataset (vector)
- *num_labels* - number of different possible outcomes (digits) (int)
- *reg_lambda* - regularization parameter to prevent overfitting (float)
- *input_layer_size* - number of different features, for the digit recognizer this corresponds to the number of pixels (int)
- *initial_Theta1* - initial weights for the first layer (matrix)
- *initial_Theta2* - initial weights for the hidden layer (matrix)  
- *initial_nn_params* - both initial weights combined in vector format (vector)
- *diff* - a check to compute difference between gradients produced by the cost_function_prime function and derivative calculated by Newton's method, should be 1e-9 or less (float)
- *X_train* - training dataset (matrix)
- *y_train* - training validation results (vector)
- *X_test* - validation dataset (matrix)
- *y_train* - validation results dataset (vector)
- *Theta1Opt* - optimized weights for first layer (matrix)
- *Theta2Opt* - optimized weights for hidden layer (matrix)
- *prediction* - prediction on test dataset (matrix) 
- *acc1* - accuracy of prediction compared to actual results
