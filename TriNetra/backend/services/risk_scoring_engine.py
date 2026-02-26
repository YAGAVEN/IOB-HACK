import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from services.mule_behavior_engine import MuleBehaviorEngine
from services.network_engine import NetworkEngine
from services.layering_engine import LayeringEngine
from database.db_utils import (
    fetch_account_transactions,
    upsert_risk_score,
    get_risk_score,
    fetch_all_transactions,
)

class RiskScoringEngine:
    """
    Real-Time Mule Risk Scoring Engine
    Combines behavioral, network, and layering risk into unified score
    """
    
    def __init__(self):
        self.behavior_engine = MuleBehaviorEngine()
        self.network_engine = NetworkEngine()
        self.layering_engine = LayeringEngine()
        
        # Risk weights
        self.behavioral_weight = 0.40
        self.network_weight = 0.30
        self.layering_weight = 0.20
        self.velocity_weight = 0.10
        
        self.scaler = MinMaxScaler()
    
    def calculate_mule_risk(self, account_id):
        """
        Calculate comprehensive mule risk score for an account
        
        Args:
            account_id: Account identifier
        
        Returns:
            Risk score between 0-100
        """
        # Get behavioral risk
        behavioral_analysis = self.behavior_engine.analyze_account(account_id)
        behavioral_score = behavioral_analysis['mule_pattern_score']
        
        # Get network risk
        network_analysis = self.network_engine.analyze_account_network(account_id)
        network_score = network_analysis.get('network_risk_score', 0.0)
        
        # Get layering risk
        layering_analysis = self.layering_engine.analyze_layering_risk(account_id)
        layering_score = layering_analysis['layering_risk_score']
        
        # Get velocity risk
        velocity_score = self._calculate_velocity_risk(account_id)
        
        # Combined weighted score
        combined_score = (
            behavioral_score * self.behavioral_weight +
            network_score * self.network_weight +
            layering_score * self.layering_weight +
            velocity_score * self.velocity_weight
        )
        
        # Convert to 0-100 scale
        risk_score = min(combined_score * 100, 100)
        
        # Store in database
        self._store_risk_score(account_id, risk_score)
        
        return {
            'account_id': account_id,
            'risk_score': round(risk_score, 2),
            'risk_level': self._get_risk_level(risk_score),
            'components': {
                'behavioral_score': round(behavioral_score * 100, 2),
                'network_score': round(network_score * 100, 2),
                'layering_score': round(layering_score * 100, 2),
                'velocity_score': round(velocity_score * 100, 2)
            },
            'details': {
                'behavioral': behavioral_analysis,
                'network': network_analysis,
                'layering': layering_analysis
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_velocity_risk(self, account_id):
        """Calculate transaction velocity risk (0-1)"""
        try:
            df = fetch_account_transactions(account_id)
            if df.empty:
                return 0.0
            
            df = df.head(100)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate velocity metrics
            time_span = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
            if time_span == 0:
                return 1.0  # All transactions at same time - very suspicious
            
            tx_per_hour = len(df) / max(time_span, 1)
            
            # Normalize velocity
            # More than 10 tx/hour is high risk
            velocity_score = min(tx_per_hour / 10, 1.0)
            
            return velocity_score
            
        except Exception as e:
            print(f"Error calculating velocity risk: {e}")
            return 0.0
    
    def _store_risk_score(self, account_id, risk_score):
        """Store risk score in database"""
        try:
            upsert_risk_score(account_id, risk_score)
        except Exception as e:
            print(f"Error storing risk score: {e}")
    
    def get_stored_risk_score(self, account_id):
        """Retrieve stored risk score from database"""
        try:
            score = get_risk_score(account_id)
            if score is not None:
                return {
                    'account_id': account_id,
                    'risk_score': score,
                    'last_updated': datetime.now().isoformat()
                }
            return None
        except Exception as e:
            print(f"Error retrieving risk score: {e}")
            return None
    
    def get_high_risk_accounts(self, threshold=70, limit=50):
        """Get accounts with risk scores above threshold"""
        try:
            from database.db_utils import fetch_df
            df = fetch_df('account_risk_scores')
            if df.empty:
                return []
            filtered = df[df['risk_score'] >= threshold].sort_values('risk_score', ascending=False).head(limit)
            return filtered.to_dict('records')
        except Exception as e:
            print(f"Error getting high risk accounts: {e}")
            return []
    
    def batch_update_risk_scores(self, account_ids=None):
        """
        Update risk scores for multiple accounts
        
        Args:
            account_ids: List of account IDs (if None, updates all accounts)
        
        Returns:
            Number of accounts updated
        """
        if account_ids is None:
            # Get all unique accounts from transactions
            try:
                df = fetch_all_transactions()
                if df.empty:
                    return 0
                from_accs = df['from_account'].dropna().unique().tolist()
                to_accs = df['to_account'].dropna().unique().tolist()
                account_ids = list(set(from_accs + to_accs))
            except Exception as e:
                print(f"Error fetching accounts: {e}")
                return 0
        
        updated_count = 0
        for account_id in account_ids:
            try:
                self.calculate_mule_risk(account_id)
                updated_count += 1
            except Exception as e:
                print(f"Error updating risk for {account_id}: {e}")
                continue
        
        return updated_count
    
    def _get_risk_level(self, score):
        """Convert numeric score to risk level"""
        if score >= 70:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def update_risk_on_transaction(self, transaction_data):
        """
        Update risk scores when a new transaction is added
        
        Args:
            transaction_data: Dictionary with transaction info
        """
        from_account = transaction_data.get('from_account')
        to_account = transaction_data.get('to_account')
        
        # Update both accounts involved
        if from_account:
            try:
                self.calculate_mule_risk(from_account)
            except Exception as e:
                print(f"Error updating risk for {from_account}: {e}")
        
        if to_account:
            try:
                self.calculate_mule_risk(to_account)
            except Exception as e:
                print(f"Error updating risk for {to_account}: {e}")
