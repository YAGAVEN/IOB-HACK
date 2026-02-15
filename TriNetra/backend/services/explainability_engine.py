import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from services.risk_scoring_engine import RiskScoringEngine

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("Warning: SHAP not available, using simplified explanations")

class ExplainabilityEngine:
    """
    Explainable AI Engine for Risk Scoring
    Provides interpretable explanations for risk scores using SHAP
    """
    
    def __init__(self):
        self.risk_engine = RiskScoringEngine()
        self.model = None
        self.explainer = None
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
    
    def explain_account_risk(self, account_id):
        """
        Generate explanation for account's risk score
        
        Args:
            account_id: Account identifier
        
        Returns:
            Dictionary with top contributing features
        """
        # Get comprehensive risk analysis
        risk_analysis = self.risk_engine.calculate_mule_risk(account_id)
        
        # Extract features for explanation
        features = self._extract_features(risk_analysis)
        
        if SHAP_AVAILABLE and self.model is not None:
            # Use SHAP for explanation
            explanations = self._generate_shap_explanation(features)
        else:
            # Use rule-based explanation
            explanations = self._generate_rule_based_explanation(features, risk_analysis)
        
        return {
            'account_id': account_id,
            'risk_score': risk_analysis['risk_score'],
            'risk_level': risk_analysis['risk_level'],
            'top_reasons': explanations['top_reasons'],
            'feature_contributions': explanations['contributions'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_features(self, risk_analysis):
        """Extract feature vector from risk analysis"""
        behavioral = risk_analysis['details']['behavioral']['features']
        network = risk_analysis['details']['network'].get('metrics', {})
        layering = risk_analysis['details']['layering']
        
        features = {
            'transaction_velocity': behavioral.get('transaction_velocity', 0),
            'in_out_ratio': min(behavioral.get('in_out_ratio', 0), 10),  # Cap extreme values
            'account_age_days': behavioral.get('account_age_days', 0),
            'rapid_in_out': 1 if behavioral.get('rapid_in_out', False) else 0,
            'dormant_activation': 1 if behavioral.get('dormant_activation_flag', False) else 0,
            'high_throughput': 1 if behavioral.get('high_throughput_flag', False) else 0,
            'degree_centrality': network.get('degree_centrality', 0),
            'betweenness_centrality': network.get('betweenness_centrality', 0),
            'pagerank': network.get('pagerank', 0),
            'is_hub': 1 if risk_analysis['details']['network'].get('is_hub', False) else 0,
            'is_funnel': 1 if risk_analysis['details']['network'].get('is_funnel', False) else 0,
            'multi_hop_count': layering.get('multi_hop_paths', 0),
            'circular_flow_count': layering.get('circular_flows', 0),
            'structuring_count': layering.get('structuring_patterns', 0)
        }
        
        return features
    
    def _generate_shap_explanation(self, features):
        """Generate SHAP-based explanation"""
        if not SHAP_AVAILABLE or self.explainer is None:
            return self._generate_rule_based_explanation(features, None)
        
        try:
            # Convert to array
            feature_array = np.array([[features[name] for name in self.feature_names]])
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(feature_array)
            
            # Get top contributing features
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # For binary classification
            
            feature_impacts = [(self.feature_names[i], abs(shap_values[0][i])) 
                              for i in range(len(self.feature_names))]
            feature_impacts.sort(key=lambda x: x[1], reverse=True)
            
            top_reasons = [self._humanize_feature(name) for name, _ in feature_impacts[:5]]
            
            contributions = {
                name: float(shap_values[0][i]) 
                for i, name in enumerate(self.feature_names)
            }
            
            return {
                'top_reasons': top_reasons,
                'contributions': contributions
            }
            
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return self._generate_rule_based_explanation(features, None)
    
    def _generate_rule_based_explanation(self, features, risk_analysis):
        """Generate rule-based explanation when SHAP is not available"""
        reasons = []
        contributions = {}
        
        # Check each feature and add explanation if significant
        if features['rapid_in_out'] == 1:
            reasons.append("Rapid in-out transaction pattern detected")
            contributions['rapid_in_out'] = 0.30
        
        if features['betweenness_centrality'] > 0.1:
            reasons.append("High betweenness centrality in network (key intermediary)")
            contributions['betweenness_centrality'] = 0.25
        
        if features['is_hub'] == 1:
            reasons.append("Hub-and-spoke distribution pattern")
            contributions['is_hub'] = 0.20
        
        if features['is_funnel'] == 1:
            reasons.append("Funnel account behavior (many inbound, few outbound)")
            contributions['is_funnel'] = 0.20
        
        if features['structuring_count'] > 0:
            reasons.append(f"Structuring pattern detected ({features['structuring_count']} instances)")
            contributions['structuring_count'] = 0.20
        
        if features['multi_hop_count'] > 0:
            reasons.append(f"Involved in multi-hop layering chains ({features['multi_hop_count']} paths)")
            contributions['multi_hop_count'] = 0.15
        
        if features['circular_flow_count'] > 0:
            reasons.append(f"Circular money flow detected ({features['circular_flow_count']} cycles)")
            contributions['circular_flow_count'] = 0.15
        
        if features['dormant_activation'] == 1:
            reasons.append("Dormant account suddenly activated")
            contributions['dormant_activation'] = 0.15
        
        if features['account_age_days'] < 30 and features['high_throughput'] == 1:
            reasons.append("New account with high transaction volume")
            contributions['account_age_days'] = 0.10
        
        if features['transaction_velocity'] > 5:
            reasons.append(f"High transaction velocity ({features['transaction_velocity']:.2f} tx/hour)")
            contributions['transaction_velocity'] = 0.10
        
        # Sort reasons by contribution
        sorted_reasons = sorted(
            [(r, contributions.get(self._extract_feature_key(r), 0)) for r in reasons],
            key=lambda x: x[1],
            reverse=True
        )
        
        top_reasons = [r for r, _ in sorted_reasons[:5]]
        
        return {
            'top_reasons': top_reasons if top_reasons else ["Low overall risk indicators"],
            'contributions': contributions
        }
    
    def _extract_feature_key(self, reason_text):
        """Extract feature key from reason text"""
        if 'rapid in-out' in reason_text.lower():
            return 'rapid_in_out'
        elif 'betweenness' in reason_text.lower():
            return 'betweenness_centrality'
        elif 'hub' in reason_text.lower():
            return 'is_hub'
        elif 'funnel' in reason_text.lower():
            return 'is_funnel'
        elif 'structuring' in reason_text.lower():
            return 'structuring_count'
        elif 'multi-hop' in reason_text.lower():
            return 'multi_hop_count'
        elif 'circular' in reason_text.lower():
            return 'circular_flow_count'
        elif 'dormant' in reason_text.lower():
            return 'dormant_activation'
        elif 'age' in reason_text.lower():
            return 'account_age_days'
        elif 'velocity' in reason_text.lower():
            return 'transaction_velocity'
        return 'unknown'
    
    def _humanize_feature(self, feature_name):
        """Convert feature name to human-readable description"""
        humanized = {
            'transaction_velocity': 'High transaction velocity',
            'in_out_ratio': 'Unusual in/out transaction ratio',
            'account_age_days': 'New account',
            'rapid_in_out': 'Rapid in-out pattern',
            'dormant_activation': 'Dormant account activation',
            'high_throughput': 'High transaction volume',
            'degree_centrality': 'High network connectivity',
            'betweenness_centrality': 'Key network intermediary',
            'pagerank': 'High network importance',
            'is_hub': 'Hub-and-spoke pattern',
            'is_funnel': 'Funnel account pattern',
            'multi_hop_count': 'Multi-hop layering involvement',
            'circular_flow_count': 'Circular flow involvement',
            'structuring_count': 'Structuring pattern detected'
        }
        return humanized.get(feature_name, feature_name.replace('_', ' ').title())
    
    def train_model(self, labeled_data=None):
        """
        Train Random Forest model for SHAP explanations
        
        Args:
            labeled_data: DataFrame with features and labels
        """
        if not SHAP_AVAILABLE:
            print("SHAP not available, skipping model training")
            return
        
        if labeled_data is None:
            # Generate synthetic training data
            labeled_data = self._generate_synthetic_training_data()
        
        X = labeled_data[self.feature_names]
        y = labeled_data['is_mule']
        
        # Train Random Forest
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Create SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        
        print("Model trained successfully")
    
    def _generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic training data for model"""
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Generate mule accounts (40% of data)
            is_mule = np.random.random() < 0.4
            
            if is_mule:
                sample = {
                    'transaction_velocity': np.random.uniform(3, 15),
                    'in_out_ratio': np.random.uniform(0.8, 1.2),
                    'account_age_days': np.random.uniform(1, 60),
                    'rapid_in_out': np.random.choice([0, 1], p=[0.2, 0.8]),
                    'dormant_activation': np.random.choice([0, 1], p=[0.7, 0.3]),
                    'high_throughput': np.random.choice([0, 1], p=[0.3, 0.7]),
                    'degree_centrality': np.random.uniform(0.3, 0.9),
                    'betweenness_centrality': np.random.uniform(0.2, 0.8),
                    'pagerank': np.random.uniform(0.1, 0.5),
                    'is_hub': np.random.choice([0, 1], p=[0.6, 0.4]),
                    'is_funnel': np.random.choice([0, 1], p=[0.5, 0.5]),
                    'multi_hop_count': np.random.randint(0, 5),
                    'circular_flow_count': np.random.randint(0, 3),
                    'structuring_count': np.random.randint(0, 4)
                }
            else:
                sample = {
                    'transaction_velocity': np.random.uniform(0, 3),
                    'in_out_ratio': np.random.uniform(0.5, 2.0),
                    'account_age_days': np.random.uniform(30, 1000),
                    'rapid_in_out': np.random.choice([0, 1], p=[0.9, 0.1]),
                    'dormant_activation': np.random.choice([0, 1], p=[0.95, 0.05]),
                    'high_throughput': np.random.choice([0, 1], p=[0.8, 0.2]),
                    'degree_centrality': np.random.uniform(0, 0.3),
                    'betweenness_centrality': np.random.uniform(0, 0.2),
                    'pagerank': np.random.uniform(0, 0.1),
                    'is_hub': np.random.choice([0, 1], p=[0.95, 0.05]),
                    'is_funnel': np.random.choice([0, 1], p=[0.9, 0.1]),
                    'multi_hop_count': np.random.randint(0, 2),
                    'circular_flow_count': np.random.randint(0, 1),
                    'structuring_count': np.random.randint(0, 1)
                }
            
            sample['is_mule'] = 1 if is_mule else 0
            data.append(sample)
        
        return pd.DataFrame(data)
