import numpy as np

# Activation function: Sigmoid
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Derivative of sigmoid function
def sigmoid_derivative(x):
    return x * (1 - x)

# Training Data
inputs = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

# Expected Output (XOR problem)
outputs = np.array([
    [0],
    [1],
    [1],
    [0]
])

# Initialize weights randomly with mean 0
np.random.seed(1)
weights_input_hidden = np.random.rand(2, 4) - 0.5  # input to hidden layer
weights_hidden_output = np.random.rand(4, 1) - 0.5  # hidden to output layer

# Hyperparameters
learning_rate = 0.1
epochs = 10000

# Training loop
for epoch in range(epochs):
    # Forward Propagation
    hidden_input = np.dot(inputs, weights_input_hidden)
    hidden_output = sigmoid(hidden_input)
    
    final_input = np.dot(hidden_output, weights_hidden_output)
    final_output = sigmoid(final_input)
    
    # Calculate error
    error = outputs - final_output
    if epoch % 2000 == 0:
        print(f"Epoch {epoch}, Error: {np.mean(np.abs(error))}")
    
    # Backpropagation
    d_output = error * sigmoid_derivative(final_output)
    
    error_hidden_layer = d_output.dot(weights_hidden_output.T)
    d_hidden_layer = error_hidden_layer * sigmoid_derivative(hidden_output)
    
    # Update weights
    weights_hidden_output += hidden_output.T.dot(d_output) * learning_rate
    weights_input_hidden += inputs.T.dot(d_hidden_layer) * learning_rate

# Testing the neural network after training
print("\nTesting neural network on training data:")
for i in range(len(inputs)):
    hidden_output = sigmoid(np.dot(inputs[i], weights_input_hidden))
    final_output = sigmoid(np.dot(hidden_output, weights_hidden_output))
    print(f"Input: {inputs[i]}, Predicted Output: {final_output[0]:.4f}, Expected Output: {outputs[i][0]}")
