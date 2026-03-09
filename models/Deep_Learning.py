"""
Deep Learning Models
Implementation of neural network architectures and deep learning algorithms
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any, Callable
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.datasets import make_classification, make_regression
import logging
from abc import ABC, abstractmethod
import time

logger = logging.getLogger(__name__)


class Layer(ABC):
    """Abstract base class for neural network layers"""

    @abstractmethod
    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass"""
        pass

    @abstractmethod
    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Backward pass"""
        pass

    @abstractmethod
    def update_parameters(self, learning_rate: float):
        """Update layer parameters"""
        pass


class Dense(Layer):
    """Fully connected layer"""

    def __init__(self, input_size: int, output_size: int,
                 activation: str = 'linear', weight_init: str = 'xavier'):
        self.input_size = input_size
        self.output_size = output_size
        self.activation = activation

        # Initialize weights and biases
        if weight_init == 'xavier':
            limit = np.sqrt(6 / (input_size + output_size))
            self.W = np.random.uniform(-limit, limit, (input_size, output_size))
        elif weight_init == 'he':
            std = np.sqrt(2 / input_size)
            self.W = np.random.normal(0, std, (input_size, output_size))
        else:
            self.W = np.random.randn(input_size, output_size) * 0.01

        self.b = np.zeros((1, output_size))

        # Gradients
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b)

        # Cache for backprop
        self.A_prev = None
        self.Z = None

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass through dense layer"""
        self.A_prev = X
        self.Z = np.dot(X, self.W) + self.b

        if self.activation == 'relu':
            return np.maximum(0, self.Z)
        elif self.activation == 'sigmoid':
            return 1 / (1 + np.exp(-self.Z))
        elif self.activation == 'tanh':
            return np.tanh(self.Z)
        elif self.activation == 'softmax':
            exp_Z = np.exp(self.Z - np.max(self.Z, axis=1, keepdims=True))
            return exp_Z / np.sum(exp_Z, axis=1, keepdims=True)
        else:  # linear
            return self.Z

    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Backward pass through dense layer"""
        m = self.A_prev.shape[0]

        # Activation derivative
        if self.activation == 'relu':
            dZ = dA * (self.Z > 0)
        elif self.activation == 'sigmoid':
            A = 1 / (1 + np.exp(-self.Z))
            dZ = dA * A * (1 - A)
        elif self.activation == 'tanh':
            dZ = dA * (1 - np.tanh(self.Z) ** 2)
        elif self.activation == 'softmax':
            # For softmax, dZ is computed in the loss function
            dZ = dA
        else:  # linear
            dZ = dA

        # Parameter gradients
        self.dW = np.dot(self.A_prev.T, dZ) / m
        self.db = np.sum(dZ, axis=0, keepdims=True) / m

        # Input gradient
        dA_prev = np.dot(dZ, self.W.T)
        return dA_prev

    def update_parameters(self, learning_rate: float):
        """Update weights and biases"""
        self.W -= learning_rate * self.dW
        self.b -= learning_rate * self.db


class Dropout(Layer):
    """Dropout regularization layer"""

    def __init__(self, dropout_rate: float = 0.5):
        self.dropout_rate = dropout_rate
        self.mask = None
        self.training = True

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass with dropout"""
        if self.training:
            self.mask = np.random.rand(*X.shape) > self.dropout_rate
            return X * self.mask / (1 - self.dropout_rate)
        else:
            return X

    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Backward pass through dropout"""
        if self.training:
            return dA * self.mask / (1 - self.dropout_rate)
        else:
            return dA

    def update_parameters(self, learning_rate: float):
        """No parameters to update"""
        pass


class BatchNormalization(Layer):
    """Batch Normalization layer"""

    def __init__(self, input_size: int, epsilon: float = 1e-8, momentum: float = 0.9):
        self.input_size = input_size
        self.epsilon = epsilon
        self.momentum = momentum

        # Parameters
        self.gamma = np.ones((1, input_size))
        self.beta = np.zeros((1, input_size))

        # Running statistics
        self.running_mean = np.zeros((1, input_size))
        self.running_var = np.ones((1, input_size))

        # Gradients
        self.dgamma = np.zeros_like(self.gamma)
        self.dbeta = np.zeros_like(self.beta)

        # Cache for backprop
        self.X_norm = None
        self.mean = None
        self.var = None

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass with batch normalization"""
        if self.training:
            self.mean = np.mean(X, axis=0, keepdims=True)
            self.var = np.var(X, axis=0, keepdims=True)

            # Update running statistics
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * self.mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * self.var
        else:
            self.mean = self.running_mean
            self.var = self.running_var

        self.X_norm = (X - self.mean) / np.sqrt(self.var + self.epsilon)
        return self.gamma * self.X_norm + self.beta

    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Backward pass through batch normalization"""
        m = dA.shape[0]

        # Gradients w.r.t. parameters
        self.dgamma = np.sum(dA * self.X_norm, axis=0, keepdims=True)
        self.dbeta = np.sum(dA, axis=0, keepdims=True)

        # Gradient w.r.t. input
        dX_norm = dA * self.gamma
        dvar = np.sum(dX_norm * (self.X_norm - self.mean) * (-0.5) * (self.var + self.epsilon)**(-1.5), axis=0, keepdims=True)
        dmean = np.sum(dX_norm * (-1) / np.sqrt(self.var + self.epsilon), axis=0, keepdims=True) + \
                dvar * np.sum(-2 * (self.X_norm - self.mean), axis=0, keepdims=True) / m

        dX = dX_norm / np.sqrt(self.var + self.epsilon) + \
             dvar * 2 * (self.X_norm - self.mean) / m + \
             dmean / m

        return dX

    def update_parameters(self, learning_rate: float):
        """Update gamma and beta"""
        self.gamma -= learning_rate * self.dgamma
        self.beta -= learning_rate * self.dbeta


class NeuralNetwork:
    """
    Custom Neural Network implementation
    """

    def __init__(self, learning_rate: float = 0.01, loss: str = 'mse'):
        self.layers = []
        self.learning_rate = learning_rate
        self.loss = loss
        self.is_fitted = False
        self.training_history = {'loss': [], 'val_loss': []}

    def add_layer(self, layer: Layer):
        """Add a layer to the network"""
        self.layers.append(layer)

    def _forward_pass(self, X: np.ndarray) -> np.ndarray:
        """Forward pass through all layers"""
        A = X
        for layer in self.layers:
            A = layer.forward(A)
        return A

    def _backward_pass(self, dA: np.ndarray):
        """Backward pass through all layers"""
        for layer in reversed(self.layers):
            dA = layer.backward(dA)

    def _update_parameters(self):
        """Update parameters in all layers"""
        for layer in self.layers:
            layer.update_parameters(self.learning_rate)

    def _compute_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute loss function"""
        if self.loss == 'mse':
            return np.mean((y_true - y_pred) ** 2)
        elif self.loss == 'binary_crossentropy':
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        elif self.loss == 'categorical_crossentropy':
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))
        else:
            raise ValueError(f"Unknown loss function: {self.loss}")

    def _compute_loss_gradient(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Compute gradient of loss function"""
        m = y_true.shape[0]
        if self.loss == 'mse':
            return 2 * (y_pred - y_true) / m
        elif self.loss == 'binary_crossentropy':
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            return (y_pred - y_true) / (y_pred * (1 - y_pred) * m)
        elif self.loss == 'categorical_crossentropy':
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            return (y_pred - y_true) / m
        else:
            raise ValueError(f"Unknown loss function: {self.loss}")

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series],
            epochs: int = 100, batch_size: int = 32,
            validation_split: float = 0.2, verbose: bool = True) -> Dict[str, List[float]]:
        """Train the neural network"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y)

        # Handle different output shapes
        if len(y.shape) == 1:
            if self.loss in ['binary_crossentropy', 'categorical_crossentropy']:
                # Convert to one-hot for classification
                n_classes = len(np.unique(y))
                y_onehot = np.zeros((y.shape[0], n_classes))
                y_onehot[np.arange(y.shape[0]), y.astype(int)] = 1
                y = y_onehot

        # Train-validation split
        if validation_split > 0:
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=validation_split, random_state=42
            )
        else:
            X_train, y_train = X, y
            X_val, y_val = None, None

        n_samples = X_train.shape[0]

        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_train_shuffled = X_train[indices]
            y_train_shuffled = y_train[indices]

            epoch_loss = 0

            # Mini-batch training
            for i in range(0, n_samples, batch_size):
                X_batch = X_train_shuffled[i:i+batch_size]
                y_batch = y_train_shuffled[i:i+batch_size]

                # Forward pass
                y_pred = self._forward_pass(X_batch)

                # Compute loss
                loss = self._compute_loss(y_batch, y_pred)
                epoch_loss += loss

                # Backward pass
                dA = self._compute_loss_gradient(y_batch, y_pred)
                self._backward_pass(dA)

                # Update parameters
                self._update_parameters()

            # Average loss for epoch
            epoch_loss /= (n_samples // batch_size)

            # Validation
            val_loss = None
            if X_val is not None:
                y_val_pred = self._forward_pass(X_val)
                val_loss = self._compute_loss(y_val, y_val_pred)

            self.training_history['loss'].append(epoch_loss)
            self.training_history['val_loss'].append(val_loss)

            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss:.4f}"
                      f"{f', Val Loss: {val_loss:.4f}' if val_loss is not None else ''}")

        self.is_fitted = True
        return self.training_history

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        # Set dropout to evaluation mode
        for layer in self.layers:
            if isinstance(layer, Dropout):
                layer.training = False

        predictions = self._forward_pass(X)

        # Reset dropout to training mode
        for layer in self.layers:
            if isinstance(layer, Dropout):
                layer.training = True

        return predictions

    def predict_classes(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict class labels"""
        predictions = self.predict(X)
        return np.argmax(predictions, axis=1)

    def evaluate(self, X: Union[np.ndarray, pd.DataFrame],
                y: Union[np.ndarray, pd.Series]) -> Dict[str, float]:
        """Evaluate model performance"""
        y_pred = self.predict(X)

        if isinstance(y, pd.Series):
            y = y.values
        y = np.array(y)

        if self.loss == 'mse':
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            return {'mse': mse, 'rmse': np.sqrt(mse), 'r2_score': r2}
        else:
            # Classification metrics
            y_pred_classes = np.argmax(y_pred, axis=1)
            if len(y.shape) > 1:
                y_true_classes = np.argmax(y, axis=1)
            else:
                y_true_classes = y

            return {
                'accuracy': accuracy_score(y_true_classes, y_pred_classes),
                'precision': precision_score(y_true_classes, y_pred_classes, average='weighted'),
                'recall': recall_score(y_true_classes, y_pred_classes, average='weighted'),
                'f1_score': f1_score(y_true_classes, y_pred_classes, average='weighted')
            }


class ConvolutionalLayer(Layer):
    """Convolutional layer for CNNs"""

    def __init__(self, input_channels: int, output_channels: int,
                 kernel_size: int, stride: int = 1, padding: int = 0):
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

        # Initialize kernels and biases
        self.kernels = np.random.randn(output_channels, input_channels,
                                     kernel_size, kernel_size) * 0.01
        self.biases = np.zeros((output_channels, 1))

        # Gradients
        self.dkernels = np.zeros_like(self.kernels)
        self.dbiases = np.zeros_like(self.biases)

        # Cache
        self.X = None

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass through convolutional layer"""
        self.X = X
        batch_size, input_channels, height, width = X.shape

        # Calculate output dimensions
        output_height = (height + 2 * self.padding - self.kernel_size) // self.stride + 1
        output_width = (width + 2 * self.padding - self.kernel_size) // self.stride + 1

        # Pad input if necessary
        if self.padding > 0:
            X_padded = np.pad(X, ((0, 0), (0, 0), (self.padding, self.padding),
                                 (self.padding, self.padding)), mode='constant')
        else:
            X_padded = X

        # Initialize output
        output = np.zeros((batch_size, self.output_channels, output_height, output_width))

        # Convolution operation
        for b in range(batch_size):
            for c_out in range(self.output_channels):
                for h in range(output_height):
                    for w in range(output_width):
                        h_start = h * self.stride
                        h_end = h_start + self.kernel_size
                        w_start = w * self.stride
                        w_end = w_start + self.kernel_size

                        receptive_field = X_padded[b, :, h_start:h_end, w_start:w_end]
                        output[b, c_out, h, w] = np.sum(receptive_field * self.kernels[c_out]) + self.biases[c_out]

        return output

    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Backward pass through convolutional layer"""
        batch_size, output_channels, output_height, output_width = dA.shape
        _, input_channels, input_height, input_width = self.X.shape

        # Pad input if necessary
        if self.padding > 0:
            X_padded = np.pad(self.X, ((0, 0), (0, 0), (self.padding, self.padding),
                                     (self.padding, self.padding)), mode='constant')
            dX_padded = np.zeros_like(X_padded)
        else:
            X_padded = self.X
            dX_padded = np.zeros_like(self.X)

        # Initialize gradients
        self.dkernels = np.zeros_like(self.kernels)
        self.dbiases = np.zeros_like(self.biases)

        # Backpropagation
        for b in range(batch_size):
            for c_out in range(self.output_channels):
                for h in range(output_height):
                    for w in range(output_width):
                        h_start = h * self.stride
                        h_end = h_start + self.kernel_size
                        w_start = w * self.stride
                        w_end = w_start + self.kernel_size

                        # Kernel gradients
                        receptive_field = X_padded[b, :, h_start:h_end, w_start:w_end]
                        self.dkernels[c_out] += receptive_field * dA[b, c_out, h, w]

                        # Input gradients
                        dX_padded[b, :, h_start:h_end, w_start:w_end] += \
                            self.kernels[c_out] * dA[b, c_out, h, w]

                # Bias gradients
                self.dbiases[c_out] += np.sum(dA[b, c_out])

        # Remove padding from input gradients
        if self.padding > 0:
            dX = dX_padded[:, :, self.padding:-self.padding, self.padding:-self.padding]
        else:
            dX = dX_padded

        return dX

    def update_parameters(self, learning_rate: float):
        """Update kernels and biases"""
        self.kernels -= learning_rate * self.dkernels
        self.biases -= learning_rate * self.dbiases


class MaxPoolingLayer(Layer):
    """Max Pooling layer"""

    def __init__(self, pool_size: int = 2, stride: int = 2):
        self.pool_size = pool_size
        self.stride = stride
        self.mask = None

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Forward pass through max pooling layer"""
        batch_size, channels, height, width = X.shape

        output_height = (height - self.pool_size) // self.stride + 1
        output_width = (width - self.pool_size) // self.stride + 1

        output = np.zeros((batch_size, channels, output_height, output_width))
        self.mask = np.zeros_like(X)

        for b in range(batch_size):
            for c in range(channels):
                for h in range(output_height):
                    for w in range(output_width):
                        h_start = h * self.stride
                        h_end = h_start + self.pool_size
                        w_start = w * self.stride
                        w_end = w_start + self.pool_size

                        receptive_field = X[b, c, h_start:h_end, w_start:w_end]
                        max_val = np.max(receptive_field)
                        output[b, c, h, w] = max_val

                        # Store mask for backprop
                        mask = (receptive_field == max_val)
                        self.mask[b, c, h_start:h_end, w_start:w_end] = mask

        return output

    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Backward pass through max pooling layer"""
        batch_size, channels, output_height, output_width = dA.shape

        dX = np.zeros_like(self.mask)

        for b in range(batch_size):
            for c in range(channels):
                for h in range(output_height):
                    for w in range(output_width):
                        h_start = h * self.stride
                        h_end = h_start + self.pool_size
                        w_start = w * self.stride
                        w_end = w_start + self.pool_size

                        dX[b, c, h_start:h_end, w_start:w_end] = \
                            self.mask[b, c, h_start:h_end, w_start:w_end] * dA[b, c, h, w]

        return dX

    def update_parameters(self, learning_rate: float):
        """No parameters to update"""
        pass


class FlattenLayer(Layer):
    """Flatten layer to convert 2D/3D tensors to 1D"""

    def __init__(self):
        self.input_shape = None

    def forward(self, X: np.ndarray) -> np.ndarray:
        """Flatten input tensor"""
        self.input_shape = X.shape
        return X.reshape(X.shape[0], -1)

    def backward(self, dA: np.ndarray) -> np.ndarray:
        """Reshape gradient back to input shape"""
        return dA.reshape(self.input_shape)

    def update_parameters(self, learning_rate: float):
        """No parameters to update"""
        pass


# Pre-built model architectures
def create_mlp_classifier(input_size: int, hidden_sizes: List[int],
                         output_size: int, dropout_rate: float = 0.0) -> NeuralNetwork:
    """Create Multi-Layer Perceptron for classification"""
    model = NeuralNetwork(learning_rate=0.01, loss='categorical_crossentropy')

    # Input layer
    model.add_layer(Dense(input_size, hidden_sizes[0], activation='relu'))

    # Hidden layers
    for i in range(1, len(hidden_sizes)):
        if dropout_rate > 0:
            model.add_layer(Dropout(dropout_rate))
        model.add_layer(Dense(hidden_sizes[i-1], hidden_sizes[i], activation='relu'))

    # Output layer
    model.add_layer(Dense(hidden_sizes[-1], output_size, activation='softmax'))

    return model


def create_mlp_regressor(input_size: int, hidden_sizes: List[int]) -> NeuralNetwork:
    """Create Multi-Layer Perceptron for regression"""
    model = NeuralNetwork(learning_rate=0.01, loss='mse')

    # Input layer
    model.add_layer(Dense(input_size, hidden_sizes[0], activation='relu'))

    # Hidden layers
    for i in range(1, len(hidden_sizes)):
        model.add_layer(Dense(hidden_sizes[i-1], hidden_sizes[i], activation='relu'))

    # Output layer
    model.add_layer(Dense(hidden_sizes[-1], 1, activation='linear'))

    return model


def create_cnn_classifier(input_shape: Tuple[int, int, int],
                         conv_layers: List[Dict], dense_layers: List[int],
                         output_size: int) -> NeuralNetwork:
    """Create Convolutional Neural Network for classification"""
    model = NeuralNetwork(learning_rate=0.01, loss='categorical_crossentropy')

    channels, height, width = input_shape
    current_channels = channels

    # Convolutional layers
    for conv_config in conv_layers:
        model.add_layer(ConvolutionalLayer(
            current_channels,
            conv_config['filters'],
            conv_config['kernel_size'],
            conv_config.get('stride', 1),
            conv_config.get('padding', 0)
        ))
        current_channels = conv_config['filters']

        if conv_config.get('pooling', False):
            model.add_layer(MaxPoolingLayer())

    # Flatten
    model.add_layer(FlattenLayer())

    # Dense layers
    flattened_size = current_channels * (height // (2 ** len([c for c in conv_layers if c.get('pooling', False)]))) ** 2

    for i, units in enumerate(dense_layers):
        model.add_layer(Dense(flattened_size if i == 0 else dense_layers[i-1],
                            units, activation='relu'))

    # Output layer
    model.add_layer(Dense(dense_layers[-1], output_size, activation='softmax'))

    return model


# Utility functions
def plot_training_history(history: Dict[str, List[float]], title: str = "Training History"):
    """Plot training and validation loss"""
    plt.figure(figsize=(10, 6))
    plt.plot(history['loss'], label='Training Loss')
    if 'val_loss' in history and history['val_loss'][0] is not None:
        plt.plot(history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()


def demonstrate_mlp_classification():
    """Demonstrate MLP on classification task"""
    print("=== MLP Classification Demo ===")

    # Generate synthetic data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=3,
                              n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train model
    model = create_mlp_classifier(input_size=20, hidden_sizes=[64, 32], output_size=3, dropout_rate=0.2)

    print("Training MLP classifier...")
    history = model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=True)

    # Evaluate
    metrics = model.evaluate(X_test, y_test)
    print("\nTest Metrics:")
    for metric, value in metrics.items():
        print(".4f")

    # Plot training history
    plot_training_history(history, "MLP Classification Training")


def demonstrate_mlp_regression():
    """Demonstrate MLP on regression task"""
    print("=== MLP Regression Demo ===")

    # Generate synthetic data
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale data
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_train_scaled = scaler_X.fit_transform(X_train)
    X_test_scaled = scaler_X.transform(X_test)
    y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).ravel()

    # Create and train model
    model = create_mlp_regressor(input_size=10, hidden_sizes=[64, 32])

    print("Training MLP regressor...")
    history = model.fit(X_train_scaled, y_train_scaled, epochs=100, batch_size=32, verbose=True)

    # Evaluate
    y_pred_scaled = model.predict(X_test_scaled)
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\nTest MSE: {mse:.4f}")
    print(f"Test R²: {r2:.4f}")

    # Plot training history
    plot_training_history(history, "MLP Regression Training")


def demonstrate_cnn():
    """Demonstrate CNN on image classification"""
    print("=== CNN Demo ===")

    # Create simple synthetic image data (for demonstration)
    # In practice, you'd use real image datasets like MNIST, CIFAR-10, etc.
    np.random.seed(42)

    # Simulate 32x32 RGB images
    n_samples = 1000
    n_classes = 10
    X = np.random.randn(n_samples, 3, 32, 32)  # (batch, channels, height, width)
    y = np.random.randint(0, n_classes, n_samples)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define CNN architecture
    conv_layers = [
        {'filters': 32, 'kernel_size': 3, 'padding': 1, 'pooling': True},
        {'filters': 64, 'kernel_size': 3, 'padding': 1, 'pooling': True}
    ]

    model = create_cnn_classifier(
        input_shape=(3, 32, 32),
        conv_layers=conv_layers,
        dense_layers=[128, 64],
        output_size=n_classes
    )

    print("Training CNN...")
    # Note: This is a simplified demo. Real CNN training would require more data and computation
    history = model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=True)

    print("CNN training completed (simplified demo)")


if __name__ == "__main__":
    demonstrate_mlp_classification()
    demonstrate_mlp_regression()
    demonstrate_cnn()