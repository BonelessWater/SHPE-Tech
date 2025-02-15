import torch
import torch.nn as nn
import torch.optim as optim

# Define the XOR data
inputs = torch.tensor([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=torch.float32)
outputs = torch.tensor([[0], [1], [1], [0]], dtype=torch.float32)

# Define the neural network model
class XORNeuralNetwork(nn.Module):
    def __init__(self):
        super(XORNeuralNetwork, self).__init__()
        self.hidden1 = nn.Linear(2, 10)   # Input layer to hidden layer 1 with 10 nodes
        self.hidden2 = nn.Linear(10, 8)   # Hidden layer 1 to hidden layer 2 with 8 nodes
        self.output = nn.Linear(8, 1)     # Hidden layer 2 to output layer

    def forward(self, x):
        x = torch.relu(self.hidden1(x))   # ReLU activation for first hidden layer
        x = torch.relu(self.hidden2(x))   # ReLU activation for second hidden layer
        x = torch.sigmoid(self.output(x)) # Sigmoid activation for the output layer
        return x

# Initialize the model, loss function, and optimizer
model = XORNeuralNetwork()
criterion = nn.MSELoss()              # Mean Squared Error loss
optimizer = optim.SGD(model.parameters(), lr=0.1)  # Stochastic Gradient Descent optimizer

# Training the model
epochs = 10000
for epoch in range(epochs):
    # Forward pass
    predictions = model(inputs)
    loss = criterion(predictions, outputs)
    
    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Print loss every 1000 epochs
    if epoch % 1000 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# Testing the model after training
print("\nTesting the trained neural network:")
with torch.no_grad():  # No need to compute gradients for testing
    for i in range(len(inputs)):
        prediction = model(inputs[i])
        print(f"Input: {inputs[i].numpy()}, Predicted Output: {prediction.item():.4f}, Expected Output: {outputs[i].item()}")
