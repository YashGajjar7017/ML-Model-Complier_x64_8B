"""
Unsupervised Machine Learning Models
Comprehensive implementation of various unsupervised learning algorithms
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, List, Optional, Dict, Any
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans as SklearnKMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA as SklearnPCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
import logging
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class KMeansCustom:
    """
    Custom implementation of K-Means clustering algorithm
    """

    def __init__(self, n_clusters: int = 3, max_iter: int = 300,
                 tol: float = 1e-4, random_state: int = None,
                 init: str = 'random'):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.init = init
        self.centroids = None
        self.labels_ = None
        self.inertia_ = None
        self.n_iter_ = 0
        self.is_fitted = False

    def _initialize_centroids(self, X: np.ndarray):
        """Initialize cluster centroids"""
        if self.random_state:
            np.random.seed(self.random_state)

        n_samples, n_features = X.shape

        if self.init == 'random':
            # Random initialization
            indices = np.random.choice(n_samples, self.n_clusters, replace=False)
            self.centroids = X[indices].copy()
        elif self.init == 'k-means++':
            # K-means++ initialization
            self.centroids = self._kmeans_plus_plus_init(X)
        else:
            raise ValueError(f"Unknown initialization method: {self.init}")

    def _kmeans_plus_plus_init(self, X: np.ndarray) -> np.ndarray:
        """K-means++ initialization"""
        n_samples, n_features = X.shape
        centroids = np.zeros((self.n_clusters, n_features))

        # First centroid
        centroids[0] = X[np.random.randint(n_samples)]

        for k in range(1, self.n_clusters):
            # Compute distances to nearest existing centroid
            distances = np.min(cdist(X, centroids[:k]), axis=1)

            # Choose next centroid with probability proportional to distance squared
            probabilities = distances ** 2
            probabilities /= np.sum(probabilities)

            next_centroid_idx = np.random.choice(n_samples, p=probabilities)
            centroids[k] = X[next_centroid_idx]

        return centroids

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'KMeansCustom':
        """Fit K-means clustering"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        n_samples, n_features = X.shape

        # Initialize centroids
        self._initialize_centroids(X)

        for iteration in range(self.max_iter):
            # Assign points to nearest centroid
            distances = cdist(X, self.centroids)
            labels = np.argmin(distances, axis=1)

            # Update centroids
            new_centroids = np.zeros_like(self.centroids)
            for k in range(self.n_clusters):
                cluster_points = X[labels == k]
                if len(cluster_points) > 0:
                    new_centroids[k] = np.mean(cluster_points, axis=0)
                else:
                    # Reinitialize empty cluster
                    new_centroids[k] = X[np.random.randint(n_samples)]

            # Check for convergence
            centroid_shift = np.sum((new_centroids - self.centroids) ** 2)
            self.centroids = new_centroids

            if centroid_shift < self.tol:
                logger.info(f"Converged after {iteration + 1} iterations")
                break

        self.n_iter_ = iteration + 1

        # Final assignment
        distances = cdist(X, self.centroids)
        self.labels_ = np.argmin(distances, axis=1)

        # Compute inertia (within-cluster sum of squares)
        self.inertia_ = 0
        for k in range(self.n_clusters):
            cluster_points = X[self.labels_ == k]
            if len(cluster_points) > 0:
                self.inertia_ += np.sum((cluster_points - self.centroids[k]) ** 2)

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict cluster labels for new data"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        distances = cdist(X, self.centroids)
        return np.argmin(distances, axis=1)

    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Transform X to distances to centroids"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before transformation")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        return cdist(X, self.centroids)

    def fit_predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Fit and predict in one step"""
        self.fit(X)
        return self.labels_

    def get_cluster_centers(self) -> np.ndarray:
        """Get cluster centroids"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted")
        return self.centroids.copy()

    def plot_clusters(self, X: Union[np.ndarray, pd.DataFrame] = None,
                     save_path: Optional[str] = None):
        """Plot clusters (for 2D data)"""
        if X is None and not self.is_fitted:
            raise ValueError("Either provide X or fit the model first")

        if X is not None:
            if isinstance(X, pd.DataFrame):
                X = X.values
            X = np.array(X)

        if X.shape[1] != 2:
            logger.warning("Plotting only works for 2D data")
            return

        plt.figure(figsize=(10, 8))

        # Plot data points
        for k in range(self.n_clusters):
            cluster_points = X[self.labels_ == k]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1],
                       label=f'Cluster {k}', alpha=0.6)

        # Plot centroids
        plt.scatter(self.centroids[:, 0], self.centroids[:, 1],
                   marker='x', s=200, linewidths=3, color='red',
                   label='Centroids')

        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.title('K-Means Clustering Results')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Cluster plot saved to {save_path}")
        else:
            plt.show()


class HierarchicalClustering:
    """
    Custom implementation of Hierarchical Clustering
    """

    def __init__(self, n_clusters: int = 3, linkage_method: str = 'ward'):
        self.n_clusters = n_clusters
        self.linkage_method = linkage_method
        self.labels_ = None
        self.linkage_matrix = None
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'HierarchicalClustering':
        """Fit hierarchical clustering"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        # Compute distance matrix
        distance_matrix = pdist(X, metric='euclidean')

        # Perform hierarchical clustering
        if self.linkage_method == 'ward':
            # For ward linkage, we need squared euclidean distances
            self.linkage_matrix = linkage(distance_matrix ** 2, method='ward')
        else:
            self.linkage_matrix = linkage(distance_matrix, method=self.linkage_method)

        # Cut tree to get clusters
        self.labels_ = fcluster(self.linkage_matrix, self.n_clusters, criterion='maxclust')
        self.labels_ -= 1  # Make labels start from 0

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict cluster labels (not directly supported for new data)"""
        logger.warning("Hierarchical clustering doesn't support prediction on new data")
        logger.warning("Use fit_predict instead")
        return np.zeros(len(X))

    def fit_predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Fit and predict in one step"""
        self.fit(X)
        return self.labels_

    def plot_dendrogram(self, save_path: Optional[str] = None):
        """Plot dendrogram"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting")

        plt.figure(figsize=(12, 8))
        dendrogram(self.linkage_matrix)
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('Sample Index')
        plt.ylabel('Distance')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Dendrogram saved to {save_path}")
        else:
            plt.show()


class GaussianMixtureModel:
    """
    Custom implementation of Gaussian Mixture Model
    """

    def __init__(self, n_components: int = 3, max_iter: int = 100,
                 tol: float = 1e-3, random_state: int = None):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

        self.weights = None
        self.means = None
        self.covariances = None
        self.labels_ = None
        self.probabilities_ = None
        self.converged_ = False
        self.n_iter_ = 0
        self.log_likelihood_ = None
        self.is_fitted = False

    def _initialize_parameters(self, X: np.ndarray):
        """Initialize GMM parameters"""
        if self.random_state:
            np.random.seed(self.random_state)

        n_samples, n_features = X.shape

        # Initialize weights (equal for all components)
        self.weights = np.ones(self.n_components) / self.n_components

        # Initialize means (random samples from data)
        indices = np.random.choice(n_samples, self.n_components, replace=False)
        self.means = X[indices].copy()

        # Initialize covariances (identity matrices)
        self.covariances = np.array([np.eye(n_features)] * self.n_components)

    def _gaussian_pdf(self, X: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
        """Compute Gaussian probability density function"""
        n_features = X.shape[1]
        diff = X - mean

        # Compute determinant and inverse
        try:
            cov_inv = np.linalg.inv(cov)
            cov_det = np.linalg.det(cov)
        except np.linalg.LinAlgError:
            # Add small regularization if singular
            cov += np.eye(n_features) * 1e-6
            cov_inv = np.linalg.inv(cov)
            cov_det = np.linalg.det(cov)

        # Compute PDF
        exponent = -0.5 * np.sum(diff * np.dot(diff, cov_inv), axis=1)
        prefactor = 1 / np.sqrt((2 * np.pi) ** n_features * cov_det)

        return prefactor * np.exp(exponent)

    def _expectation_step(self, X: np.ndarray) -> np.ndarray:
        """E-step: compute responsibilities"""
        n_samples = X.shape[0]
        responsibilities = np.zeros((n_samples, self.n_components))

        for k in range(self.n_components):
            responsibilities[:, k] = (self.weights[k] *
                                    self._gaussian_pdf(X, self.means[k], self.covariances[k]))

        # Normalize responsibilities
        responsibilities_sum = np.sum(responsibilities, axis=1, keepdims=True)
        responsibilities_sum[responsibilities_sum == 0] = 1  # Avoid division by zero
        responsibilities /= responsibilities_sum

        return responsibilities

    def _maximization_step(self, X: np.ndarray, responsibilities: np.ndarray):
        """M-step: update parameters"""
        n_samples = X.shape[0]

        for k in range(self.n_components):
            resp_k = responsibilities[:, k]
            resp_sum = np.sum(resp_k)

            if resp_sum > 0:
                # Update weights
                self.weights[k] = resp_sum / n_samples

                # Update means
                self.means[k] = np.sum(resp_k[:, np.newaxis] * X, axis=0) / resp_sum

                # Update covariances
                diff = X - self.means[k]
                self.covariances[k] = np.dot(resp_k * diff.T, diff) / resp_sum

                # Ensure positive definite
                self.covariances[k] += np.eye(X.shape[1]) * 1e-6

    def _compute_log_likelihood(self, X: np.ndarray) -> float:
        """Compute log likelihood"""
        log_likelihood = 0

        for i, x in enumerate(X):
            likelihood = 0
            for k in range(self.n_components):
                likelihood += self.weights[k] * self._gaussian_pdf(
                    x.reshape(1, -1), self.means[k], self.covariances[k]
                )[0]

            if likelihood > 0:
                log_likelihood += np.log(likelihood)

        return log_likelihood

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'GaussianMixtureModel':
        """Fit Gaussian Mixture Model"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        self._initialize_parameters(X)

        prev_log_likelihood = -np.inf

        for iteration in range(self.max_iter):
            # E-step
            responsibilities = self._expectation_step(X)

            # M-step
            self._maximization_step(X, responsibilities)

            # Compute log likelihood
            log_likelihood = self._compute_log_likelihood(X)

            # Check convergence
            if abs(log_likelihood - prev_log_likelihood) < self.tol:
                self.converged_ = True
                self.n_iter_ = iteration + 1
                break

            prev_log_likelihood = log_likelihood

        self.log_likelihood_ = log_likelihood

        # Assign final labels (hard clustering)
        responsibilities = self._expectation_step(X)
        self.labels_ = np.argmax(responsibilities, axis=1)
        self.probabilities_ = responsibilities

        self.is_fitted = True
        return self

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict cluster labels"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        responsibilities = self._expectation_step(X)
        return np.argmax(responsibilities, axis=1)

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Predict cluster probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        return self._expectation_step(X)


class PrincipalComponentAnalysis:
    """
    Custom implementation of Principal Component Analysis
    """

    def __init__(self, n_components: Optional[int] = None):
        self.n_components = n_components
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.mean_ = None
        self.is_fitted = False

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> 'PrincipalComponentAnalysis':
        """Fit PCA"""
        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)

        # Center the data
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_

        # Compute covariance matrix
        covariance_matrix = np.cov(X_centered.T)

        # Compute eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        # Sort eigenvalues and eigenvectors in descending order
        sorted_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sorted_indices]
        eigenvectors = eigenvectors[:, sorted_indices]

        # Determine number of components
        if self.n_components is None:
            self.n_components = len(eigenvalues)
        else:
            self.n_components = min(self.n_components, len(eigenvalues))

        # Store components and explained variance
        self.components_ = eigenvectors[:, :self.n_components]
        self.explained_variance_ = eigenvalues[:self.n_components]
        self.explained_variance_ratio_ = self.explained_variance_ / np.sum(eigenvalues)

        self.is_fitted = True
        return self

    def transform(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Transform data to principal component space"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before transformation")

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = np.array(X)
        X_centered = X - self.mean_

        return np.dot(X_centered, self.components_)

    def fit_transform(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X_transformed: np.ndarray) -> np.ndarray:
        """Transform data back to original space"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before inverse transformation")

        return np.dot(X_transformed, self.components_.T) + self.mean_

    def plot_explained_variance(self, save_path: Optional[str] = None):
        """Plot explained variance ratio"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before plotting")

        plt.figure(figsize=(10, 6))

        # Cumulative explained variance
        cumulative_variance = np.cumsum(self.explained_variance_ratio_)

        plt.subplot(1, 2, 1)
        plt.bar(range(1, len(self.explained_variance_ratio_) + 1),
                self.explained_variance_ratio_, alpha=0.7)
        plt.xlabel('Principal Component')
        plt.ylabel('Explained Variance Ratio')
        plt.title('Individual Explained Variance')
        plt.grid(True, alpha=0.3)

        plt.subplot(1, 2, 2)
        plt.plot(range(1, len(cumulative_variance) + 1),
                cumulative_variance, 'ro-', alpha=0.7)
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance')
        plt.title('Cumulative Explained Variance')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Variance plot saved to {save_path}")
        else:
            plt.show()


# Utility functions for unsupervised learning
def evaluate_clustering(X: np.ndarray, labels: np.ndarray,
                       model_name: str = "Model") -> Dict[str, float]:
    """Evaluate clustering performance"""
    try:
        silhouette = silhouette_score(X, labels)
    except:
        silhouette = None

    try:
        ch_score = calinski_harabasz_score(X, labels)
    except:
        ch_score = None

    try:
        db_score = davies_bouldin_score(X, labels)
    except:
        db_score = None

    metrics = {
        'silhouette_score': silhouette,
        'calinski_harabasz_score': ch_score,
        'davies_bouldin_score': db_score,
        'n_clusters': len(np.unique(labels))
    }

    print(f"\n{model_name} Clustering Evaluation:")
    for metric, value in metrics.items():
        if value is not None:
            print(".4f")
        else:
            print(f"{metric}: Not available")

    return {k: v for k, v in metrics.items() if v is not None}


def find_optimal_clusters(X: np.ndarray, max_clusters: int = 10,
                         method: str = 'elbow') -> int:
    """Find optimal number of clusters"""
    inertias = []
    silhouette_scores = []

    for k in range(2, max_clusters + 1):
        kmeans = KMeansCustom(n_clusters=k, random_state=42)
        kmeans.fit(X)

        inertias.append(kmeans.inertia_)

        try:
            silhouette = silhouette_score(X, kmeans.labels_)
            silhouette_scores.append(silhouette)
        except:
            silhouette_scores.append(0)

    if method == 'elbow':
        # Simple elbow method (second derivative)
        if len(inertias) >= 3:
            # Find point where rate of decrease slows
            diffs = np.diff(inertias)
            diffs2 = np.diff(diffs)
            optimal_k = np.argmin(diffs2) + 2
        else:
            optimal_k = 3
    elif method == 'silhouette':
        optimal_k = np.argmax(silhouette_scores) + 2
    else:
        optimal_k = 3

    return optimal_k


def create_clustering_dataset(n_samples: int = 1000, n_features: int = 2,
                            n_clusters: int = 3, random_state: int = 42):
    """Create synthetic clustering dataset"""
    np.random.seed(random_state)

    # Generate cluster centers
    centers = np.random.randn(n_clusters, n_features) * 3

    X = []
    y = []

    samples_per_cluster = n_samples // n_clusters

    for i in range(n_clusters):
        # Generate points around each center
        cluster_points = np.random.randn(samples_per_cluster, n_features) * 0.5 + centers[i]
        X.extend(cluster_points)
        y.extend([i] * samples_per_cluster)

    # Add some noise points
    noise_points = np.random.randn(n_samples // 10, n_features) * 2
    X.extend(noise_points)
    y.extend([-1] * len(noise_points))

    return np.array(X), np.array(y)


def demonstrate_unsupervised_learning():
    """Demonstrate various unsupervised learning algorithms"""
    print("=== Unsupervised Machine Learning Demonstration ===")

    # Create clustering dataset
    X, y_true = create_clustering_dataset(n_samples=600, n_features=2, n_clusters=4)

    # K-Means Clustering
    print("\n--- K-Means Clustering ---")
    kmeans = KMeansCustom(n_clusters=4, random_state=42)
    kmeans.fit(X)
    evaluate_clustering(X, kmeans.labels_, "K-Means")

    # Hierarchical Clustering
    print("\n--- Hierarchical Clustering ---")
    hc = HierarchicalClustering(n_clusters=4)
    hc.fit(X)
    evaluate_clustering(X, hc.labels_, "Hierarchical")

    # Gaussian Mixture Model
    print("\n--- Gaussian Mixture Model ---")
    gmm = GaussianMixtureModel(n_components=4, random_state=42)
    gmm.fit(X)
    evaluate_clustering(X, gmm.labels_, "GMM")

    # Principal Component Analysis
    print("\n--- Principal Component Analysis ---")
    pca = PrincipalComponentAnalysis(n_components=2)
    X_pca = pca.fit_transform(X)

    explained_var_ratio = pca.explained_variance_ratio_
    print(f"Explained variance ratio: {explained_var_ratio}")
    print(".4f")

    # Plot clusters if 2D
    if X.shape[1] == 2:
        kmeans.plot_clusters(X)


if __name__ == "__main__":
    demonstrate_unsupervised_learning()
