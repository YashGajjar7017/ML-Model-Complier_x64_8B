"""
Linear Regression Model Implementation
Implements various linear regression techniques for predictive modeling
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import logging

logger = logging.getLogger(__name__)


class LinearRegressionModel:
    """
    Comprehensive Linear Regression implementation with multiple approaches
    """

    def __init__(self):
        self.model = None
        self.coefficients = None
        self.intercept = None
        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series],
            method: str = 'normal_equation') -> 'LinearRegressionModel':
        """
        Fit linear regression model using specified method

        Args:
            X: Feature matrix
            y: Target vector
            method: 'normal_equation', 'gradient_descent', 'sklearn'

        Returns:
            Fitted model instance
        """
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y).reshape(-1, 1)

        if method == 'normal_equation':
            self._fit_normal_equation(X, y)
        elif method == 'gradient_descent':
            self._fit_gradient_descent(X, y)
        elif method == 'sklearn':
            self._fit_sklearn(X, y)
        else:
            raise ValueError(f"Unknown method: {method}")

        self.is_fitted = True
        logger.info(f"Linear regression fitted using {method}")
        return self

    def _fit_normal_equation(self, X: np.ndarray, y: np.ndarray):
        """Fit using normal equation: θ = (X^T * X)^(-1) * X^T * y"""
        # Add bias term (intercept)
        X_b = np.c_[np.ones((X.shape[0], 1)), X]

        try:
            # Normal equation
            theta = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
            self.intercept = theta[0][0]
            self.coefficients = theta[1:].flatten()
        except np.linalg.LinAlgError:
            logger.warning("Matrix is singular, using pseudoinverse")
            theta = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)
            self.intercept = theta[0][0]
            self.coefficients = theta[1:].flatten()

    def _fit_gradient_descent(self, X: np.ndarray, y: np.ndarray,
                            learning_rate: float = 0.01,
                            n_iterations: int = 1000,
                            tolerance: float = 1e-6):
        """Fit using gradient descent optimization"""
        m = X.shape[0]
        X_b = np.c_[np.ones((m, 1)), X]  # Add bias term
        theta = np.random.randn(X_b.shape[1], 1)

        for iteration in range(n_iterations):
            gradients = 2/m * X_b.T.dot(X_b.dot(theta) - y)
            theta_new = theta - learning_rate * gradients

            # Check for convergence
            if np.allclose(theta, theta_new, atol=tolerance):
                logger.info(f"Converged after {iteration} iterations")
                break

            theta = theta_new

        self.intercept = theta[0][0]
        self.coefficients = theta[1:].flatten()

    def _fit_sklearn(self, X: np.ndarray, y: np.ndarray):
        """Fit using scikit-learn's LinearRegression"""
        self.model = LinearRegression()
        self.model.fit(X, y.ravel())
        self.intercept = self.model.intercept_
        self.coefficients = self.model.coef_

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Make predictions using fitted model

        Args:
            X: Feature matrix

        Returns:
            Predictions array
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        if self.model is not None:  # sklearn model
            return self.model.predict(X)
        else:  # custom implementation
            # Add bias term
            X_b = np.c_[np.ones((X.shape[0], 1)), X]
            theta = np.c_[self.intercept, self.coefficients].T
            return X_b.dot(theta).flatten()

    def score(self, X: Union[np.ndarray, pd.DataFrame],
              y: Union[np.ndarray, pd.Series],
              metric: str = 'r2') -> float:
        """
        Calculate model performance score

        Args:
            X: Feature matrix
            y: True target values
            metric: 'r2', 'mse', 'mae', 'rmse'

        Returns:
            Performance score
        """
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else np.array(y)

        if metric == 'r2':
            return r2_score(y_true, y_pred)
        elif metric == 'mse':
            return mean_squared_error(y_true, y_pred)
        elif metric == 'mae':
            return mean_absolute_error(y_true, y_pred)
        elif metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def get_feature_importance(self) -> Optional[dict]:
        """
        Get feature importance (absolute coefficient values)

        Returns:
            Dictionary of feature names and their importance
        """
        if not self.is_fitted or self.coefficients is None:
            return None

        importance = np.abs(self.coefficients)

        if self.feature_names:
            return dict(zip(self.feature_names, importance))
        else:
            return {f'feature_{i}': imp for i, imp in enumerate(importance)}

    def plot_residuals(self, X: Union[np.ndarray, pd.DataFrame],
                      y: Union[np.ndarray, pd.Series],
                      save_path: Optional[str] = None):
        """
        Plot residuals to check model assumptions

        Args:
            X: Feature matrix
            y: True target values
            save_path: Path to save plot (optional)
        """
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else np.array(y)
        residuals = y_true - y_pred

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Residuals vs Fitted
        ax1.scatter(y_pred, residuals, alpha=0.5)
        ax1.axhline(y=0, color='red', linestyle='--')
        ax1.set_xlabel('Fitted values')
        ax1.set_ylabel('Residuals')
        ax1.set_title('Residuals vs Fitted')
        ax1.grid(True, alpha=0.3)

        # Q-Q plot approximation
        residuals_sorted = np.sort(residuals)
        theoretical_quantiles = np.random.normal(0, np.std(residuals), len(residuals))
        theoretical_quantiles = np.sort(theoretical_quantiles)

        ax2.scatter(theoretical_quantiles, residuals_sorted, alpha=0.5)
        ax2.plot([theoretical_quantiles.min(), theoretical_quantiles.max()],
                [theoretical_quantiles.min(), theoretical_quantiles.max()],
                color='red', linestyle='--')
        ax2.set_xlabel('Theoretical Quantiles')
        ax2.set_ylabel('Sample Quantiles')
        ax2.set_title('Q-Q Plot')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Residual plot saved to {save_path}")
        else:
            plt.show()

    def summary(self) -> dict:
        """
        Get model summary statistics

        Returns:
            Dictionary with model information
        """
        if not self.is_fitted:
            return {"status": "Model not fitted"}

        summary = {
            "intercept": self.intercept,
            "coefficients": self.coefficients.tolist() if self.coefficients is not None else None,
            "n_features": len(self.coefficients) if self.coefficients is not None else 0,
            "feature_names": self.feature_names,
            "feature_importance": self.get_feature_importance()
        }

        return summary


class PolynomialRegression:
    """
    Polynomial regression by transforming features to polynomial features
    """

    def __init__(self, degree: int = 2):
        self.degree = degree
        self.linear_model = LinearRegressionModel()

    def _create_polynomial_features(self, X: np.ndarray) -> np.ndarray:
        """Create polynomial features up to specified degree"""
        X_poly = X.copy()
        for d in range(2, self.degree + 1):
            X_poly = np.c_[X_poly, X ** d]
        return X_poly

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'PolynomialRegression':
        """Fit polynomial regression model"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_poly = self._create_polynomial_features(X)
        self.linear_model.fit(X_poly, y)
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X_poly = self._create_polynomial_features(X)
        return self.linear_model.predict(X_poly)

    def score(self, X: Union[np.ndarray, pd.DataFrame],
              y: Union[np.ndarray, pd.Series],
              metric: str = 'r2') -> float:
        """Calculate performance score"""
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else np.array(y)

        if metric == 'r2':
            return r2_score(y_true, y_pred)
        elif metric == 'mse':
            return mean_squared_error(y_true, y_pred)
        elif metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        else:
            raise ValueError(f"Unknown metric: {metric}")


class RidgeRegression:
    """
    Ridge regression (L2 regularization) implementation
    """

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.coefficients = None
        self.intercept = None
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'RidgeRegression':
        """Fit ridge regression model"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y).reshape(-1, 1)

        # Add bias term
        X_b = np.c_[np.ones((X.shape[0], 1)), X]

        # Ridge regression: θ = (X^T * X + αI)^(-1) * X^T * y
        identity = np.eye(X_b.shape[1])
        identity[0, 0] = 0  # Don't regularize intercept

        try:
            theta = np.linalg.inv(X_b.T.dot(X_b) + self.alpha * identity).dot(X_b.T).dot(y)
        except np.linalg.LinAlgError:
            theta = np.linalg.pinv(X_b.T.dot(X_b) + self.alpha * identity).dot(X_b.T).dot(y)

        self.intercept = theta[0][0]
        self.coefficients = theta[1:].flatten()
        self.is_fitted = True

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        theta = np.c_[self.intercept, self.coefficients].T

        return X_b.dot(theta).flatten()

    def score(self, X: Union[np.ndarray, pd.DataFrame],
              y: Union[np.ndarray, pd.Series],
              metric: str = 'r2') -> float:
        """Calculate performance score"""
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else np.array(y)

        if metric == 'r2':
            return r2_score(y_true, y_pred)
        elif metric == 'mse':
            return mean_squared_error(y_true, y_pred)
        elif metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        else:
            raise ValueError(f"Unknown metric: {metric}")


# Example usage and testing functions
def create_sample_data(n_samples: int = 100, n_features: int = 1, noise: float = 0.1):
    """Create sample regression data"""
    np.random.seed(42)
    X = np.random.randn(n_samples, n_features)

    # True relationship: y = 2 + 3*X + noise
    true_coef = np.array([3.0] * n_features)
    true_intercept = 2.0

    y = true_intercept + X.dot(true_coef) + noise * np.random.randn(n_samples)

    return X, y, true_coef, true_intercept


def demonstrate_linear_regression():
    """Demonstrate linear regression usage"""
    print("=== Linear Regression Demonstration ===")

    # Create sample data
    X, y, true_coef, true_intercept = create_sample_data(n_samples=100, n_features=2)

    # Fit different models
    models = {
        'Normal Equation': LinearRegressionModel().fit(X, y, method='normal_equation'),
        'Gradient Descent': LinearRegressionModel().fit(X, y, method='gradient_descent'),
        'Scikit-learn': LinearRegressionModel().fit(X, y, method='sklearn')
    }

    print(f"True coefficients: {true_coef}")
    print(f"True intercept: {true_intercept}")
    print()

    for name, model in models.items():
        print(f"{name}:")
        print(".4f")
        print(".4f")
        print(f"  R² Score: {model.score(X, y, 'r2'):.4f}")
        print(f"  Coefficients: {model.coefficients}")
        print(f"  Intercept: {model.intercept:.4f}")
        print()

    # Polynomial regression
    print("=== Polynomial Regression ===")
    X_simple = X[:, 0].reshape(-1, 1)  # Use only first feature
    y_simple = y

    poly_model = PolynomialRegression(degree=2)
    poly_model.fit(X_simple, y_simple)

    print(f"Polynomial R² Score: {poly_model.score(X_simple, y_simple):.4f}")

    # Ridge regression
    print("\n=== Ridge Regression ===")
    ridge_model = RidgeRegression(alpha=0.1)
    ridge_model.fit(X, y)

    print(f"Ridge R² Score: {ridge_model.score(X, y):.4f}")
    print(f"Ridge Coefficients: {ridge_model.coefficients}")


if __name__ == "__main__":
    demonstrate_linear_regression()
