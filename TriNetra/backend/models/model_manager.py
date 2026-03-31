"""
Model Manager
Central hub for managing and coordinating all ML/DL models
"""

import os
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import warnings

from .random_forest_mule import MuleDetectionRandomForest
from .risk_scoring_model import RulBasedRiskScoringModel, RiskWeights
from .hydra_gan import HYDRA_GAN
from .gnn_mule_detector import GNN_MuleDetectionSystem
from .graph_analytics import GraphAnalyticsEngine
from .shap_explainer import SHAPExplainer, ExplainabilityReport

class ModelManager:
    """
    Centralized model management system
    Coordinates all ML/DL models and analytics
    """
    
    def __init__(self, model_dir: str = './saved_models'):
        """
        Initialize model manager
        
        Args:
            model_dir: Directory for saving/loading models
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.random_forest = None
        self.risk_scorer = RulBasedRiskScoringModel()
        self.hydra_gan = None
        self.gnn_detector = None
        self.graph_analytics = GraphAnalyticsEngine()
        self.shap_explainer = None
        
        # Model status
        self.models_trained = {
            'random_forest': False,
            'hydra_gan': False,
            'gnn_detector': False
        }
        
        print("ModelManager initialized")
    
    def initialize_random_forest(self, n_estimators=100, max_depth=10):
        """Initialize Random Forest model"""
        self.random_forest = MuleDetectionRandomForest(
            n_estimators=n_estimators,
            max_depth=max_depth
        )
        print("Random Forest initialized")
    
    def initialize_hydra_gan(self, latent_dim=100, pattern_dim=50, device='cpu'):
        """Initialize HYDRA GAN"""
        self.hydra_gan = HYDRA_GAN(
            latent_dim=latent_dim,
            pattern_dim=pattern_dim,
            device=device
        )
        print("HYDRA GAN initialized")
    
    def initialize_gnn(self, n_features, device='cpu'):
        """Initialize GNN detector"""
        self.gnn_detector = GNN_MuleDetectionSystem(
            n_features=n_features,
            device=device
        )
        print("GNN detector initialized")
    
    def train_random_forest(self, X, y, validation_split=0.2):
        """
        Train Random Forest model
        
        Args:
            X: Feature matrix
            y: Labels
            validation_split: Validation split ratio
            
        Returns:
            metrics: Training metrics
        """
        if self.random_forest is None:
            self.initialize_random_forest()
        
        print("Training Random Forest...")
        metrics = self.random_forest.train(X, y, validation_split)
        self.models_trained['random_forest'] = True
        
        # Initialize SHAP explainer
        self.shap_explainer = SHAPExplainer(
            self.random_forest.model,
            self.random_forest.feature_names
        )
        self.shap_explainer.fit(X, explainer_type='tree')
        
        print(f"Random Forest trained - Accuracy: {metrics['accuracy']:.3f}")
        return metrics
    
    def train_hydra_gan(self, real_patterns, epochs=100, batch_size=32):
        """
        Train HYDRA GAN
        
        Args:
            real_patterns: Real transaction patterns
            epochs: Training epochs
            batch_size: Batch size
            
        Returns:
            history: Training history
        """
        if self.hydra_gan is None:
            self.initialize_hydra_gan()
        
        print("Training HYDRA GAN...")
        history = self.hydra_gan.train(real_patterns, epochs, batch_size)
        self.models_trained['hydra_gan'] = True
        
        print(f"HYDRA GAN trained - Final G Loss: {history['g_losses'][-1]:.4f}")
        return history
    
    def train_gnn(self, X, A, y, train_mask, val_mask, epochs=200):
        """
        Train GNN detector
        
        Args:
            X: Node features
            A: Adjacency matrix
            y: Node labels
            train_mask: Training mask
            val_mask: Validation mask
            epochs: Training epochs
            
        Returns:
            history: Training history
        """
        if self.gnn_detector is None:
            self.initialize_gnn(n_features=X.shape[1])
        
        print("Training GNN detector...")
        history = self.gnn_detector.train(X, A, y, train_mask, val_mask, epochs)
        self.models_trained['gnn_detector'] = True
        
        final_acc = history['val_accuracies'][-1]
        print(f"GNN trained - Final Val Accuracy: {final_acc:.3f}")
        return history
    
    def predict_mule_risk_rf(self, features: Dict) -> Dict:
        """
        Predict mule risk using Random Forest
        
        Args:
            features: Account features dictionary
            
        Returns:
            prediction: Risk prediction with explanation
        """
        if not self.models_trained['random_forest']:
            raise ValueError("Random Forest not trained")
        
        X, _ = self.random_forest.prepare_features(features)
        
        # Prediction
        prediction = self.random_forest.predict(X)[0]
        risk_score = self.random_forest.get_mule_risk_score(X)[0]
        
        # Explanation
        explanation = None
        if self.shap_explainer:
            explanation = self.shap_explainer.explain_prediction(X)
        
        return {
            'model': 'random_forest',
            'prediction': 'MULE' if prediction == 1 else 'NORMAL',
            'risk_score': float(risk_score),
            'confidence': float(abs(risk_score - 0.5) * 2),
            'explanation': explanation
        }
    
    def predict_mule_risk_gnn(self, X, A) -> Dict:
        """
        Predict mule risk using GNN
        
        Args:
            X: Node features
            A: Adjacency matrix
            
        Returns:
            predictions: Risk predictions for all nodes
        """
        if not self.models_trained['gnn_detector']:
            raise ValueError("GNN not trained")
        
        predictions, probabilities = self.gnn_detector.predict(X, A)
        risk_scores = self.gnn_detector.get_mule_risk_scores(X, A)
        
        return {
            'model': 'gnn',
            'predictions': predictions.tolist(),
            'risk_scores': risk_scores.tolist(),
            'probabilities': probabilities.tolist()
        }
    
    def calculate_rule_based_risk(self, features: Dict) -> Dict:
        """
        Calculate risk using rule-based model
        
        Args:
            features: Account features
            
        Returns:
            risk_result: Risk score and breakdown
        """
        return self.risk_scorer.calculate_risk_score(features)
    
    def generate_adversarial_pattern(self, n_samples=1, pattern_type=None) -> Any:
        """
        Generate adversarial patterns using HYDRA GAN
        
        Args:
            n_samples: Number of patterns
            pattern_type: Optional pattern type
            
        Returns:
            patterns: Generated patterns
        """
        if not self.models_trained['hydra_gan']:
            raise ValueError("HYDRA GAN not trained")
        
        return self.hydra_gan.generate_adversarial_pattern(n_samples, pattern_type)
    
    def analyze_graph(self, transactions: List[Dict]) -> Dict:
        """
        Analyze transaction network graph
        
        Args:
            transactions: List of transactions
            
        Returns:
            analysis: Graph analysis results
        """
        # Build graph
        graph = self.graph_analytics.build_graph_from_transactions(transactions)
        
        # Calculate metrics
        metrics = self.graph_analytics.get_graph_metrics()
        pagerank = self.graph_analytics.calculate_pagerank()
        betweenness = self.graph_analytics.calculate_betweenness_centrality()
        
        # Detect communities
        communities = self.graph_analytics.detect_communities_louvain()
        community_stats = self.graph_analytics.get_community_stats()
        
        # Find patterns
        cycles = self.graph_analytics.find_cycles()
        hubs = self.graph_analytics.identify_hubs(threshold=0.6)
        funnels = self.graph_analytics.identify_funnels(threshold=0.6)
        
        return {
            'graph_metrics': {
                'n_nodes': metrics.n_nodes,
                'n_edges': metrics.n_edges,
                'density': metrics.density,
                'avg_clustering': metrics.avg_clustering,
                'n_components': metrics.n_components
            },
            'top_nodes': {
                'by_pagerank': self.graph_analytics.get_top_nodes_by_centrality('pagerank', 10),
                'by_betweenness': self.graph_analytics.get_top_nodes_by_centrality('betweenness', 10)
            },
            'communities': {
                'n_communities': community_stats['n_communities'],
                'modularity': community_stats['modularity'],
                'avg_size': community_stats['avg_community_size']
            },
            'suspicious_patterns': {
                'cycles': len(cycles),
                'hubs': len(hubs),
                'funnels': len(funnels)
            }
        }
    
    def get_comprehensive_risk_assessment(self, account_id: str, features: Dict, transactions: List[Dict] = None) -> Dict:
        """
        Get comprehensive risk assessment using all available models
        
        Args:
            account_id: Account identifier
            features: Account features
            transactions: Optional transaction history
            
        Returns:
            assessment: Comprehensive risk assessment
        """
        assessment = {
            'account_id': account_id,
            'timestamp': datetime.now().isoformat(),
            'risk_scores': {},
            'explanations': {},
            'recommendations': []
        }
        
        # Rule-based risk
        rule_risk = self.calculate_rule_based_risk(features)
        assessment['risk_scores']['rule_based'] = rule_risk['final_score']
        assessment['explanations']['rule_based'] = rule_risk
        
        # Random Forest (if trained)
        if self.models_trained['random_forest']:
            try:
                rf_result = self.predict_mule_risk_rf(features)
                assessment['risk_scores']['random_forest'] = rf_result['risk_score']
                assessment['explanations']['random_forest'] = rf_result
            except Exception as e:
                warnings.warn(f"Random Forest prediction failed: {e}")
        
        # Ensemble risk score
        risk_scores = list(assessment['risk_scores'].values())
        assessment['final_risk_score'] = np.mean(risk_scores)
        assessment['risk_confidence'] = 1.0 - np.std(risk_scores)
        
        # Risk level
        final_score = assessment['final_risk_score']
        if final_score >= 0.8:
            assessment['risk_level'] = 'CRITICAL'
            assessment['recommendations'].append('Immediate investigation required')
            assessment['recommendations'].append('File SAR (Suspicious Activity Report)')
        elif final_score >= 0.6:
            assessment['risk_level'] = 'HIGH'
            assessment['recommendations'].append('Enhanced due diligence')
            assessment['recommendations'].append('Monitor transactions closely')
        elif final_score >= 0.4:
            assessment['risk_level'] = 'MEDIUM'
            assessment['recommendations'].append('Standard monitoring')
        else:
            assessment['risk_level'] = 'LOW'
            assessment['recommendations'].append('Normal processing')
        
        return assessment
    
    def save_all_models(self):
        """Save all trained models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.models_trained['random_forest']:
            path = os.path.join(self.model_dir, f'random_forest_{timestamp}.pkl')
            self.random_forest.save_model(path)
        
        if self.models_trained['hydra_gan']:
            path = os.path.join(self.model_dir, f'hydra_gan_{timestamp}.pt')
            self.hydra_gan.save_model(path)
        
        if self.models_trained['gnn_detector']:
            path = os.path.join(self.model_dir, f'gnn_detector_{timestamp}.pt')
            self.gnn_detector.save_model(path)
        
        print(f"All models saved to {self.model_dir}")
    
    def get_model_status(self) -> Dict:
        """Get status of all models"""
        return {
            'models_trained': self.models_trained,
            'models_available': {
                'random_forest': self.random_forest is not None,
                'risk_scorer': True,
                'hydra_gan': self.hydra_gan is not None,
                'gnn_detector': self.gnn_detector is not None,
                'graph_analytics': True,
                'shap_explainer': self.shap_explainer is not None
            }
        }


if __name__ == "__main__":
    print("Model Manager Test\n")
    
    # Initialize manager
    manager = ModelManager()
    
    # Initialize Random Forest
    manager.initialize_random_forest()
    
    # Generate training data
    X, y = manager.random_forest.generate_training_data(n_samples=500)
    
    # Train
    metrics = manager.train_random_forest(X, y)
    print(f"\nTraining complete: {metrics['accuracy']:.3f} accuracy")
    
    # Test prediction
    test_features = {
        'transaction_velocity': 25,
        'in_out_ratio': 0.95,
        'account_age_days': 45,
        'rapid_in_out': 1,
        'dormant_activation': 0,
        'high_throughput': 1,
        'degree_centrality': 0.65,
        'betweenness_centrality': 0.45,
        'pagerank': 0.03,
        'is_hub': 1,
        'is_funnel': 1,
        'multi_hop_count': 6,
        'circular_flow_count': 3,
        'structuring_count': 5
    }
    
    # Comprehensive assessment
    assessment = manager.get_comprehensive_risk_assessment(
        account_id='TEST_001',
        features=test_features
    )
    
    print(f"\nComprehensive Risk Assessment:")
    print(f"  Account: {assessment['account_id']}")
    print(f"  Risk Level: {assessment['risk_level']}")
    print(f"  Final Score: {assessment['final_risk_score']:.3f}")
    print(f"  Confidence: {assessment['risk_confidence']:.3f}")
    print(f"\nRecommendations:")
    for rec in assessment['recommendations']:
        print(f"  - {rec}")
    
    # Model status
    print(f"\nModel Status:")
    status = manager.get_model_status()
    for model, trained in status['models_trained'].items():
        status_str = "✓ Trained" if trained else "✗ Not trained"
        print(f"  {model}: {status_str}")
