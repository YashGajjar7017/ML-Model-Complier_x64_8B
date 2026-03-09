"""
Supervised Machine Learning Models
Comprehensive implementation of various supervised learning algorithms
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class LogisticRegressionCustom:
    """
    Custom implementation of Logistic Regression for binary classification
    """

    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 1000,
                 regularization: str = None, lambda_param: float = 0.01):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.regularization = regularization
        self.lambda_param = lambda_param
        self.weights = None
        self.bias = None
        self.is_fitted = False

    def sigmoid(self, z: np.ndarray) -> np.ndarray:
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'LogisticRegressionCustom':
        """Fit logistic regression model using gradient descent"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y).reshape(-1, 1)

        n_samples, n_features = X.shape

        # Initialize parameters
        self.weights = np.zeros((n_features, 1))
        self.bias = 0

        # Gradient descent
        for i in range(self.n_iterations):
            # Forward pass
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)

            # Compute gradients
            dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1 / n_samples) * np.sum(y_predicted - y)

            # Add regularization
            if self.regularization == 'l2':
                dw += (self.lambda_param / n_samples) * self.weights
            elif self.regularization == 'l1':
                dw += (self.lambda_param / n_samples) * np.sign(self.weights)

            # Update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

            # Early stopping (optional)
            if i % 100 == 0:
                loss = self._compute_loss(X, y)
                if i % 500 == 0:
                    logger.debug(f"Iteration {i}, Loss: {loss:.4f}")

        self.is_fitted = True
        return self

    def _compute_loss(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute binary cross-entropy loss"""
        linear_model = np.dot(X, self.weights) + self.bias
        y_predicted = self.sigmoid(linear_model)

        # Binary cross-entropy
        loss = (-1 / len(y)) * np.sum(
            y * np.log(y_predicted + 1e-15) +
            (1 - y) * np.log(1 - y_predicted + 1e-15)
        )

        # Add regularization term
        if self.regularization == 'l2':
            loss += (self.lambda_param / (2 * len(y))) * np.sum(self.weights ** 2)
        elif self.regularization == 'l1':
            loss += (self.lambda_param / len(y)) * np.sum(np.abs(self.weights))

        return loss

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        linear_model = np.dot(X, self.weights) + self.bias
        return self.sigmoid(linear_model)

    def predict(self, X: Union[np.ndarray, pd.DataFrame],
                threshold: float = 0.5) -> np.ndarray:
        """Predict class labels"""
        probabilities = self.predict_proba(X)
        return (probabilities >= threshold).astype(int).flatten()

    def score(self, X: Union[np.ndarray, pd.DataFrame],
              y: Union[np.ndarray, pd.Series],
              metric: str = 'accuracy') -> float:
        """Calculate performance score"""
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else np.array(y)

        if metric == 'accuracy':
            return accuracy_score(y_true, y_pred)
        elif metric == 'precision':
            return precision_score(y_true, y_pred, average='weighted')
        elif metric == 'recall':
            return recall_score(y_true, y_pred, average='weighted')
        elif metric == 'f1':
            return f1_score(y_true, y_pred, average='weighted')
        else:
            raise ValueError(f"Unknown metric: {metric}")


class SupportVectorMachineCustom:
    """
    Custom implementation of Support Vector Machine
    """

    def __init__(self, learning_rate: float = 0.001, lambda_param: float = 0.01,
                 n_iterations: int = 1000):
        self.learning_rate = learning_rate
        self.lambda_param = lambda_param
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'SupportVectorMachineCustom':
        """Fit SVM using gradient descent"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y)

        # Convert labels to {-1, 1}
        y = np.where(y == 0, -1, 1)

        n_samples, n_features = X.shape

        # Initialize parameters
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Gradient descent
        for _ in range(self.n_iterations):
            for idx, x_i in enumerate(X):
                condition = y[idx] * (np.dot(x_i, self.weights) - self.bias) >= 1

                if condition:
                    # Correct classification
                    self.weights -= self.learning_rate * (2 * self.lambda_param * self.weights)
                else:
                    # Misclassification
                    self.weights -= self.learning_rate * (
                        2 * self.lambda_param * self.weights - np.dot(x_i, y[idx])
                    )
                    self.bias -= self.learning_rate * y[idx]

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        linear_output = np.dot(X, self.weights) - self.bias
        return np.sign(linear_output).astype(int)


class KNearestNeighborsCustom:
    """
    Custom implementation of K-Nearest Neighbors
    """

    def __init__(self, k: int = 5, distance_metric: str = 'euclidean'):
        self.k = k
        self.distance_metric = distance_metric
        self.X_train = None
        self.y_train = None
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'KNearestNeighborsCustom':
        """Store training data"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        self.X_train = np.array(X)
        self.y_train = np.array(y)
        self.is_fitted = True
        return self

    def _compute_distance(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Compute distance between two points"""
        if self.distance_metric == 'euclidean':
            return np.sqrt(np.sum((x1 - x2) ** 2))
        elif self.distance_metric == 'manhattan':
            return np.sum(np.abs(x1 - x2))
        elif self.distance_metric == 'cosine':
            dot_product = np.dot(x1, x2)
            norm_x1 = np.linalg.norm(x1)
            norm_x2 = np.linalg.norm(x2)
            return 1 - (dot_product / (norm_x1 * norm_x2))
        else:
            raise ValueError(f"Unknown distance metric: {self.distance_metric}")

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        predictions = []

        for x in X:
            # Compute distances to all training points
            distances = [self._compute_distance(x, x_train) for x_train in self.X_train]

            # Get k nearest neighbors
            k_indices = np.argsort(distances)[:self.k]
            k_nearest_labels = self.y_train[k_indices]

            # Majority vote
            most_common = Counter(k_nearest_labels).most_common(1)[0][0]
            predictions.append(most_common)

        return np.array(predictions)


class NaiveBayesCustom:
    """
    Custom implementation of Naive Bayes classifier
    """

    def __init__(self, smoothing: float = 1.0):
        self.smoothing = smoothing
        self.classes = None
        self.class_priors = {}
        self.feature_likelihoods = {}
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'NaiveBayesCustom':
        """Fit Naive Bayes model"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y)

        self.classes = np.unique(y)
        n_samples, n_features = X.shape

        # Calculate class priors
        for cls in self.classes:
            self.class_priors[cls] = np.sum(y == cls) / n_samples

        # Calculate feature likelihoods (assuming Gaussian distribution)
        self.feature_likelihoods = {}
        for cls in self.classes:
            X_cls = X[y == cls]
            self.feature_likelihoods[cls] = {
                'mean': np.mean(X_cls, axis=0),
                'var': np.var(X_cls, axis=0) + self.smoothing  # Add smoothing
            }

        self.is_fitted = True
        return self

    def _calculate_likelihood(self, x: np.ndarray, cls: Any) -> float:
        """Calculate likelihood of feature vector given class"""
        mean = self.feature_likelihoods[cls]['mean']
        var = self.feature_likelihoods[cls]['var']

        # Gaussian likelihood
        exponent = np.exp(-((x - mean) ** 2) / (2 * var))
        likelihood = np.prod(exponent / np.sqrt(2 * np.pi * var))

        return likelihood

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict class probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        probabilities = []

        for x in X:
            class_probs = {}
            for cls in self.classes:
                prior = self.class_priors[cls]
                likelihood = self._calculate_likelihood(x, cls)
                class_probs[cls] = prior * likelihood

            # Normalize probabilities
            total_prob = sum(class_probs.values())
            if total_prob > 0:
                class_probs = {cls: prob / total_prob for cls, prob in class_probs.items()}

            probabilities.append([class_probs[cls] for cls in self.classes])

        return np.array(probabilities)

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict class labels"""
        probabilities = self.predict_proba(X)
        return self.classes[np.argmax(probabilities, axis=1)]


class MultiLayerPerceptron:
    """
    Simple Multi-Layer Perceptron implementation
    """

    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int,
                 learning_rate: float = 0.01, n_iterations: int = 1000,
                 activation: str = 'relu'):
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.activation = activation

        self.weights = []
        self.biases = []
        self.is_fitted = False

        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize weights and biases"""
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]

        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            limit = np.sqrt(6 / (layer_sizes[i] + layer_sizes[i + 1]))
            self.weights.append(
                np.random.uniform(-limit, limit, (layer_sizes[i], layer_sizes[i + 1]))
            )
            self.biases.append(np.zeros((1, layer_sizes[i + 1])))

    def _activation_function(self, z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply activation function and return value and derivative"""
        if self.activation == 'relu':
            return np.maximum(0, z), (z > 0).astype(float)
        elif self.activation == 'sigmoid':
            sigmoid = 1 / (1 + np.exp(-np.clip(z, -500, 500)))
            return sigmoid, sigmoid * (1 - sigmoid)
        elif self.activation == 'tanh':
            tanh = np.tanh(z)
            return tanh, 1 - tanh ** 2
        else:
            raise ValueError(f"Unknown activation: {self.activation}")

    def _forward_pass(self, X: np.ndarray) -> List[np.ndarray]:
        """Forward pass through the network"""
        activations = [X]

        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            z = np.dot(activations[-1], weight) + bias

            if i < len(self.weights) - 1:  # Hidden layers
                activation, _ = self._activation_function(z)
            else:  # Output layer (no activation for regression)
                activation = z

            activations.append(activation)

        return activations

    def _backward_pass(self, activations: List[np.ndarray], y: np.ndarray):
        """Backward pass to compute gradients"""
        # Output layer error
        output_error = activations[-1] - y.reshape(-1, self.output_size)

        gradients_w = []
        gradients_b = []

        # Backpropagate through layers
        error = output_error

        for i in reversed(range(len(self.weights))):
            # Compute gradients
            dw = np.dot(activations[i].T, error) / len(y)
            db = np.sum(error, axis=0, keepdims=True) / len(y)

            gradients_w.insert(0, dw)
            gradients_b.insert(0, db)

            # Propagate error to previous layer
            if i > 0:
                _, activation_derivative = self._activation_function(
                    np.dot(activations[i], self.weights[i]) + self.biases[i]
                )
                error = np.dot(error, self.weights[i].T) * activation_derivative

        return gradients_w, gradients_b

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'MultiLayerPerceptron':
        """Fit the neural network"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y).reshape(-1, 1) if y.ndim == 1 else y

        for iteration in range(self.n_iterations):
            # Forward pass
            activations = self._forward_pass(X)

            # Backward pass
            gradients_w, gradients_b = self._backward_pass(activations, y)

            # Update weights and biases
            for i in range(len(self.weights)):
                self.weights[i] -= self.learning_rate * gradients_w[i]
                self.biases[i] -= self.learning_rate * gradients_b[i]

            # Log progress
            if iteration % 100 == 0:
                loss = np.mean((activations[-1] - y) ** 2)
                logger.debug(f"Iteration {iteration}, Loss: {loss:.4f}")

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        activations = self._forward_pass(X)
        return activations[-1]


# Utility functions for supervised learning
def evaluate_classification_model(model, X_test: np.ndarray, y_test: np.ndarray,
                                model_name: str = "Model") -> Dict[str, float]:
    """Evaluate classification model performance"""
    y_pred = model.predict(X_test)

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1_score': f1_score(y_test, y_pred, average='weighted')
    }

    print(f"\n{model_name} Performance:")
    for metric, value in metrics.items():
        print(".4f")

    return metrics


def evaluate_regression_model(model, X_test: np.ndarray, y_test: np.ndarray,
                            model_name: str = "Model") -> Dict[str, float]:
    """Evaluate regression model performance"""
    y_pred = model.predict(X_test)

    metrics = {
        'mse': mean_squared_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
        'r2_score': r2_score(y_test, y_pred)
    }

    print(f"\n{model_name} Performance:")
    for metric, value in metrics.items():
        print(".4f")

    return metrics


def create_classification_dataset(n_samples: int = 1000, n_features: int = 2,
                                n_classes: int = 2, random_state: int = 42):
    """Create synthetic classification dataset"""
    np.random.seed(random_state)
    X = np.random.randn(n_samples, n_features)

    # Create non-linear decision boundaries
    if n_classes == 2:
        y = (X[:, 0] ** 2 + X[:, 1] ** 2 > 1).astype(int)
    else:
        # Multi-class
        centers = np.random.randn(n_classes, n_features)
        y = np.argmin(np.sum((X[:, np.newaxis] - centers) ** 2, axis=2), axis=1)

    return X, y


def create_regression_dataset(n_samples: int = 1000, n_features: int = 5,
                            noise: float = 0.1, random_state: int = 42):
    """Create synthetic regression dataset"""
    np.random.seed(random_state)
    X = np.random.randn(n_samples, n_features)

    # Non-linear relationship
    y = (X[:, 0] ** 2 + np.sin(X[:, 1]) + X[:, 2] * X[:, 3] +
         noise * np.random.randn(n_samples))

    return X, y


def demonstrate_supervised_learning():
    """Demonstrate various supervised learning algorithms"""
    print("=== Supervised Machine Learning Demonstration ===")

    # Classification
    print("\n--- Classification Task ---")
    X_cls, y_cls = create_classification_dataset(n_samples=1000, n_features=2)
    X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(
        X_cls, y_cls, test_size=0.2, random_state=42
    )

    # Logistic Regression
    lr = LogisticRegressionCustom(learning_rate=0.1, n_iterations=1000)
    lr.fit(X_train_cls, y_train_cls)
    evaluate_classification_model(lr, X_test_cls, y_test_cls, "Logistic Regression")

    # KNN
    knn = KNearestNeighborsCustom(k=5)
    knn.fit(X_train_cls, y_train_cls)
    evaluate_classification_model(knn, X_test_cls, y_test_cls, "K-Nearest Neighbors")

    # Naive Bayes
    nb = NaiveBayesCustom()
    nb.fit(X_train_cls, y_train_cls)
    evaluate_classification_model(nb, X_test_cls, y_test_cls, "Naive Bayes")

    # Regression
    print("\n--- Regression Task ---")
    X_reg, y_reg = create_regression_dataset(n_samples=1000, n_features=3)
    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )

    # Neural Network
    nn = MultiLayerPerceptron(
        input_size=X_train_reg.shape[1],
        hidden_sizes=[10, 5],
        output_size=1,
        learning_rate=0.01,
        n_iterations=500
    )
    nn.fit(X_train_reg, y_train_reg)
    evaluate_regression_model(nn, X_test_reg, y_test_reg, "Neural Network")


if __name__ == "__main__":
    demonstrate_supervised_learning()
