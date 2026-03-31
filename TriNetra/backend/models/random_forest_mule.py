"""
Random Forest Classifier for Mule Account Detection
Used in the explainability/risk pipeline for mule-risk learning + SHAP explanations
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import os
from datetime import datetime

class MuleDetectionRandomForest:
    """
    Random Forest Classifier for detecting money mule accounts
    Integrates with SHAP for explainability
    """
    
    def __init__(self, n_estimators=100, max_depth=10, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            class_weight='balanced',
            n_jobs=-1
        )
        self.feature_names = [
            'transaction_velocity',
            'in_out_ratio',
            'account_age_days',
            'rapid_in_out',
            'dormant_activation',
            'high_throughput',
            'degree_centrality',
            'betweenness_centrality',
            'pagerank',
            'is_hub',
            'is_funnel',
            'multi_hop_count',
            'circular_flow_count',
            'structuring_count'
        ]
        self.is_trained = False
        self.feature_importance_ = None
    
    def prepare_features(self, data_df):
        """
        Prepare feature matrix from transaction data
        
        Args:
            data_df: DataFrame with transaction features
            
        Returns:
            X: Feature matrix
            feature_names: List of feature names
        """
        if isinstance(data_df, dict):
            # Convert dict to DataFrame
            data_df = pd.DataFrame([data_df])
        
        # Ensure all features exist
        for feature in self.feature_names:
            if feature not in data_df.columns:
                data_df[feature] = 0
        
        X = data_df[self.feature_names].values
        return X, self.feature_names
    
    def train(self, X, y, validation_split=0.2):
        """
        Train the Random Forest model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels (0: normal, 1: mule)
            validation_split: Fraction of data for validation
            
        Returns:
            metrics: Dictionary with training metrics
        """
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Get predictions
        y_pred = self.model.predict(X_val)
        y_pred_proba = self.model.predict_proba(X_val)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': self.model.score(X_val, y_val),
            'roc_auc': roc_auc_score(y_val, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_val, y_pred).tolist(),
            'classification_report': classification_report(y_val, y_pred, output_dict=True)
        }
        
        # Store feature importance
        self.feature_importance_ = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        return metrics
    
    def predict(self, X):
        """
        Predict mule probability for accounts
        
        Args:
            X: Feature matrix
            
        Returns:
            predictions: Array of predictions (0 or 1)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """
        Predict mule probability scores
        
        Args:
            X: Feature matrix
            
        Returns:
            probabilities: Array of probabilities for each class
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        return self.model.predict_proba(X)
    
    def get_mule_risk_score(self, X):
        """
        Get mule risk score (probability of being a mule)
        
        Args:
            X: Feature matrix
            
        Returns:
            scores: Array of mule risk scores (0-1)
        """
        probabilities = self.predict_proba(X)
        return probabilities[:, 1]  # Probability of class 1 (mule)
    
    def get_feature_importance(self):
        """
        Get feature importance scores
        
        Returns:
            importance: Dictionary mapping features to importance scores
        """
        if self.feature_importance_ is None:
            raise ValueError("Model must be trained to get feature importance")
        
        # Sort by importance
        sorted_importance = sorted(
            self.feature_importance_.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return dict(sorted_importance)
    
    def save_model(self, filepath):
        """
        Save trained model to disk
        
        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance_,
            'is_trained': self.is_trained,
            'saved_at': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load trained model from disk
        
        Args:
            filepath: Path to load model from
        """
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.feature_importance_ = model_data['feature_importance']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
    
    def generate_training_data(self, n_samples=1000):
        """
        Generate synthetic training data for testing
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            X: Feature matrix
            y: Labels (0: normal, 1: mule)
        """
        np.random.seed(42)
        
        # Generate normal accounts (70%)
        n_normal = int(n_samples * 0.7)
        normal_data = {
            'transaction_velocity': np.random.normal(5, 2, n_normal),
            'in_out_ratio': np.random.normal(1.0, 0.2, n_normal),
            'account_age_days': np.random.uniform(180, 1000, n_normal),
            'rapid_in_out': np.random.binomial(1, 0.1, n_normal),
            'dormant_activation': np.random.binomial(1, 0.05, n_normal),
            'high_throughput': np.random.binomial(1, 0.15, n_normal),
            'degree_centrality': np.random.normal(0.3, 0.1, n_normal),
            'betweenness_centrality': np.random.normal(0.2, 0.1, n_normal),
            'pagerank': np.random.normal(0.01, 0.005, n_normal),
            'is_hub': np.random.binomial(1, 0.1, n_normal),
            'is_funnel': np.random.binomial(1, 0.1, n_normal),
            'multi_hop_count': np.random.poisson(1, n_normal),
            'circular_flow_count': np.random.poisson(0.5, n_normal),
            'structuring_count': np.random.poisson(0.3, n_normal)
        }
        
        # Generate mule accounts (30%)
        n_mule = n_samples - n_normal
        mule_data = {
            'transaction_velocity': np.random.normal(20, 5, n_mule),
            'in_out_ratio': np.random.normal(0.95, 0.1, n_mule),
            'account_age_days': np.random.uniform(10, 180, n_mule),
            'rapid_in_out': np.random.binomial(1, 0.8, n_mule),
            'dormant_activation': np.random.binomial(1, 0.4, n_mule),
            'high_throughput': np.random.binomial(1, 0.7, n_mule),
            'degree_centrality': np.random.normal(0.6, 0.15, n_mule),
            'betweenness_centrality': np.random.normal(0.5, 0.2, n_mule),
            'pagerank': np.random.normal(0.03, 0.01, n_mule),
            'is_hub': np.random.binomial(1, 0.5, n_mule),
            'is_funnel': np.random.binomial(1, 0.6, n_mule),
            'multi_hop_count': np.random.poisson(5, n_mule),
            'circular_flow_count': np.random.poisson(3, n_mule),
            'structuring_count': np.random.poisson(4, n_mule)
        }
        
        # Combine data
        X_normal = pd.DataFrame(normal_data)[self.feature_names].values
        X_mule = pd.DataFrame(mule_data)[self.feature_names].values
        
        X = np.vstack([X_normal, X_mule])
        y = np.array([0] * n_normal + [1] * n_mule)
        
        # Shuffle
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        return X, y


if __name__ == "__main__":
    # Example usage
    print("Training Random Forest Mule Detection Model...")
    
    model = MuleDetectionRandomForest()
    
    # Generate training data
    X, y = model.generate_training_data(n_samples=1000)
    print(f"Generated {len(X)} samples")
    
    # Train model
    metrics = model.train(X, y)
    print(f"\nTraining Results:")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"ROC AUC: {metrics['roc_auc']:.3f}")
    
    # Feature importance
    print("\nTop 5 Important Features:")
    importance = model.get_feature_importance()
    for i, (feature, score) in enumerate(list(importance.items())[:5]):
        print(f"{i+1}. {feature}: {score:.3f}")
    
    # Test prediction
    X_test, _ = model.generate_training_data(n_samples=5)
    predictions = model.predict(X_test)
    probabilities = model.get_mule_risk_score(X_test)
    
    print("\nTest Predictions:")
    for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
        print(f"Account {i+1}: {'MULE' if pred == 1 else 'NORMAL'} (risk: {prob:.3f})")
