"""
Rule-based Risk Scoring Model
Weighted ensemble logic combining multiple risk dimensions
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskDimension(Enum):
    """Risk scoring dimensions"""
    BEHAVIORAL = "behavioral"
    NETWORK = "network"
    LAYERING = "layering"
    VELOCITY = "velocity"

@dataclass
class RiskWeights:
    """Configurable weights for risk scoring"""
    behavioral: float = 0.30
    network: float = 0.25
    layering: float = 0.25
    velocity: float = 0.20
    
    def normalize(self):
        """Ensure weights sum to 1.0"""
        total = self.behavioral + self.network + self.layering + self.velocity
        self.behavioral /= total
        self.network /= total
        self.layering /= total
        self.velocity /= total

class RulBasedRiskScoringModel:
    """
    Rule-based risk scoring model using weighted ensemble logic
    Combines multiple risk dimensions into a final risk score
    """
    
    def __init__(self, weights: RiskWeights = None):
        """
        Initialize risk scoring model
        
        Args:
            weights: Risk dimension weights (default: balanced)
        """
        self.weights = weights or RiskWeights()
        self.weights.normalize()
        
        # Risk thresholds
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.9
        }
        
        # Behavioral risk parameters
        self.behavioral_params = {
            'rapid_in_out_threshold': 0.9,  # 90% of funds move out quickly
            'dormancy_threshold_days': 90,
            'throughput_threshold': 50000,  # High total transaction volume
            'structuring_threshold': 5  # Number of structuring patterns
        }
        
        # Network risk parameters
        self.network_params = {
            'degree_centrality_threshold': 0.5,
            'betweenness_centrality_threshold': 0.3,
            'pagerank_threshold': 0.02,
            'hub_connections': 10
        }
        
        # Layering risk parameters
        self.layering_params = {
            'multi_hop_threshold': 3,
            'circular_flow_threshold': 2,
            'integration_depth': 4
        }
        
        # Velocity risk parameters
        self.velocity_params = {
            'transaction_velocity_threshold': 15,  # txns per day
            'amount_velocity_threshold': 100000,  # $ per day
            'spike_multiplier': 3  # 3x normal velocity
        }
    
    def calculate_behavioral_score(self, features: Dict) -> float:
        """
        Calculate behavioral risk score
        
        Args:
            features: Dictionary of behavioral features
            
        Returns:
            score: Behavioral risk score (0-1)
        """
        score = 0.0
        
        # Rapid in-out pattern
        in_out_ratio = features.get('in_out_ratio', 1.0)
        rapid_in_out = features.get('rapid_in_out', 0)
        if rapid_in_out and in_out_ratio > self.behavioral_params['rapid_in_out_threshold']:
            score += 0.35
        
        # Dormant account activation
        account_age = features.get('account_age_days', 365)
        dormant_activation = features.get('dormant_activation', 0)
        if dormant_activation and account_age > self.behavioral_params['dormancy_threshold_days']:
            score += 0.25
        
        # High throughput
        total_throughput = features.get('total_throughput', 0)
        if total_throughput > self.behavioral_params['throughput_threshold']:
            score += 0.20
        
        # Structuring patterns
        structuring_count = features.get('structuring_count', 0)
        if structuring_count >= self.behavioral_params['structuring_threshold']:
            score += 0.20
        
        return min(score, 1.0)
    
    def calculate_network_score(self, features: Dict) -> float:
        """
        Calculate network risk score
        
        Args:
            features: Dictionary of network features
            
        Returns:
            score: Network risk score (0-1)
        """
        score = 0.0
        
        # Degree centrality (number of connections)
        degree_centrality = features.get('degree_centrality', 0)
        if degree_centrality > self.network_params['degree_centrality_threshold']:
            score += 0.30
        
        # Betweenness centrality (bridge position)
        betweenness = features.get('betweenness_centrality', 0)
        if betweenness > self.network_params['betweenness_centrality_threshold']:
            score += 0.25
        
        # PageRank (importance in network)
        pagerank = features.get('pagerank', 0)
        if pagerank > self.network_params['pagerank_threshold']:
            score += 0.20
        
        # Hub or funnel node
        is_hub = features.get('is_hub', 0)
        is_funnel = features.get('is_funnel', 0)
        if is_hub or is_funnel:
            score += 0.25
        
        return min(score, 1.0)
    
    def calculate_layering_score(self, features: Dict) -> float:
        """
        Calculate layering risk score
        
        Args:
            features: Dictionary of layering features
            
        Returns:
            score: Layering risk score (0-1)
        """
        score = 0.0
        
        # Multi-hop transactions
        multi_hop_count = features.get('multi_hop_count', 0)
        if multi_hop_count >= self.layering_params['multi_hop_threshold']:
            score += 0.40
        
        # Circular flow patterns
        circular_flow_count = features.get('circular_flow_count', 0)
        if circular_flow_count >= self.layering_params['circular_flow_threshold']:
            score += 0.35
        
        # Integration depth
        integration_depth = features.get('integration_depth', 0)
        if integration_depth >= self.layering_params['integration_depth']:
            score += 0.25
        
        return min(score, 1.0)
    
    def calculate_velocity_score(self, features: Dict) -> float:
        """
        Calculate velocity risk score
        
        Args:
            features: Dictionary of velocity features
            
        Returns:
            score: Velocity risk score (0-1)
        """
        score = 0.0
        
        # Transaction velocity (count)
        transaction_velocity = features.get('transaction_velocity', 0)
        if transaction_velocity > self.velocity_params['transaction_velocity_threshold']:
            score += 0.35
        
        # Amount velocity (volume)
        amount_velocity = features.get('amount_velocity', 0)
        if amount_velocity > self.velocity_params['amount_velocity_threshold']:
            score += 0.35
        
        # Velocity spike detection
        avg_velocity = features.get('avg_velocity', transaction_velocity)
        if transaction_velocity > avg_velocity * self.velocity_params['spike_multiplier']:
            score += 0.30
        
        return min(score, 1.0)
    
    def calculate_risk_score(self, features: Dict) -> Dict:
        """
        Calculate comprehensive risk score
        
        Args:
            features: Dictionary of all risk features
            
        Returns:
            result: Dictionary with risk scores and breakdown
        """
        # Calculate individual dimension scores
        behavioral_score = self.calculate_behavioral_score(features)
        network_score = self.calculate_network_score(features)
        layering_score = self.calculate_layering_score(features)
        velocity_score = self.calculate_velocity_score(features)
        
        # Weighted ensemble
        final_score = (
            self.weights.behavioral * behavioral_score +
            self.weights.network * network_score +
            self.weights.layering * layering_score +
            self.weights.velocity * velocity_score
        )
        
        # Determine risk level
        risk_level = self._get_risk_level(final_score)
        
        return {
            'final_score': round(final_score, 3),
            'risk_level': risk_level,
            'dimension_scores': {
                'behavioral': round(behavioral_score, 3),
                'network': round(network_score, 3),
                'layering': round(layering_score, 3),
                'velocity': round(velocity_score, 3)
            },
            'dimension_contributions': {
                'behavioral': round(self.weights.behavioral * behavioral_score, 3),
                'network': round(self.weights.network * network_score, 3),
                'layering': round(self.weights.layering * layering_score, 3),
                'velocity': round(self.weights.velocity * velocity_score, 3)
            },
            'weights': {
                'behavioral': self.weights.behavioral,
                'network': self.weights.network,
                'layering': self.weights.layering,
                'velocity': self.weights.velocity
            }
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= self.risk_thresholds['critical']:
            return 'CRITICAL'
        elif score >= self.risk_thresholds['high']:
            return 'HIGH'
        elif score >= self.risk_thresholds['medium']:
            return 'MEDIUM'
        elif score >= self.risk_thresholds['low']:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def batch_score(self, features_list: List[Dict]) -> List[Dict]:
        """
        Score multiple accounts
        
        Args:
            features_list: List of feature dictionaries
            
        Returns:
            scores: List of risk score results
        """
        return [self.calculate_risk_score(features) for features in features_list]
    
    def update_weights(self, new_weights: RiskWeights):
        """Update risk dimension weights"""
        self.weights = new_weights
        self.weights.normalize()
    
    def update_thresholds(self, dimension: str, new_thresholds: Dict):
        """Update risk thresholds for a dimension"""
        if dimension == 'behavioral':
            self.behavioral_params.update(new_thresholds)
        elif dimension == 'network':
            self.network_params.update(new_thresholds)
        elif dimension == 'layering':
            self.layering_params.update(new_thresholds)
        elif dimension == 'velocity':
            self.velocity_params.update(new_thresholds)


if __name__ == "__main__":
    # Example usage
    print("Rule-based Risk Scoring Model Test\n")
    
    model = RulBasedRiskScoringModel()
    
    # Test case 1: High-risk mule account
    high_risk_features = {
        'in_out_ratio': 0.95,
        'rapid_in_out': 1,
        'account_age_days': 30,
        'dormant_activation': 0,
        'total_throughput': 75000,
        'structuring_count': 7,
        'degree_centrality': 0.6,
        'betweenness_centrality': 0.4,
        'pagerank': 0.025,
        'is_hub': 1,
        'is_funnel': 1,
        'multi_hop_count': 5,
        'circular_flow_count': 3,
        'integration_depth': 5,
        'transaction_velocity': 25,
        'amount_velocity': 150000,
        'avg_velocity': 5
    }
    
    # Test case 2: Low-risk normal account
    low_risk_features = {
        'in_out_ratio': 1.05,
        'rapid_in_out': 0,
        'account_age_days': 500,
        'dormant_activation': 0,
        'total_throughput': 15000,
        'structuring_count': 0,
        'degree_centrality': 0.2,
        'betweenness_centrality': 0.1,
        'pagerank': 0.005,
        'is_hub': 0,
        'is_funnel': 0,
        'multi_hop_count': 1,
        'circular_flow_count': 0,
        'integration_depth': 1,
        'transaction_velocity': 5,
        'amount_velocity': 20000,
        'avg_velocity': 4
    }
    
    # Score accounts
    high_risk_result = model.calculate_risk_score(high_risk_features)
    low_risk_result = model.calculate_risk_score(low_risk_features)
    
    print("High-Risk Account:")
    print(f"  Final Score: {high_risk_result['final_score']}")
    print(f"  Risk Level: {high_risk_result['risk_level']}")
    print(f"  Dimension Scores: {high_risk_result['dimension_scores']}")
    
    print("\nLow-Risk Account:")
    print(f"  Final Score: {low_risk_result['final_score']}")
    print(f"  Risk Level: {low_risk_result['risk_level']}")
    print(f"  Dimension Scores: {low_risk_result['dimension_scores']}")
