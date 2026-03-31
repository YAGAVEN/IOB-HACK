import networkx as nx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from services.network_engine import NetworkEngine
from database.db_utils import fetch_all_transactions as _db_fetch_all

class LayeringEngine:
    """
    Layering & Multi-Hop Fund Flow Detection Engine
    Detects complex money laundering patterns involving multiple transaction hops
    """
    
    def __init__(self):
        self.network_engine = NetworkEngine()
        self.structuring_threshold = 49000  # Just below 50k reporting threshold
        self.structuring_tolerance = 2000
        self.min_structuring_count = 3
        
    def detect_multi_hop_paths(self, graph=None, time_window_hours=24, min_hops=3):
        """
        Detect multi-hop transaction paths within a time window
        
        Args:
            graph: NetworkX graph (if None, builds from DB)
            time_window_hours: Time window for path detection
            min_hops: Minimum number of hops to consider
        
        Returns:
            List of suspicious multi-hop paths
        """
        if graph is None:
            transactions_df = self._get_all_transactions()
            graph = self.network_engine.build_transaction_graph(transactions_df)
        
        suspicious_paths = []
        
        # Sample nodes to check (avoid exponential complexity)
        nodes = list(graph.nodes())
        sample_size = min(30, len(nodes))
        sample_nodes = np.random.choice(nodes, sample_size, replace=False) if len(nodes) > sample_size else nodes
        
        for source in sample_nodes:
            # Find paths from this source
            for target in sample_nodes:
                if source == target:
                    continue
                
                try:
                    # Find simple paths
                    paths = list(nx.all_simple_paths(graph, source, target, cutoff=min_hops + 2))
                    
                    for path in paths:
                        if len(path) < min_hops:
                            continue
                        
                        # Check if entire path occurred within time window
                        path_info = self._analyze_path_timing(graph, path, time_window_hours)
                        
                        if path_info['within_window']:
                            suspicious_paths.append({
                                'path': path,
                                'hops': len(path) - 1,
                                'total_amount': path_info['total_amount'],
                                'time_span_hours': path_info['time_span_hours'],
                                'first_timestamp': path_info['first_timestamp'],
                                'last_timestamp': path_info['last_timestamp'],
                                'pattern_type': 'multi_hop_layering'
                            })
                
                except nx.NetworkXNoPath:
                    continue
                except Exception as e:
                    continue
        
        # Sort by number of hops and amount
        suspicious_paths.sort(key=lambda x: (x['hops'], x['total_amount']), reverse=True)
        
        return suspicious_paths
    
    def _analyze_path_timing(self, graph, path, time_window_hours):
        """Analyze timing of transactions along a path"""
        timestamps = []
        total_amount = 0
        
        for i in range(len(path) - 1):
            edge_data = graph.get_edge_data(path[i], path[i+1])
            if edge_data:
                total_amount += edge_data.get('weight', 0)
                edge_timestamps = edge_data.get('timestamps', [])
                if edge_timestamps:
                    # Use first timestamp for this edge
                    timestamps.append(pd.to_datetime(edge_timestamps[0]))
        
        if not timestamps:
            return {
                'within_window': False,
                'total_amount': 0,
                'time_span_hours': 0,
                'first_timestamp': None,
                'last_timestamp': None
            }
        
        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        within_window = time_span <= time_window_hours
        
        return {
            'within_window': within_window,
            'total_amount': total_amount,
            'time_span_hours': time_span,
            'first_timestamp': timestamps[0].isoformat(),
            'last_timestamp': timestamps[-1].isoformat()
        }
    
    def detect_circular_flows(self, graph=None):
        """
        Detect circular money flows (A → B → C → A)
        
        Args:
            graph: NetworkX graph (if None, builds from DB)
        
        Returns:
            List of circular flow patterns
        """
        if graph is None:
            transactions_df = self._get_all_transactions()
            graph = self.network_engine.build_transaction_graph(transactions_df)
        
        circular_flows = []
        
        try:
            # Find all simple cycles
            cycles = list(nx.simple_cycles(graph))
            
            for cycle in cycles:
                if len(cycle) >= 3:  # At least 3 nodes
                    # Calculate total amount flowing through cycle
                    total_amount = 0
                    for i in range(len(cycle)):
                        next_idx = (i + 1) % len(cycle)
                        edge_data = graph.get_edge_data(cycle[i], cycle[next_idx])
                        if edge_data:
                            total_amount += edge_data.get('weight', 0)
                    
                    circular_flows.append({
                        'cycle': cycle,
                        'length': len(cycle),
                        'total_amount': total_amount,
                        'pattern_type': 'circular_flow'
                    })
            
            # Sort by length and amount
            circular_flows.sort(key=lambda x: (x['length'], x['total_amount']), reverse=True)
            
        except Exception as e:
            print(f"Error detecting circular flows: {e}")
        
        return circular_flows[:50]  # Return top 50
    
    def detect_structuring(self, transactions_df=None, account_id=None):
        """
        Detect structuring (smurfing) - multiple transactions just below reporting threshold
        
        Args:
            transactions_df: DataFrame of transactions (if None, fetches from DB)
            account_id: Optional specific account to analyze
        
        Returns:
            List of structuring patterns
        """
        if transactions_df is None:
            transactions_df = self._get_all_transactions()
        
        if account_id:
            # Filter to transactions involving this account
            transactions_df = transactions_df[
                (transactions_df['from_account'] == account_id) | 
                (transactions_df['to_account'] == account_id)
            ]
        
        if transactions_df.empty:
            return []
        
        # Convert timestamp to datetime
        transactions_df['timestamp'] = pd.to_datetime(transactions_df['timestamp'])
        
        structuring_patterns = []
        
        # Group by account and look for patterns
        accounts = set(transactions_df['from_account'].unique()).union(
            set(transactions_df['to_account'].unique())
        )
        
        for account in accounts:
            # Get outbound transactions from this account
            outbound = transactions_df[transactions_df['from_account'] == account].copy()
            
            if len(outbound) < self.min_structuring_count:
                continue
            
            # Check for transactions near threshold
            near_threshold = outbound[
                (outbound['amount'] >= self.structuring_threshold - self.structuring_tolerance) & 
                (outbound['amount'] <= self.structuring_threshold + self.structuring_tolerance)
            ]
            
            if len(near_threshold) >= self.min_structuring_count:
                # Group by time windows (24 hours)
                near_threshold = near_threshold.sort_values('timestamp')
                
                # Check for clustering in time
                for i in range(len(near_threshold) - self.min_structuring_count + 1):
                    window_txs = []
                    start_time = near_threshold.iloc[i]['timestamp']
                    
                    for j in range(i, len(near_threshold)):
                        tx_time = near_threshold.iloc[j]['timestamp']
                        if (tx_time - start_time).total_seconds() / 3600 <= 72:  # 72-hour window
                            window_txs.append(near_threshold.iloc[j])
                    
                    if len(window_txs) >= self.min_structuring_count:
                        total_amount = sum(tx['amount'] for tx in window_txs)
                        
                        structuring_patterns.append({
                            'account_id': account,
                            'transaction_count': len(window_txs),
                            'total_amount': total_amount,
                            'avg_amount': total_amount / len(window_txs),
                            'time_window_hours': (window_txs[-1]['timestamp'] - window_txs[0]['timestamp']).total_seconds() / 3600,
                            'pattern_type': 'structuring',
                            'transactions': [
                                {
                                    'transaction_id': tx.get('transaction_id', ''),
                                    'amount': tx['amount'],
                                    'timestamp': tx['timestamp'].isoformat()
                                } for tx in window_txs
                            ]
                        })
                        break  # Found pattern for this account
        
        return structuring_patterns
    
    def _get_all_transactions(self):
        """Fetch all transactions from database"""
        try:
            return _db_fetch_all()
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return pd.DataFrame()
    
    def analyze_layering_risk(self, account_id):
        """
        Comprehensive layering risk analysis for an account
        
        Returns:
            Dictionary with all layering-related detections
        """
        # Build graph
        transactions_df = self._get_all_transactions()
        graph = self.network_engine.build_transaction_graph(transactions_df)
        
        # Detect multi-hop paths
        multi_hop = self.detect_multi_hop_paths(graph)
        account_multi_hop = [p for p in multi_hop if account_id in p['path']]
        
        # Detect circular flows
        circular = self.detect_circular_flows(graph)
        account_circular = [c for c in circular if account_id in c['cycle']]
        
        # Detect structuring
        structuring = self.detect_structuring(transactions_df, account_id)
        
        # Calculate layering risk score
        layering_score = self._calculate_layering_score(
            len(account_multi_hop),
            len(account_circular),
            len(structuring)
        )
        
        return {
            'account_id': account_id,
            'multi_hop_paths': len(account_multi_hop),
            'circular_flows': len(account_circular),
            'structuring_patterns': len(structuring),
            'layering_risk_score': layering_score,
            'details': {
                'multi_hop_examples': account_multi_hop[:5],
                'circular_examples': account_circular[:5],
                'structuring_examples': structuring[:5]
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_layering_score(self, multi_hop_count, circular_count, structuring_count):
        """Calculate layering risk score (0-1)"""
        score = 0.0
        
        # Multi-hop involvement
        if multi_hop_count > 0:
            score += min(0.4, multi_hop_count * 0.1)
        
        # Circular flow involvement
        if circular_count > 0:
            score += min(0.35, circular_count * 0.15)
        
        # Structuring patterns
        if structuring_count > 0:
            score += min(0.25, structuring_count * 0.1)
        
        return min(score, 1.0)
