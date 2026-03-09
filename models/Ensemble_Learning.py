"""
Ensemble Learning Models
Implementation of ensemble methods combining multiple models for better performance
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any, Callable
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score, confusion_matrix
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.datasets import make_classification, make_regression
from collections import Counter
import random
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseEnsemble(ABC):
    """Abstract base class for ensemble methods"""

    def __init__(self, n_estimators: int = 10, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.estimators = []
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'BaseEnsemble':
        """Fit the ensemble model"""
        pass

    @abstractmethod
    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        pass

    def _prepare_data(self, X: Union[np.ndarray, pd.DataFrame],
                     y: Union[np.ndarray, pd.Series]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        return np.array(X), np.array(y)


class BaggingClassifier(BaseEnsemble):
    """
    Bagging (Bootstrap Aggregating) for classification
    """

    def __init__(self, base_estimator=None, n_estimators: int = 10,
                 max_samples: float = 1.0, bootstrap: bool = True,
                 random_state: int = 42):
        super().__init__(n_estimators, random_state)
        self.base_estimator = base_estimator or DecisionTreeClassifier(random_state=random_state)
        self.max_samples = max_samples
        self.bootstrap = bootstrap
        self.classes_ = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'BaggingClassifier':
        """Fit bagging classifier"""
        X, y = self._prepare_data(X, y)

        self.classes_ = np.unique(y)
        n_samples = X.shape[0]
        sample_size = int(self.max_samples * n_samples)

        np.random.seed(self.random_state)

        for i in range(self.n_estimators):
            # Bootstrap sampling
            if self.bootstrap:
                indices = np.random.choice(n_samples, size=sample_size, replace=True)
            else:
                indices = np.random.choice(n_samples, size=sample_size, replace=False)

            X_bootstrap = X[indices]
            y_bootstrap = y[indices]

            # Train base estimator
            estimator = self._clone_estimator()
            estimator.fit(X_bootstrap, y_bootstrap)
            self.estimators.append(estimator)

        self.is_fitted = True
        return self

    def _clone_estimator(self):
        """Clone the base estimator"""
        if hasattr(self.base_estimator, 'random_state'):
            return self.base_estimator.__class__(
                **{k: v for k, v in self.base_estimator.get_params().items()
                   if k != 'random_state'},
                random_state=self.random_state
            )
        else:
            return self.base_estimator.__class__(**self.base_estimator.get_params())

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions using majority voting"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        # Get predictions from all estimators
        predictions = np.array([estimator.predict(X) for estimator in self.estimators])

        # Majority voting
        final_predictions = []
        for i in range(X.shape[0]):
            sample_predictions = predictions[:, i]
            most_common = Counter(sample_predictions).most_common(1)[0][0]
            final_predictions.append(most_common)

        return np.array(final_predictions)

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict class probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        # Get probability predictions from all estimators
        probas = np.array([estimator.predict_proba(X) for estimator in self.estimators
                          if hasattr(estimator, 'predict_proba')])

        if len(probas) == 0:
            raise AttributeError("Base estimator doesn't support predict_proba")

        # Average probabilities
        return np.mean(probas, axis=0)


class BaggingRegressor(BaseEnsemble):
    """
    Bagging (Bootstrap Aggregating) for regression
    """

    def __init__(self, base_estimator=None, n_estimators: int = 10,
                 max_samples: float = 1.0, bootstrap: bool = True,
                 random_state: int = 42):
        super().__init__(n_estimators, random_state)
        self.base_estimator = base_estimator or DecisionTreeRegressor(random_state=random_state)
        self.max_samples = max_samples
        self.bootstrap = bootstrap

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'BaggingRegressor':
        """Fit bagging regressor"""
        X, y = self._prepare_data(X, y)

        n_samples = X.shape[0]
        sample_size = int(self.max_samples * n_samples)

        np.random.seed(self.random_state)

        for i in range(self.n_estimators):
            # Bootstrap sampling
            if self.bootstrap:
                indices = np.random.choice(n_samples, size=sample_size, replace=True)
            else:
                indices = np.random.choice(n_samples, size=sample_size, replace=False)

            X_bootstrap = X[indices]
            y_bootstrap = y[indices]

            # Train base estimator
            estimator = self._clone_estimator()
            estimator.fit(X_bootstrap, y_bootstrap)
            self.estimators.append(estimator)

        self.is_fitted = True
        return self

    def _clone_estimator(self):
        """Clone the base estimator"""
        if hasattr(self.base_estimator, 'random_state'):
            return self.base_estimator.__class__(
                **{k: v for k, v in self.base_estimator.get_params().items()
                   if k != 'random_state'},
                random_state=self.random_state
            )
        else:
            return self.base_estimator.__class__(**self.base_estimator.get_params())

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions using averaging"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        # Get predictions from all estimators
        predictions = np.array([estimator.predict(X) for estimator in self.estimators])

        # Average predictions
        return np.mean(predictions, axis=0)


class AdaBoostClassifier(BaseEnsemble):
    """
    AdaBoost (Adaptive Boosting) for classification
    """

    def __init__(self, base_estimator=None, n_estimators: int = 50,
                 learning_rate: float = 1.0, random_state: int = 42):
        super().__init__(n_estimators, random_state)
        self.base_estimator = base_estimator or DecisionTreeClassifier(max_depth=1, random_state=random_state)
        self.learning_rate = learning_rate
        self.estimator_weights = []
        self.estimator_errors = []
        self.classes_ = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'AdaBoostClassifier':
        """Fit AdaBoost classifier"""
        X, y = self._prepare_data(X, y)

        # Convert labels to {-1, 1}
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("AdaBoost only supports binary classification")

        y_binary = np.where(y == self.classes_[0], -1, 1)

        n_samples = X.shape[0]
        sample_weights = np.ones(n_samples) / n_samples

        np.random.seed(self.random_state)

        for i in range(self.n_estimators):
            # Train base estimator with sample weights
            estimator = self._clone_estimator()
            estimator.fit(X, y_binary, sample_weight=sample_weights)
            self.estimators.append(estimator)

            # Get predictions
            y_pred = estimator.predict(X)

            # Calculate weighted error
            incorrect = (y_pred != y_binary)
            estimator_error = np.sum(sample_weights * incorrect) / np.sum(sample_weights)

            # Avoid division by zero
            estimator_error = np.clip(estimator_error, 1e-10, 1 - 1e-10)

            # Calculate estimator weight
            estimator_weight = self.learning_rate * 0.5 * np.log((1 - estimator_error) / estimator_error)
            self.estimator_weights.append(estimator_weight)
            self.estimator_errors.append(estimator_error)

            # Update sample weights
            sample_weights *= np.exp(-estimator_weight * y_binary * y_pred)
            sample_weights /= np.sum(sample_weights)  # Normalize

        self.is_fitted = True
        return self

    def _clone_estimator(self):
        """Clone the base estimator"""
        if hasattr(self.base_estimator, 'random_state'):
            return self.base_estimator.__class__(
                **{k: v for k, v in self.base_estimator.get_params().items()
                   if k != 'random_state'},
                random_state=self.random_state
            )
        else:
            return self.base_estimator.__class__(**self.base_estimator.get_params())

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions using weighted voting"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        # Get weighted predictions from all estimators
        weighted_predictions = np.zeros(X.shape[0])

        for estimator, weight in zip(self.estimators, self.estimator_weights):
            y_pred = estimator.predict(X)
            weighted_predictions += weight * y_pred

        # Convert back to original labels
        final_predictions = np.where(weighted_predictions >= 0, self.classes_[0], self.classes_[1])

        return final_predictions


class GradientBoostingClassifier(BaseEnsemble):
    """
    Gradient Boosting for classification
    """

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.1,
                 max_depth: int = 3, subsample: float = 1.0, random_state: int = 42):
        super().__init__(n_estimators, random_state)
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.subsample = subsample
        self.classes_ = None
        self.initial_prediction = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'GradientBoostingClassifier':
        """Fit gradient boosting classifier"""
        X, y = self._prepare_data(X, y)

        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)

        if n_classes == 2:
            # Binary classification
            y_binary = np.where(y == self.classes_[0], -1, 1)
            self._fit_binary(X, y_binary)
        else:
            # Multi-class classification (simplified)
            self._fit_multiclass(X, y)

        self.is_fitted = True
        return self

    def _fit_binary(self, X: np.ndarray, y: np.ndarray):
        """Fit for binary classification"""
        n_samples = X.shape[0]

        # Initial prediction (log-odds)
        initial_pred = np.log(np.sum(y == 1) / np.sum(y == -1))
        self.initial_prediction = initial_pred

        F = np.full(n_samples, initial_pred)  # Current predictions

        for i in range(self.n_estimators):
            # Compute pseudo-residuals
            p = 1 / (1 + np.exp(-F))  # Sigmoid
            residuals = y - p

            # Fit base learner to residuals
            if self.subsample < 1.0:
                indices = np.random.choice(n_samples, size=int(self.subsample * n_samples), replace=False)
                X_sample = X[indices]
                residuals_sample = residuals[indices]
            else:
                X_sample = X
                residuals_sample = residuals

            tree = DecisionTreeRegressor(max_depth=self.max_depth, random_state=self.random_state)
            tree.fit(X_sample, residuals_sample)
            self.estimators.append(tree)

            # Update predictions
            gamma = tree.predict(X)
            F += self.learning_rate * gamma

    def _fit_multiclass(self, X: np.ndarray, y: np.ndarray):
        """Fit for multi-class classification (simplified)"""
        # Use one-vs-rest approach
        n_classes = len(self.classes_)
        self.initial_prediction = np.zeros(n_classes)

        for class_idx in range(n_classes):
            y_binary = np.where(y == self.classes_[class_idx], 1, -1)
            self._fit_binary(X, y_binary)

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        if len(self.classes_) == 2:
            return self._predict_binary(X)
        else:
            return self._predict_multiclass(X)

    def _predict_binary(self, X: np.ndarray) -> np.ndarray:
        """Predict for binary classification"""
        F = np.full(X.shape[0], self.initial_prediction)

        for estimator in self.estimators:
            F += self.learning_rate * estimator.predict(X)

        # Convert to probabilities and then to classes
        probs = 1 / (1 + np.exp(-F))
        predictions = np.where(probs >= 0.5, self.classes_[1], self.classes_[0])

        return predictions

    def _predict_multiclass(self, X: np.ndarray) -> np.ndarray:
        """Predict for multi-class classification"""
        # Simplified: just use the last binary classifier
        return self._predict_binary(X)


class RandomForestClassifier(BaggingClassifier):
    """
    Random Forest for classification (extension of bagging with random feature selection)
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = None,
                 max_features: str = 'sqrt', bootstrap: bool = True,
                 random_state: int = 42):
        base_estimator = DecisionTreeClassifier(
            max_depth=max_depth,
            max_features=max_features,
            random_state=random_state
        )
        super().__init__(base_estimator=base_estimator, n_estimators=n_estimators,
                        bootstrap=bootstrap, random_state=random_state)
        self.max_features = max_features

    def _clone_estimator(self):
        """Clone the base estimator with random state"""
        return DecisionTreeClassifier(
            max_depth=self.base_estimator.max_depth,
            max_features=self.max_features,
            random_state=np.random.randint(10000)  # Different random state for each tree
        )


class RandomForestRegressor(BaggingRegressor):
    """
    Random Forest for regression (extension of bagging with random feature selection)
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = None,
                 max_features: str = 'sqrt', bootstrap: bool = True,
                 random_state: int = 42):
        base_estimator = DecisionTreeRegressor(
            max_depth=max_depth,
            max_features=max_features,
            random_state=random_state
        )
        super().__init__(base_estimator=base_estimator, n_estimators=n_estimators,
                        bootstrap=bootstrap, random_state=random_state)
        self.max_features = max_features

    def _clone_estimator(self):
        """Clone the base estimator with random state"""
        return DecisionTreeRegressor(
            max_depth=self.base_estimator.max_depth,
            max_features=self.max_features,
            random_state=np.random.randint(10000)  # Different random state for each tree
        )


class VotingClassifier(BaseEnsemble):
    """
    Voting classifier that combines predictions from multiple models
    """

    def __init__(self, estimators: List[Tuple[str, Any]], voting: str = 'hard'):
        super().__init__(len(estimators))
        self.estimators = estimators  # List of (name, estimator) tuples
        self.voting = voting  # 'hard' or 'soft'
        self.classes_ = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'VotingClassifier':
        """Fit voting classifier"""
        X, y = self._prepare_data(X, y)
        self.classes_ = np.unique(y)

        # Fit all estimators
        for name, estimator in self.estimators:
            estimator.fit(X, y)

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions using voting"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        if self.voting == 'hard':
            return self._predict_hard(X)
        elif self.voting == 'soft':
            return self._predict_soft(X)
        else:
            raise ValueError("Voting must be 'hard' or 'soft'")

    def _predict_hard(self, X: np.ndarray) -> np.ndarray:
        """Hard voting"""
        predictions = np.array([estimator.predict(X) for _, estimator in self.estimators])
        final_predictions = []

        for i in range(X.shape[0]):
            sample_predictions = predictions[:, i]
            most_common = Counter(sample_predictions).most_common(1)[0][0]
            final_predictions.append(most_common)

        return np.array(final_predictions)

    def _predict_soft(self, X: np.ndarray) -> np.ndarray:
        """Soft voting"""
        probas = np.array([estimator.predict_proba(X) for _, estimator in self.estimators
                          if hasattr(estimator, 'predict_proba')])

        if len(probas) == 0:
            raise AttributeError("All estimators must support predict_proba for soft voting")

        # Average probabilities
        avg_probas = np.mean(probas, axis=0)
        return self.classes_[np.argmax(avg_probas, axis=1)]


class StackingClassifier(BaseEnsemble):
    """
    Stacking classifier that uses a meta-learner to combine base model predictions
    """

    def __init__(self, base_estimators: List[Tuple[str, Any]],
                 meta_estimator=None, cv: int = 5, random_state: int = 42):
        super().__init__(len(base_estimators), random_state)
        self.base_estimators = base_estimators
        self.meta_estimator = meta_estimator or LogisticRegression(random_state=random_state)
        self.cv = cv
        self.classes_ = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'StackingClassifier':
        """Fit stacking classifier"""
        X, y = self._prepare_data(X, y)
        self.classes_ = np.unique(y)

        n_samples = X.shape[0]

        # Get cross-validated predictions from base estimators
        base_predictions = np.zeros((n_samples, len(self.base_estimators)))

        for i, (name, estimator) in enumerate(self.base_estimators):
            # Use cross-validation to get out-of-fold predictions
            cv_predictions = np.zeros(n_samples)

            for train_idx, val_idx in self._get_cv_splits(n_samples):
                estimator.fit(X[train_idx], y[train_idx])
                if hasattr(estimator, 'predict_proba'):
                    pred = estimator.predict_proba(X[val_idx])
                    if pred.shape[1] > 1:
                        cv_predictions[val_idx] = pred[:, 1]  # Probability of positive class
                    else:
                        cv_predictions[val_idx] = pred.ravel()
                else:
                    cv_predictions[val_idx] = estimator.predict(X[val_idx])

            base_predictions[:, i] = cv_predictions

        # Train meta-estimator on base predictions
        self.meta_estimator.fit(base_predictions, y)

        # Retrain base estimators on full data
        self.estimators = []
        for name, estimator in self.base_estimators:
            estimator.fit(X, y)
            self.estimators.append(estimator)

        self.is_fitted = True
        return self

    def _get_cv_splits(self, n_samples: int):
        """Generate cross-validation splits"""
        fold_size = n_samples // self.cv
        indices = np.arange(n_samples)
        np.random.shuffle(indices)

        for i in range(self.cv):
            val_start = i * fold_size
            val_end = (i + 1) * fold_size if i < self.cv - 1 else n_samples

            val_idx = indices[val_start:val_end]
            train_idx = np.concatenate([indices[:val_start], indices[val_end:]])

            yield train_idx, val_idx

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions using stacking"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values
        X = np.array(X)

        # Get predictions from base estimators
        base_predictions = np.zeros((X.shape[0], len(self.estimators)))

        for i, estimator in enumerate(self.estimators):
            if hasattr(estimator, 'predict_proba'):
                pred = estimator.predict_proba(X)
                if pred.shape[1] > 1:
                    base_predictions[:, i] = pred[:, 1]
                else:
                    base_predictions[:, i] = pred.ravel()
            else:
                base_predictions[:, i] = estimator.predict(X)

        # Get final prediction from meta-estimator
        return self.meta_estimator.predict(base_predictions)


# Utility functions
def evaluate_ensemble(model, X_test: np.ndarray, y_test: np.ndarray,
                     model_name: str = "Ensemble Model") -> Dict[str, float]:
    """Evaluate ensemble model performance"""
    y_pred = model.predict(X_test)

    if hasattr(model, 'classes_') and len(model.classes_) > 2:
        # Multi-class classification
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        }
    else:
        # Binary classification or regression
        if len(np.unique(y_test)) == 2:
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1_score': f1_score(y_test, y_pred)
            }
        else:
            # Regression
            y_pred_numeric = y_pred.astype(float)
            y_test_numeric = y_test.astype(float)
            mse = mean_squared_error(y_test_numeric, y_pred_numeric)
            r2 = r2_score(y_test_numeric, y_pred_numeric)
            metrics = {
                'mse': mse,
                'rmse': np.sqrt(mse),
                'r2_score': r2
            }

    print(f"\n{model_name} Evaluation:")
    for metric, value in metrics.items():
        print(".4f")

    return metrics


def compare_ensemble_methods():
    """Compare different ensemble methods"""
    print("=== Ensemble Methods Comparison ===")

    # Generate synthetic classification data
    X, y = make_classification(n_samples=1000, n_features=20, n_classes=2,
                              n_informative=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define base estimators
    base_estimators = [
        ('dt', DecisionTreeClassifier(random_state=42)),
        ('lr', LogisticRegression(random_state=42)),
        ('nb', GaussianNB()),
        ('knn', KNeighborsClassifier())
    ]

    # Test different ensemble methods
    ensembles = {
        'Bagging': BaggingClassifier(n_estimators=10, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=10, random_state=42),
        'AdaBoost': AdaBoostClassifier(n_estimators=10, random_state=42),
        'Voting': VotingClassifier(estimators=base_estimators, voting='hard'),
        'Stacking': StackingClassifier(base_estimators=base_estimators, random_state=42)
    }

    results = {}

    for name, model in ensembles.items():
        print(f"\n--- Training {name} ---")
        model.fit(X_train, y_train)
        results[name] = evaluate_ensemble(model, X_test, y_test, name)

    return results


def demonstrate_gradient_boosting():
    """Demonstrate gradient boosting"""
    print("=== Gradient Boosting Demo ===")

    # Generate synthetic data
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=2,
                              n_informative=8, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train gradient boosting
    gb = GradientBoostingClassifier(n_estimators=50, learning_rate=0.1, max_depth=3)
    gb.fit(X_train, y_train)

    # Evaluate
    evaluate_ensemble(gb, X_test, y_test, "Gradient Boosting")


def demonstrate_ensemble_regression():
    """Demonstrate ensemble methods for regression"""
    print("=== Ensemble Regression Demo ===")

    # Generate synthetic regression data
    X, y = make_regression(n_samples=1000, n_features=10, noise=0.1, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Test bagging and random forest regression
    models = {
        'Bagging Regressor': BaggingRegressor(n_estimators=10, random_state=42),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=10, random_state=42)
    }

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"{name} Results:")
        print(".4f")
        print(".4f")


if __name__ == "__main__":
    compare_ensemble_methods()
    demonstrate_gradient_boosting()
    demonstrate_ensemble_regression()