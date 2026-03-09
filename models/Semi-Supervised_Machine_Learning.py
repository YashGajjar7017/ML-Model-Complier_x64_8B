"""
Semi-Supervised Machine Learning Models
Implementation of algorithms that use both labeled and unlabeled data
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any
import matplotlib.pyplot as plt
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
from scipy.spatial.distance import cdist, pdist
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
import logging
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class LabelPropagationCustom:
    """
    Custom implementation of Label Propagation algorithm
    """

    def __init__(self, kernel: str = 'rbf', gamma: float = 20,
                 max_iter: int = 1000, tol: float = 1e-3):
        self.kernel = kernel
        self.gamma = gamma
        self.max_iter = max_iter
        self.tol = tol
        self.label_distributions_ = None
        self.transduction_ = None
        self.is_fitted = False

    def _compute_affinity_matrix(self, X: np.ndarray) -> np.ndarray:
        """Compute affinity matrix using specified kernel"""
        if self.kernel == 'rbf':
            # RBF kernel
            distances = cdist(X, X, 'euclidean')
            return np.exp(-self.gamma * distances ** 2)
        elif self.kernel == 'knn':
            # K-nearest neighbors kernel
            distances = cdist(X, X, 'euclidean')
            n_samples = X.shape[0]
            affinity = np.zeros((n_samples, n_samples))

            # For each point, connect to k nearest neighbors
            k = min(10, n_samples - 1)  # Default k
            for i in range(n_samples):
                indices = np.argsort(distances[i])[:k+1]  # +1 to include self
                affinity[i, indices] = 1
                affinity[indices, i] = 1

            return affinity
        else:
            raise ValueError(f"Unknown kernel: {self.kernel}")

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'LabelPropagationCustom':
        """Fit label propagation model"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y)

        n_samples = X.shape[0]
        n_classes = len(np.unique(y[y != -1]))  # Exclude unlabeled (-1)

        # Create affinity matrix
        W = self._compute_affinity_matrix(X)

        # Create degree matrix
        D = np.diag(np.sum(W, axis=1))

        # Create label matrix Y (one-hot encoded)
        Y = np.zeros((n_samples, n_classes))
        labeled_indices = y != -1

        for i, label in enumerate(y):
            if label != -1:
                Y[i, int(label)] = 1

        # Label propagation algorithm
        F = Y.copy()  # Label distribution matrix
        F_prev = F.copy()

        for iteration in range(self.max_iter):
            # Propagation step: F = D^(-1) * W * F
            F = np.linalg.solve(D, W @ F)

            # Clamp labeled points
            F[labeled_indices] = Y[labeled_indices]

            # Check convergence
            if np.max(np.abs(F - F_prev)) < self.tol:
                logger.info(f"Converged after {iteration + 1} iterations")
                break

            F_prev = F.copy()

        self.label_distributions_ = F
        self.transduction_ = np.argmax(F, axis=1)
        self.is_fitted = True

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict labels for new data points"""
        logger.warning("Label propagation doesn't support prediction on completely new data")
        logger.warning("Use fit with partially labeled data instead")
        return np.array([])

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame] = None) -> np.ndarray:
        """Get label probability distributions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return self.label_distributions_


class SelfTrainingClassifier:
    """
    Self-training classifier that iteratively labels unlabeled data
    """

    def __init__(self, base_classifier, threshold: float = 0.8,
                 max_iter: int = 10, verbose: bool = False):
        self.base_classifier = base_classifier
        self.threshold = threshold
        self.max_iter = max_iter
        self.verbose = verbose
        self.is_fitted = False
        self.labeled_indices_ = None
        self.confidence_scores_ = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'SelfTrainingClassifier':
        """Fit self-training classifier"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y)

        # Identify labeled and unlabeled data
        labeled_mask = y != -1
        self.labeled_indices_ = np.where(labeled_mask)[0]

        X_labeled = X[labeled_mask]
        y_labeled = y[labeled_mask]
        X_unlabeled = X[~labeled_mask]

        # Initial training on labeled data
        self.base_classifier.fit(X_labeled, y_labeled)

        for iteration in range(self.max_iter):
            if len(X_unlabeled) == 0:
                break

            # Predict on unlabeled data
            if hasattr(self.base_classifier, 'predict_proba'):
                probabilities = self.base_classifier.predict_proba(X_unlabeled)
                max_probs = np.max(probabilities, axis=1)
                predictions = np.argmax(probabilities, axis=1)
            else:
                predictions = self.base_classifier.predict(X_unlabeled)
                max_probs = np.ones(len(predictions))  # Assume confidence = 1

            # Select high-confidence predictions
            confident_mask = max_probs >= self.threshold
            if not np.any(confident_mask):
                if self.verbose:
                    print(f"No confident predictions in iteration {iteration}")
                break

            # Add confident predictions to labeled set
            X_confident = X_unlabeled[confident_mask]
            y_confident = predictions[confident_mask]

            X_labeled = np.vstack([X_labeled, X_confident])
            y_labeled = np.concatenate([y_labeled, y_confident])

            # Remove confident samples from unlabeled set
            X_unlabeled = X_unlabeled[~confident_mask]

            # Retrain classifier
            self.base_classifier.fit(X_labeled, y_labeled)

            if self.verbose:
                print(f"Iteration {iteration}: Added {len(X_confident)} new labels, "
                      f"{len(X_unlabeled)} unlabeled remaining")

        # Final training on all confidently labeled data
        self.base_classifier.fit(X_labeled, y_labeled)
        self.confidence_scores_ = max_probs if 'max_probs' in locals() else None
        self.is_fitted = True

        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return self.base_classifier.predict(X)

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if hasattr(self.base_classifier, 'predict_proba'):
            return self.base_classifier.predict_proba(X)
        else:
            raise AttributeError("Base classifier doesn't support predict_proba")

    def score(self, X: Union[np.ndarray, pd.DataFrame],
              y: Union[np.ndarray, pd.Series]) -> float:
        """Calculate accuracy score"""
        y_pred = self.predict(X)
        y_true = y.values if isinstance(y, pd.Series) else np.array(y)
        return accuracy_score(y_true, y_pred)


class CoTrainingClassifier:
    """
    Co-training classifier that uses two different views/features
    """

    def __init__(self, classifier1, classifier2, p: int = 1, n: int = 3,
                 k: int = 30, u: int = 75):
        self.classifier1 = classifier1
        self.classifier2 = classifier2
        self.p = p  # Number of positive examples to add per iteration
        self.n = n  # Number of negative examples to add per iteration
        self.k = k  # Initial number of labeled examples
        self.u = u  # Size of pool of unlabeled examples
        self.is_fitted = False

    def fit(self, X1: Union[np.ndarray, pd.DataFrame],
            X2: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'CoTrainingClassifier':
        """Fit co-training classifier"""
        if isinstance(X1, pd.DataFrame):
            X1 = X1.values
        if isinstance(X2, pd.DataFrame):
            X2 = X2.values
        if isinstance(y, pd.Series):
            y = y.values

        X1, X2, y = np.array(X1), np.array(X2), np.array(y)

        # Separate labeled and unlabeled data
        labeled_mask = y != -1
        unlabeled_mask = ~labeled_mask

        # Start with small labeled set
        n_classes = len(np.unique(y[labeled_mask]))
        labeled_indices = np.where(labeled_mask)[0][:self.k]

        # Initialize training sets
        X1_labeled = X1[labeled_indices]
        X2_labeled = X2[labeled_indices]
        y_labeled = y[labeled_indices]

        X1_unlabeled = X1[unlabeled_mask]
        X2_unlabeled = X2[unlabeled_mask]

        # Initial training
        self.classifier1.fit(X1_labeled, y_labeled)
        self.classifier2.fit(X2_labeled, y_labeled)

        iteration = 0
        while len(X1_unlabeled) > 0 and iteration < 10:  # Max iterations
            iteration += 1

            # Get predictions from both classifiers
            if hasattr(self.classifier1, 'predict_proba'):
                prob1 = self.classifier1.predict_proba(X1_unlabeled)
                conf1 = np.max(prob1, axis=1)
                pred1 = np.argmax(prob1, axis=1)
            else:
                pred1 = self.classifier1.predict(X1_unlabeled)
                conf1 = np.ones(len(pred1))

            if hasattr(self.classifier2, 'predict_proba'):
                prob2 = self.classifier2.predict_proba(X2_unlabeled)
                conf2 = np.max(prob2, axis=1)
                pred2 = np.argmax(prob2, axis=1)
            else:
                pred2 = self.classifier2.predict(X2_unlabeled)
                conf2 = np.ones(len(pred2))

            # Find most confident predictions that agree
            agree_mask = (pred1 == pred2) & (conf1 >= 0.8) & (conf2 >= 0.8)

            if not np.any(agree_mask):
                break

            # Add to labeled set
            agreed_indices = np.where(agree_mask)[0][:self.p + self.n]
            X1_to_add = X1_unlabeled[agreed_indices]
            X2_to_add = X2_unlabeled[agreed_indices]
            y_to_add = pred1[agreed_indices]

            X1_labeled = np.vstack([X1_labeled, X1_to_add])
            X2_labeled = np.vstack([X2_labeled, X2_to_add])
            y_labeled = np.concatenate([y_labeled, y_to_add])

            # Remove from unlabeled set
            X1_unlabeled = np.delete(X1_unlabeled, agreed_indices, axis=0)
            X2_unlabeled = np.delete(X2_unlabeled, agreed_indices, axis=0)

            # Retrain classifiers
            self.classifier1.fit(X1_labeled, y_labeled)
            self.classifier2.fit(X2_labeled, y_labeled)

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions using first classifier"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        return self.classifier1.predict(X)

    def predict_with_both(self, X1: Union[np.ndarray, pd.DataFrame],
                         X2: Union[np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with both classifiers"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        pred1 = self.classifier1.predict(X1)
        pred2 = self.classifier2.predict(X2)

        return pred1, pred2


class TransductiveSVM:
    """
    Transductive Support Vector Machine for semi-supervised learning
    """

    def __init__(self, C: float = 1.0, C_star: float = 0.1,
                 kernel: str = 'linear', max_iter: int = 100):
        self.C = C  # Penalty for labeled examples
        self.C_star = C_star  # Penalty for unlabeled examples
        self.kernel = kernel
        self.max_iter = max_iter
        self.alpha = None
        self.b = 0
        self.support_vectors = None
        self.support_vector_labels = None
        self.is_fitted = False

    def _kernel_function(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Compute kernel function"""
        if self.kernel == 'linear':
            return np.dot(x1, x2)
        elif self.kernel == 'rbf':
            gamma = 1.0  # Default gamma
            return np.exp(-gamma * np.sum((x1 - x2) ** 2))
        else:
            raise ValueError(f"Unknown kernel: {self.kernel}")

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'TransductiveSVM':
        """Fit Transductive SVM"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = np.array(X)
        y = np.array(y)

        n_samples = X.shape[0]

        # Separate labeled and unlabeled data
        labeled_mask = y != -1
        unlabeled_mask = ~labeled_mask

        X_labeled = X[labeled_mask]
        y_labeled = y[labeled_mask]
        X_unlabeled = X[unlabeled_mask]

        n_labeled = len(X_labeled)
        n_unlabeled = len(X_unlabeled)

        # Initialize labels for unlabeled data (random)
        y_unlabeled = np.random.choice([-1, 1], n_unlabeled)

        # Combine all data
        X_all = np.vstack([X_labeled, X_unlabeled])
        y_all = np.concatenate([y_labeled, y_unlabeled])

        # Initialize alpha
        alpha = np.zeros(n_samples)

        # Simplified SMO-like algorithm for transductive SVM
        for iteration in range(self.max_iter):
            alpha_prev = alpha.copy()

            for i in range(n_samples):
                # Select random j != i
                j = np.random.randint(n_samples)
                while j == i:
                    j = np.random.randint(n_samples)

                # Compute kernel values
                K_ii = self._kernel_function(X_all[i], X_all[i])
                K_ij = self._kernel_function(X_all[i], X_all[j])
                K_jj = self._kernel_function(X_all[j], X_all[j])

                # Compute eta
                eta = 2 * K_ij - K_ii - K_jj
                if eta >= 0:
                    continue

                # Compute new alpha values
                alpha_i_old, alpha_j_old = alpha[i], alpha[j]

                # Compute L and H bounds
                if y_all[i] != y_all[j]:
                    L = max(0, alpha[j] - alpha[i])
                    H = min(self.C, self.C + alpha[j] - alpha[i]) if i < n_labeled else min(self.C_star, self.C_star + alpha[j] - alpha[i])
                else:
                    L = max(0, alpha[i] + alpha[j] - (self.C if i < n_labeled else self.C_star))
                    H = min(self.C if i < n_labeled else self.C_star, alpha[i] + alpha[j])

                if L == H:
                    continue

                # Update alpha_j
                alpha[j] = alpha_j_old - (y_all[j] * (self._compute_error(i, X_all, y_all, alpha) -
                                                    self._compute_error(j, X_all, y_all, alpha))) / eta

                # Clip alpha_j
                alpha[j] = max(L, min(H, alpha[j]))

                # Update alpha_i
                alpha[i] = alpha_i_old + y_all[i] * y_all[j] * (alpha_j_old - alpha[j])

            # Check convergence
            if np.linalg.norm(alpha - alpha_prev) < 1e-5:
                break

        self.alpha = alpha
        self.support_vectors = X_all[alpha > 1e-5]
        self.support_vector_labels = y_all[alpha > 1e-5]
        self.alpha_support = alpha[alpha > 1e-5]

        # Compute bias term
        self.b = self._compute_bias(X_all, y_all)

        self.is_fitted = True
        return self

    def _compute_error(self, i: int, X: np.ndarray, y: np.ndarray, alpha: np.ndarray) -> float:
        """Compute error for sample i"""
        prediction = sum(alpha[j] * y[j] * self._kernel_function(X[i], X[j])
                        for j in range(len(X)))
        return prediction - y[i]

    def _compute_bias(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute bias term"""
        if len(self.alpha_support) == 0:
            return 0

        b_values = []
        for i in range(len(self.support_vectors)):
            prediction = sum(self.alpha_support[j] * self.support_vector_labels[j] *
                           self._kernel_function(self.support_vectors[i], self.support_vectors[j])
                           for j in range(len(self.support_vectors)))
            b_values.append(self.support_vector_labels[i] - prediction)

        return np.mean(b_values)

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        predictions = []
        for x in X:
            prediction = sum(self.alpha_support[i] * self.support_vector_labels[i] *
                           self._kernel_function(x, self.support_vectors[i])
                           for i in range(len(self.support_vectors))) + self.b
            predictions.append(np.sign(prediction))

        return np.array(predictions)


# Utility functions for semi-supervised learning
def create_semi_supervised_dataset(n_samples: int = 1000, n_features: int = 2,
                                 n_classes: int = 2, labeled_ratio: float = 0.1,
                                 random_state: int = 42):
    """Create synthetic semi-supervised dataset"""
    np.random.seed(random_state)

    # Generate base data
    X = np.random.randn(n_samples, n_features)

    # Create non-linear decision boundary
    if n_classes == 2:
        y = (X[:, 0] ** 2 + X[:, 1] ** 2 > 1).astype(int)
    else:
        centers = np.random.randn(n_classes, n_features)
        distances = np.sum((X[:, np.newaxis] - centers) ** 2, axis=2)
        y = np.argmin(distances, axis=1)

    # Randomly remove labels
    n_labeled = int(n_samples * labeled_ratio)
    labeled_indices = np.random.choice(n_samples, n_labeled, replace=False)

    y_semi = y.copy()
    y_semi[~np.isin(np.arange(n_samples), labeled_indices)] = -1  # -1 for unlabeled

    return X, y, y_semi, labeled_indices


def evaluate_semi_supervised(X_test: np.ndarray, y_test: np.ndarray,
                           y_pred: np.ndarray, model_name: str = "Model") -> Dict[str, float]:
    """Evaluate semi-supervised learning performance"""
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1_score': f1_score(y_test, y_pred, average='weighted')
    }

    print(f"\n{model_name} Semi-Supervised Evaluation:")
    for metric, value in metrics.items():
        print(".4f")

    return metrics


def compare_labeled_vs_semi_supervised():
    """Compare supervised vs semi-supervised learning performance"""
    print("=== Semi-Supervised Learning Comparison ===")

    # Create dataset
    X, y_true, y_semi, labeled_indices = create_semi_supervised_dataset(
        n_samples=1000, labeled_ratio=0.1
    )

    X_train, X_test, y_train_true, y_test = train_test_split(
        X, y_true, test_size=0.2, random_state=42
    )

    # Create semi-supervised labels for training
    y_train_semi = np.full(len(y_train_true), -1)
    train_labeled_mask = np.random.choice(len(y_train_true),
                                        size=int(0.1 * len(y_train_true)),
                                        replace=False)
    y_train_semi[train_labeled_mask] = y_train_true[train_labeled_mask]

    print(f"Training set: {len(y_train_true)} samples")
    print(f"Labeled samples: {np.sum(y_train_semi != -1)}")
    print(f"Unlabeled samples: {np.sum(y_train_semi == -1)}")

    # Label Propagation
    print("\n--- Label Propagation ---")
    lp = LabelPropagationCustom()
    lp.fit(X_train, y_train_semi)
    y_pred_lp = lp.transduction_[len(X_train) - len(X_test):]  # Get test predictions
    evaluate_semi_supervised(X_test, y_test, y_pred_lp, "Label Propagation")

    # Self-Training (using a simple classifier)
    from models.Supervised_Machine_Learning import LogisticRegressionCustom

    print("\n--- Self-Training ---")
    base_classifier = LogisticRegressionCustom()
    st = SelfTrainingClassifier(base_classifier, threshold=0.8)
    st.fit(X_train, y_train_semi)
    y_pred_st = st.predict(X_test)
    evaluate_semi_supervised(X_test, y_test, y_pred_st, "Self-Training")

    # Supervised baseline (using only labeled data)
    print("\n--- Supervised Baseline ---")
    labeled_mask = y_train_semi != -1
    X_labeled = X_train[labeled_mask]
    y_labeled = y_train_semi[labeled_mask]

    baseline_classifier = LogisticRegressionCustom()
    baseline_classifier.fit(X_labeled, y_labeled)
    y_pred_baseline = baseline_classifier.predict(X_test)
    evaluate_semi_supervised(X_test, y_test, y_pred_baseline, "Supervised Baseline")


if __name__ == "__main__":
    compare_labeled_vs_semi_supervised()
