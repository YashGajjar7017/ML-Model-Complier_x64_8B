"""
Random Forest Regression Model Implementation
Implements ensemble learning with decision trees for regression tasks
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DecisionTreeRegressorCustom:
    """
    Custom implementation of decision tree regressor
    """

    def __init__(self, max_depth: int = None, min_samples_split: int = 2,
                 min_samples_leaf: int = 1, max_features: Optional[int] = None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.tree = None
        self.feature_importance = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'DecisionTreeRegressorCustom':
        """Fit the decision tree"""
        self.n_features = X.shape[1]
        if self.max_features is None:
            self.max_features = self.n_features

        self.tree = self._build_tree(X, y, depth=0)
        self._calculate_feature_importance()
        return self

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int) -> Dict:
        """Recursively build the decision tree"""
        n_samples, n_features = X.shape

        # Stopping criteria
        if (self.max_depth is not None and depth >= self.max_depth) or \
           n_samples < self.min_samples_split or \
           np.all(y == y[0]):
            return {'value': np.mean(y), 'samples': n_samples}

        # Find best split
        best_split = self._find_best_split(X, y)

        if best_split['variance_reduction'] == 0:
            return {'value': np.mean(y), 'samples': n_samples}

        # Create child nodes
        left_indices = X[:, best_split['feature']] <= best_split['threshold']
        right_indices = ~left_indices

        left_tree = self._build_tree(X[left_indices], y[left_indices], depth + 1)
        right_tree = self._build_tree(X[right_indices], y[right_indices], depth + 1)

        return {
            'feature': best_split['feature'],
            'threshold': best_split['threshold'],
            'left': left_tree,
            'right': right_tree,
            'variance_reduction': best_split['variance_reduction'],
            'samples': n_samples,
            'value': np.mean(y)
        }

    def _find_best_split(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Find the best feature and threshold to split on"""
        best_split = {
            'feature': None,
            'threshold': None,
            'variance_reduction': 0
        }

        current_variance = np.var(y) * len(y)

        # Randomly select subset of features
        feature_indices = np.random.choice(self.n_features,
                                         size=min(self.max_features, self.n_features),
                                         replace=False)

        for feature_idx in feature_indices:
            feature_values = X[:, feature_idx]
            unique_values = np.unique(feature_values)

            # Try different thresholds
            for threshold in unique_values:
                left_indices = feature_values <= threshold
                right_indices = ~left_indices

                if np.sum(left_indices) < self.min_samples_leaf or \
                   np.sum(right_indices) < self.min_samples_leaf:
                    continue

                left_y, right_y = y[left_indices], y[right_indices]

                # Calculate variance reduction
                left_variance = np.var(left_y) * len(left_y) if len(left_y) > 0 else 0
                right_variance = np.var(right_y) * len(right_y) if len(right_y) > 0 else 0
                total_variance = left_variance + right_variance

                variance_reduction = current_variance - total_variance

                if variance_reduction > best_split['variance_reduction']:
                    best_split = {
                        'feature': feature_idx,
                        'threshold': threshold,
                        'variance_reduction': variance_reduction
                    }

        return best_split

    def _calculate_feature_importance(self):
        """Calculate feature importance based on variance reduction"""
        self.feature_importance = np.zeros(self.n_features)
        self._traverse_tree(self.tree)

    def _traverse_tree(self, node: Dict):
        """Traverse tree to accumulate feature importance"""
        if 'feature' in node:
            self.feature_importance[node['feature']] += node.get('variance_reduction', 0)
            self._traverse_tree(node['left'])
            self._traverse_tree(node['right'])

    def predict_sample(self, x: np.ndarray, node: Dict) -> float:
        """Predict for a single sample"""
        if 'value' in node:
            return node['value']

        if x[node['feature']] <= node['threshold']:
            return self.predict_sample(x, node['left'])
        else:
            return self.predict_sample(x, node['right'])

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict for multiple samples"""
        return np.array([self.predict_sample(x, self.tree) for x in X])


class RandomForestRegressorCustom:
    """
    Custom implementation of Random Forest Regressor
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = None,
                 min_samples_split: int = 2, min_samples_leaf: int = 1,
                 max_features: str = 'auto', bootstrap: bool = True,
                 random_state: int = None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.bootstrap = bootstrap
        self.random_state = random_state

        self.trees = []
        self.feature_importances = None
        self.is_fitted = False

        if random_state:
            np.random.seed(random_state)

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'RandomForestRegressorCustom':
        """Fit the random forest"""
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X, y = np.array(X), np.array(y)

        self.trees = []
        self.feature_importances = np.zeros(X.shape[1])

        for i in range(self.n_estimators):
            # Bootstrap sampling
            if self.bootstrap:
                indices = np.random.choice(X.shape[0], size=X.shape[0], replace=True)
                X_bootstrap = X[indices]
                y_bootstrap = y[indices]
            else:
                X_bootstrap, y_bootstrap = X, y

            # Create and fit tree
            tree = DecisionTreeRegressorCustom(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf,
                max_features=self._get_max_features(X.shape[1])
            )

            tree.fit(X_bootstrap, y_bootstrap)
            self.trees.append(tree)

            # Accumulate feature importances
            if tree.feature_importance is not None:
                self.feature_importances += tree.feature_importance

        # Normalize feature importances
        if np.sum(self.feature_importances) > 0:
            self.feature_importances /= np.sum(self.feature_importances)

        self.is_fitted = True
        logger.info(f"Random Forest fitted with {self.n_estimators} trees")
        return self

    def _get_max_features(self, n_features: int) -> int:
        """Determine number of features to consider for each split"""
        if self.max_features == 'auto' or self.max_features == 'sqrt':
            return max(1, int(np.sqrt(n_features)))
        elif self.max_features == 'log2':
            return max(1, int(np.log2(n_features)))
        elif isinstance(self.max_features, float):
            return max(1, int(self.max_features * n_features))
        elif isinstance(self.max_features, int):
            return min(self.max_features, n_features)
        else:
            return n_features

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        # Get predictions from all trees
        tree_predictions = np.array([tree.predict(X) for tree in self.trees])

        # Average predictions
        return np.mean(tree_predictions, axis=0)

    def predict_with_uncertainty(self, X: Union[np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimation

        Returns:
            Tuple of (predictions, standard_deviations)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        # Get predictions from all trees
        tree_predictions = np.array([tree.predict(X) for tree in self.trees])

        # Calculate mean and standard deviation
        predictions = np.mean(tree_predictions, axis=0)
        uncertainties = np.std(tree_predictions, axis=0)

        return predictions, uncertainties

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
        elif metric == 'mae':
            return mean_absolute_error(y_true, y_pred)
        elif metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores"""
        if not self.is_fitted or self.feature_importances is None:
            return None

        if hasattr(self, 'feature_names'):
            return dict(zip(self.feature_names, self.feature_importances))
        else:
            return {f'feature_{i}': imp for i, imp in enumerate(self.feature_importances)}

    def cross_validate(self, X: Union[np.ndarray, pd.DataFrame],
                      y: Union[np.ndarray, pd.Series],
                      cv: int = 5, scoring: str = 'r2') -> np.ndarray:
        """Perform cross-validation"""
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        # Simple k-fold cross-validation implementation
        n_samples = len(X)
        fold_size = n_samples // cv
        scores = []

        indices = np.random.permutation(n_samples)

        for fold in range(cv):
            # Create train/test split
            test_start = fold * fold_size
            test_end = (fold + 1) * fold_size if fold < cv - 1 else n_samples

            test_indices = indices[test_start:test_end]
            train_indices = np.concatenate([indices[:test_start], indices[test_end:]])

            X_train, X_test = X[train_indices], X[test_indices]
            y_train, y_test = y[train_indices], y[test_indices]

            # Fit and score
            self.fit(X_train, y_train)
            score = self.score(X_test, y_test, scoring)
            scores.append(score)

        return np.array(scores)

    def plot_feature_importance(self, top_n: int = 10, save_path: Optional[str] = None):
        """Plot feature importance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting")

        importance_dict = self.get_feature_importance()
        if not importance_dict:
            logger.warning("No feature importance available")
            return

        # Sort features by importance
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:top_n]

        features, importances = zip(*top_features)

        plt.figure(figsize=(10, 6))
        plt.barh(range(len(features)), importances)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Importance')
        plt.title(f'Top {top_n} Feature Importances')
        plt.gca().invert_yaxis()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to {save_path}")
        else:
            plt.show()

    def summary(self) -> Dict[str, Any]:
        """Get model summary"""
        if not self.is_fitted:
            return {"status": "Model not fitted"}

        summary = {
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "bootstrap": self.bootstrap,
            "feature_importance": self.get_feature_importance(),
            "n_trees": len(self.trees)
        }

        return summary


class RandomForestRegressorSklearn:
    """
    Wrapper for scikit-learn's RandomForestRegressor with additional functionality
    """

    def __init__(self, **kwargs):
        self.model = RandomForestRegressor(**kwargs)
        self.is_fitted = False
        self.feature_names = None

    def fit(self, X: Union[np.ndarray, pd.DataFrame],
            y: Union[np.ndarray, pd.Series]) -> 'RandomForestRegressorSklearn':
        """Fit the model"""
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Make predictions"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        return self.model.predict(X)

    def predict_with_uncertainty(self, X: Union[np.ndarray, pd.DataFrame]) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions with uncertainty using tree variance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        # Get predictions from all trees
        tree_predictions = np.array([tree.predict(X) for tree in self.model.estimators_])

        predictions = np.mean(tree_predictions, axis=0)
        uncertainties = np.std(tree_predictions, axis=0)

        return predictions, uncertainties

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
        elif metric == 'mae':
            return mean_absolute_error(y_true, y_pred)
        elif metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        else:
            raise ValueError(f"Unknown metric: {metric}")

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores"""
        if not self.is_fitted:
            return None

        if self.feature_names:
            return dict(zip(self.feature_names, self.model.feature_importances_))
        else:
            return {f'feature_{i}': imp for i, imp in enumerate(self.model.feature_importances_)}

    def plot_feature_importance(self, top_n: int = 10, save_path: Optional[str] = None):
        """Plot feature importance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting")

        importance_dict = self.get_feature_importance()
        if not importance_dict:
            logger.warning("No feature importance available")
            return

        # Sort features by importance
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        top_features = sorted_features[:top_n]

        features, importances = zip(*top_features)

        plt.figure(figsize=(10, 6))
        plt.barh(range(len(features)), importances)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Importance')
        plt.title(f'Top {top_n} Feature Importances')
        plt.gca().invert_yaxis()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to {save_path}")
        else:
            plt.show()


# Example usage and testing functions
def create_sample_data(n_samples: int = 1000, n_features: int = 10, noise: float = 0.1):
    """Create sample regression data with non-linear relationships"""
    np.random.seed(42)
    X = np.random.randn(n_samples, n_features)

    # Non-linear relationship
    y = (X[:, 0] ** 2 + np.sin(X[:, 1]) * 2 + X[:, 2] * X[:, 3] +
         0.5 * np.random.randn(n_samples) * noise)

    return X, y


def demonstrate_random_forest():
    """Demonstrate random forest regression usage"""
    print("=== Random Forest Regression Demonstration ===")

    # Create sample data
    X, y = create_sample_data(n_samples=1000, n_features=5)

    # Custom implementation
    print("Custom Random Forest:")
    rf_custom = RandomForestRegressorCustom(
        n_estimators=50, max_depth=10, random_state=42
    )
    rf_custom.fit(X, y)

    print(".4f")
    print(".4f")
    print(".4f")

    # Feature importance
    importance = rf_custom.get_feature_importance()
    print("Top 3 features:")
    sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feature, imp in sorted_imp[:3]:
        print(".4f")

    print()

    # Scikit-learn implementation
    print("Scikit-learn Random Forest:")
    rf_sklearn = RandomForestRegressorSklearn(
        n_estimators=50, max_depth=10, random_state=42
    )
    rf_sklearn.fit(X, y)

    print(".4f")
    print(".4f")
    print(".4f")

    # Cross-validation
    print("\nCross-validation scores:")
    cv_scores = rf_custom.cross_validate(X, y, cv=3)
    print(f"CV R² Scores: {cv_scores}")
    print(".4f")


if __name__ == "__main__":
    demonstrate_random_forest()
