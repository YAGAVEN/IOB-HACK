import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class MuleBehaviorEngine:
    """
    Mule Behavioral Profiling Engine
    Analyzes account behavior patterns to detect money mule activity
    """
    
    def __init__(self):
        self.high_volume_threshold = 50000
        self.small_amount_threshold = 10000
        self.large_amount_threshold = 50000
        self.rapid_window_hours = 1
        self.pattern_window_hours = 24
        self.dormant_days = 60
        self.new_account_days = 30
    
    def compute_behavioral_features(self, account_id, transactions_df=None):
        """
        Compute behavioral features for a given account
        
        Args:
            account_id: Account identifier
            transactions_df: Optional DataFrame of transactions (if not provided, fetches from DB)
        
        Returns:
            Dictionary with behavioral features
        """
        if transactions_df is None:
            transactions_df = self._get_account_transactions(account_id)
        
        if transactions_df.empty:
            return self._empty_features()
        
        features = {}
        
        # Calculate transaction velocity
        features['transaction_velocity'] = self._calculate_velocity(transactions_df)
        
        # Calculate in/out ratio
        features['in_out_ratio'] = self._calculate_in_out_ratio(account_id, transactions_df)
        
        # Calculate account age
        features['account_age_days'] = self._calculate_account_age(account_id, transactions_df)
        
        # Check dormant activation pattern
        features['dormant_activation_flag'] = self._check_dormant_activation(transactions_df)
        
        # Check small inbound -> large outbound pattern
        features['small_inbound_large_outbound_pattern'] = self._check_small_to_large_pattern(
            account_id, transactions_df
        )
        
        # Check high throughput
        features['high_throughput_flag'] = self._check_high_throughput(account_id, transactions_df)
        
        # Detect rapid in-out pattern
        features['rapid_in_out'] = self._detect_rapid_in_out(account_id, transactions_df)
        
        # Calculate mule pattern score
        features['mule_pattern_score'] = self._calculate_mule_score(features)
        
        return features
    
    def _get_account_transactions(self, account_id):
        """Fetch transactions for an account from database"""
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            query = """
                SELECT * FROM transactions 
                WHERE from_account = ? OR to_account = ?
                ORDER BY timestamp
            """
            df = pd.read_sql_query(query, conn, params=[account_id, account_id])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return pd.DataFrame()
    
    def _calculate_velocity(self, transactions_df):
        """Calculate transaction velocity (transactions per hour)"""
        if transactions_df.empty:
            return 0.0
        
        time_span = (transactions_df['timestamp'].max() - transactions_df['timestamp'].min())
        hours = max(time_span.total_seconds() / 3600, 1)
        return len(transactions_df) / hours
    
    def _calculate_in_out_ratio(self, account_id, transactions_df):
        """Calculate ratio of incoming to outgoing transactions"""
        inbound = transactions_df[transactions_df['to_account'] == account_id]
        outbound = transactions_df[transactions_df['from_account'] == account_id]
        
        inbound_count = len(inbound)
        outbound_count = len(outbound)
        
        if outbound_count == 0:
            return float('inf') if inbound_count > 0 else 0.0
        
        return inbound_count / outbound_count
    
    def _calculate_account_age(self, account_id, transactions_df):
        """Calculate account age in days based on first transaction"""
        if transactions_df.empty:
            return 0
        
        first_transaction = transactions_df['timestamp'].min()
        age = (datetime.now() - first_transaction).days
        return max(age, 0)
    
    def _check_dormant_activation(self, transactions_df):
        """Check if account was dormant then suddenly activated"""
        if len(transactions_df) < 2:
            return False
        
        transactions_df = transactions_df.sort_values('timestamp')
        
        # Look for gaps of dormant_days or more
        for i in range(len(transactions_df) - 1):
            gap = (transactions_df.iloc[i + 1]['timestamp'] - 
                   transactions_df.iloc[i]['timestamp']).days
            
            if gap >= self.dormant_days:
                # Check if there's a spike after dormancy
                recent_transactions = transactions_df[
                    transactions_df['timestamp'] >= transactions_df.iloc[i + 1]['timestamp']
                ]
                if len(recent_transactions) >= 5:
                    return True
        
        return False
    
    def _check_small_to_large_pattern(self, account_id, transactions_df):
        """
        Detect pattern: 5+ small inbound followed by large outbound within 24h
        """
        if len(transactions_df) < 6:
            return False
        
        transactions_df = transactions_df.sort_values('timestamp')
        
        # Look for small inbound transactions
        small_inbound = transactions_df[
            (transactions_df['to_account'] == account_id) & 
            (transactions_df['amount'] < self.small_amount_threshold)
        ]
        
        # For each large outbound, check if preceded by 5+ small inbound
        large_outbound = transactions_df[
            (transactions_df['from_account'] == account_id) & 
            (transactions_df['amount'] > self.large_amount_threshold)
        ]
        
        for _, out_tx in large_outbound.iterrows():
            out_time = out_tx['timestamp']
            window_start = out_time - timedelta(hours=self.pattern_window_hours)
            
            recent_small_inbound = small_inbound[
                (small_inbound['timestamp'] >= window_start) & 
                (small_inbound['timestamp'] < out_time)
            ]
            
            if len(recent_small_inbound) >= 5:
                return True
        
        return False
    
    def _check_high_throughput(self, account_id, transactions_df):
        """Check if account has unusually high transaction throughput"""
        total_amount = transactions_df['amount'].sum()
        return total_amount > self.high_volume_threshold
    
    def _detect_rapid_in_out(self, account_id, transactions_df):
        """Detect inbound and outbound within rapid_window_hours"""
        if len(transactions_df) < 2:
            return False
        
        transactions_df = transactions_df.sort_values('timestamp')
        
        inbound = transactions_df[transactions_df['to_account'] == account_id]
        outbound = transactions_df[transactions_df['from_account'] == account_id]
        
        # Check if any outbound happens within rapid_window_hours of inbound
        for _, in_tx in inbound.iterrows():
            in_time = in_tx['timestamp']
            window_end = in_time + timedelta(hours=self.rapid_window_hours)
            
            rapid_outbound = outbound[
                (outbound['timestamp'] >= in_time) & 
                (outbound['timestamp'] <= window_end)
            ]
            
            if len(rapid_outbound) > 0:
                return True
        
        return False
    
    def _calculate_mule_score(self, features):
        """
        Calculate overall mule pattern score (0-1)
        Weighted combination of different indicators
        """
        score = 0.0
        
        # Rapid in-out is a strong indicator
        if features['rapid_in_out']:
            score += 0.30
        
        # Small to large pattern
        if features['small_inbound_large_outbound_pattern']:
            score += 0.25
        
        # Dormant activation
        if features['dormant_activation_flag']:
            score += 0.15
        
        # High velocity
        if features['transaction_velocity'] > 5:
            score += 0.15
        
        # New account + high throughput
        if features['account_age_days'] < self.new_account_days and features['high_throughput_flag']:
            score += 0.15
        
        return min(score, 1.0)
    
    def _empty_features(self):
        """Return empty feature set"""
        return {
            'transaction_velocity': 0.0,
            'in_out_ratio': 0.0,
            'account_age_days': 0,
            'dormant_activation_flag': False,
            'small_inbound_large_outbound_pattern': False,
            'high_throughput_flag': False,
            'rapid_in_out': False,
            'mule_pattern_score': 0.0
        }
    
    def analyze_account(self, account_id):
        """
        Main analysis function for an account
        Returns complete behavioral analysis with detection results
        """
        features = self.compute_behavioral_features(account_id)
        
        return {
            'account_id': account_id,
            'features': features,
            'rapid_in_out': features['rapid_in_out'],
            'dormant_activation': features['dormant_activation_flag'],
            'mule_pattern_score': features['mule_pattern_score'],
            'risk_level': self._get_risk_level(features['mule_pattern_score']),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_risk_level(self, score):
        """Convert score to risk level"""
        if score >= 0.7:
            return 'HIGH'
        elif score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
