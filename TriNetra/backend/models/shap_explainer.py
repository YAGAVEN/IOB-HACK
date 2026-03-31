"""
SHAP Explainability Engine
Provides interpretable explanations for ML model predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
import warnings

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    warnings.warn("SHAP not available. Install with: pip install shap")

class SHAPExplainer:
    """
    SHAP-based explainability engine for ML models
    Provides feature importance and contribution explanations
    """
    
    def __init__(self, model, feature_names: List[str]):
        """
        Initialize SHAP explainer
        
        Args:
            model: Trained ML model (sklearn, xgboost, etc.)
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.shap_values = None
        self.base_value = None
        
        if not SHAP_AVAILABLE:
            warnings.warn("SHAP not available, using simplified explanations")
    
    def fit(self, X_background: np.ndarray, explainer_type='tree'):
        """
        Fit SHAP explainer on background data
        
        Args:
            X_background: Background dataset for SHAP (training data sample)
            explainer_type: Type of explainer ('tree', 'kernel', 'linear')
        """
        if not SHAP_AVAILABLE:
            return
        
        if explainer_type == 'tree':
            # For tree-based models (RandomForest, XGBoost, etc.)
            self.explainer = shap.TreeExplainer(self.model)
        elif explainer_type == 'kernel':
            # Model-agnostic kernel explainer
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba, 
                shap.sample(X_background, 100)
            )
        elif explainer_type == 'linear':
            # For linear models
            self.explainer = shap.LinearExplainer(self.model, X_background)
        else:
            raise ValueError(f"Unknown explainer type: {explainer_type}")
        
        print(f"SHAP {explainer_type} explainer fitted")
    
    def explain_prediction(self, X: np.ndarray, index: Optional[int] = None) -> Dict:
        """
        Explain a single prediction
        
        Args:
            X: Input features (single instance or batch)
            index: Index to explain (if X is batch)
            
        Returns:
            explanation: Dictionary with explanation details
        """
        if not SHAP_AVAILABLE:
            return self._simplified_explanation(X, index)
        
        if self.explainer is None:
            raise ValueError("Explainer not fitted. Call fit() first.")
        
        # Ensure 2D array
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        # Get SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # For binary classification, use positive class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Select instance
        if index is not None:
            shap_instance = shap_values[index]
            features = X[index]
        else:
            shap_instance = shap_values[0]
            features = X[0]
        
        # Create explanation
        explanation = {
            'base_value': float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, np.ndarray) else self.explainer.expected_value),
            'feature_contributions': {},
            'feature_values': {},
            'top_positive': [],
            'top_negative': []
        }
        
        # Feature contributions
        for i, (feature_name, shap_val, feature_val) in enumerate(zip(
            self.feature_names, shap_instance, features
        )):
            explanation['feature_contributions'][feature_name] = float(shap_val)
            explanation['feature_values'][feature_name] = float(feature_val)
        
        # Sort features by contribution
        sorted_contrib = sorted(
            explanation['feature_contributions'].items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        # Top positive and negative contributors
        explanation['top_positive'] = [
            {'feature': f, 'contribution': c, 'value': explanation['feature_values'][f]}
            for f, c in sorted_contrib if c > 0
        ][:5]
        
        explanation['top_negative'] = [
            {'feature': f, 'contribution': c, 'value': explanation['feature_values'][f]}
            for f, c in sorted_contrib if c < 0
        ][:5]
        
        return explanation
    
    def explain_batch(self, X: np.ndarray) -> List[Dict]:
        """
        Explain multiple predictions
        
        Args:
            X: Input features (batch)
            
        Returns:
            explanations: List of explanation dictionaries
        """
        explanations = []
        for i in range(X.shape[0]):
            exp = self.explain_prediction(X, index=i)
            explanations.append(exp)
        
        return explanations
    
    def get_global_feature_importance(self, X: np.ndarray) -> Dict[str, float]:
        """
        Get global feature importance across dataset
        
        Args:
            X: Input features
            
        Returns:
            importance: Dictionary mapping features to importance scores
        """
        if not SHAP_AVAILABLE:
            return self._simplified_global_importance()
        
        if self.explainer is None:
            raise ValueError("Explainer not fitted. Call fit() first.")
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # For binary classification
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Mean absolute SHAP values
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        
        importance = dict(zip(self.feature_names, mean_abs_shap))
        
        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return importance
    
    def generate_explanation_text(self, explanation: Dict, risk_score: float) -> str:
        """
        Generate human-readable explanation text
        
        Args:
            explanation: Explanation dictionary
            risk_score: Predicted risk score
            
        Returns:
            text: Human-readable explanation
        """
        lines = []
        lines.append(f"Risk Score: {risk_score:.3f}")
        lines.append(f"Baseline Risk: {explanation['base_value']:.3f}\n")
        
        if explanation['top_positive']:
            lines.append("Factors INCREASING risk:")
            for item in explanation['top_positive'][:3]:
                lines.append(f"  • {item['feature']}: {item['value']:.2f} "
                           f"(+{item['contribution']:.3f})")
        
        if explanation['top_negative']:
            lines.append("\nFactors DECREASING risk:")
            for item in explanation['top_negative'][:3]:
                lines.append(f"  • {item['feature']}: {item['value']:.2f} "
                           f"({item['contribution']:.3f})")
        
        return "\n".join(lines)
    
    def get_force_plot_data(self, explanation: Dict) -> Dict:
        """
        Get data for force plot visualization
        
        Args:
            explanation: Explanation dictionary
            
        Returns:
            plot_data: Data for force plot
        """
        return {
            'base_value': explanation['base_value'],
            'contributions': explanation['feature_contributions'],
            'feature_values': explanation['feature_values']
        }
    
    def _simplified_explanation(self, X: np.ndarray, index: Optional[int] = None) -> Dict:
        """
        Simplified explanation when SHAP is not available
        Uses feature importance from model
        
        Args:
            X: Input features
            index: Instance index
            
        Returns:
            explanation: Simplified explanation
        """
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        if index is not None:
            features = X[index]
        else:
            features = X[0]
        
        # Get feature importance from model
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
        else:
            # Fallback to uniform importance
            importance = np.ones(len(self.feature_names)) / len(self.feature_names)
        
        # Estimate contributions (simplified)
        contributions = features * importance
        contributions = (contributions / contributions.sum()) * 0.5  # Normalize
        
        explanation = {
            'base_value': 0.3,
            'feature_contributions': dict(zip(self.feature_names, contributions)),
            'feature_values': dict(zip(self.feature_names, features)),
            'top_positive': [],
            'top_negative': [],
            'note': 'Simplified explanation (SHAP not available)'
        }
        
        # Sort by contribution
        sorted_contrib = sorted(
            explanation['feature_contributions'].items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        explanation['top_positive'] = [
            {'feature': f, 'contribution': c, 'value': explanation['feature_values'][f]}
            for f, c in sorted_contrib if c > 0
        ][:5]
        
        return explanation
    
    def _simplified_global_importance(self) -> Dict[str, float]:
        """Simplified global importance when SHAP is not available"""
        if hasattr(self.model, 'feature_importances_'):
            importance = dict(zip(self.feature_names, self.model.feature_importances_))
            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        else:
            return {f: 1.0 / len(self.feature_names) for f in self.feature_names}


class ExplainabilityReport:
    """
    Comprehensive explainability report generator
    """
    
    def __init__(self, explainer: SHAPExplainer):
        self.explainer = explainer
    
    def generate_account_report(self, 
                                account_id: str, 
                                features: np.ndarray, 
                                risk_score: float,
                                threshold: float = 0.7) -> Dict:
        """
        Generate comprehensive explanation report for an account
        
        Args:
            account_id: Account identifier
            features: Account features
            risk_score: Predicted risk score
            threshold: Risk threshold for classification
            
        Returns:
            report: Comprehensive explanation report
        """
        # Get explanation
        explanation = self.explainer.explain_prediction(features)
        
        # Generate text
        explanation_text = self.explainer.generate_explanation_text(explanation, risk_score)
        
        # Risk classification
        if risk_score >= threshold:
            classification = 'HIGH RISK'
            recommendation = 'Flag for investigation and enhanced due diligence'
        elif risk_score >= threshold * 0.7:
            classification = 'MEDIUM RISK'
            recommendation = 'Monitor closely and review transaction patterns'
        else:
            classification = 'LOW RISK'
            recommendation = 'Standard monitoring'
        
        report = {
            'account_id': account_id,
            'risk_score': risk_score,
            'classification': classification,
            'recommendation': recommendation,
            'explanation_text': explanation_text,
            'feature_contributions': explanation['feature_contributions'],
            'top_risk_factors': explanation['top_positive'],
            'mitigating_factors': explanation['top_negative'],
            'base_risk': explanation['base_value']
        }
        
        return report


if __name__ == "__main__":
    print("SHAP Explainability Engine Test\n")
    
    if SHAP_AVAILABLE:
        print("SHAP is available ✓\n")
        
        # Create dummy model and data
        from sklearn.ensemble import RandomForestClassifier
        
        feature_names = [
            'transaction_velocity', 'in_out_ratio', 'account_age_days',
            'degree_centrality', 'betweenness_centrality'
        ]
        
        # Generate training data
        np.random.seed(42)
        X_train = np.random.randn(100, 5)
        y_train = (X_train[:, 0] + X_train[:, 1] > 0).astype(int)
        
        # Train model
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # Initialize explainer
        explainer = SHAPExplainer(model, feature_names)
        explainer.fit(X_train, explainer_type='tree')
        
        # Test instance
        X_test = np.random.randn(1, 5)
        risk_score = model.predict_proba(X_test)[0, 1]
        
        # Get explanation
        explanation = explainer.explain_prediction(X_test)
        
        print(f"Risk Score: {risk_score:.3f}\n")
        print("Top Risk Factors:")
        for item in explanation['top_positive'][:3]:
            print(f"  • {item['feature']}: {item['value']:.2f} (+{item['contribution']:.3f})")
        
        # Global importance
        print("\nGlobal Feature Importance:")
        importance = explainer.get_global_feature_importance(X_train)
        for feature, score in list(importance.items())[:5]:
            print(f"  {feature}: {score:.4f}")
        
    else:
        print("SHAP not available. Using simplified explanations.\n")
        print("Install SHAP with: pip install shap")
