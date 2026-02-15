import networkx as nx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import sys
import os
try:
    import community as community_louvain
except ImportError:
    community_louvain = None

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config

class NetworkEngine:
    """
    Graph-Based Transaction Network Analysis Engine
    Uses NetworkX to build and analyze transaction networks
    """
    
    def __init__(self):
        self.hub_threshold = 10
        self.funnel_threshold = 5
        
    def build_transaction_graph(self, transactions_df=None):
        """
        Build directed graph from transactions
        
        Args:
            transactions_df: DataFrame of transactions (if None, fetches all from DB)
        
        Returns:
            NetworkX DiGraph object
        """
        if transactions_df is None:
            transactions_df = self._get_all_transactions()
        
        G = nx.DiGraph()
        
        # Add edges with attributes
        for _, row in transactions_df.iterrows():
            from_acc = row['from_account']
            to_acc = row['to_account']
            amount = row['amount']
            timestamp = row.get('timestamp', datetime.now().isoformat())
            
            # Add or update edge
            if G.has_edge(from_acc, to_acc):
                # Update existing edge
                G[from_acc][to_acc]['weight'] += amount
                G[from_acc][to_acc]['count'] += 1
                G[from_acc][to_acc]['timestamps'].append(timestamp)
            else:
                # Create new edge
                G.add_edge(from_acc, to_acc, 
                          weight=amount, 
                          count=1,
                          timestamps=[timestamp])
        
        return G
    
    def _get_all_transactions(self):
        """Fetch all transactions from database"""
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            df = pd.read_sql_query("SELECT * FROM transactions", conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return pd.DataFrame()
    
    def compute_network_metrics(self, graph, account_id=None):
        """
        Compute network centrality metrics
        
        Args:
            graph: NetworkX graph
            account_id: Optional specific account (if None, computes for all)
        
        Returns:
            Dictionary of metrics per account
        """
        if graph.number_of_nodes() == 0:
            return {}
        
        metrics = {}
        
        # Degree centrality
        degree_cent = nx.degree_centrality(graph)
        
        # In-degree and out-degree
        in_degree = dict(graph.in_degree())
        out_degree = dict(graph.out_degree())
        
        # Betweenness centrality (computationally expensive for large graphs)
        if graph.number_of_nodes() < 1000:
            betweenness_cent = nx.betweenness_centrality(graph)
        else:
            # Use approximation for large graphs
            betweenness_cent = nx.betweenness_centrality(graph, k=min(100, graph.number_of_nodes()))
        
        # PageRank
        try:
            pagerank = nx.pagerank(graph, max_iter=100)
        except:
            pagerank = {node: 0.0 for node in graph.nodes()}
        
        # Build metrics dictionary
        for node in graph.nodes():
            if account_id and node != account_id:
                continue
                
            metrics[node] = {
                'degree_centrality': degree_cent.get(node, 0.0),
                'in_degree': in_degree.get(node, 0),
                'out_degree': out_degree.get(node, 0),
                'betweenness_centrality': betweenness_cent.get(node, 0.0),
                'pagerank': pagerank.get(node, 0.0)
            }
        
        if account_id:
            return metrics.get(account_id, {})
        
        return metrics
    
    def detect_communities(self, graph):
        """
        Detect communities using Louvain method
        
        Returns:
            Dictionary mapping node to community ID
        """
        if community_louvain is None:
            print("Warning: community package not available, skipping community detection")
            return {}
        
        # Convert to undirected for community detection
        undirected = graph.to_undirected()
        
        try:
            communities = community_louvain.best_partition(undirected)
            return communities
        except Exception as e:
            print(f"Community detection failed: {e}")
            return {}
    
    def detect_hub_and_spoke(self, graph, account_id=None):
        """
        Detect hub-and-spoke patterns
        One central node with many outgoing connections to low-degree nodes
        
        Returns:
            List of hub accounts with their spoke counts
        """
        hubs = []
        
        nodes_to_check = [account_id] if account_id else graph.nodes()
        
        for node in nodes_to_check:
            if node not in graph:
                continue
                
            out_degree = graph.out_degree(node)
            
            if out_degree >= self.hub_threshold:
                # Check if connected nodes have low degree (spokes)
                neighbors = list(graph.successors(node))
                low_degree_neighbors = sum(
                    1 for n in neighbors 
                    if graph.out_degree(n) <= 2
                )
                
                if low_degree_neighbors >= self.hub_threshold * 0.7:
                    hubs.append({
                        'account_id': node,
                        'out_degree': out_degree,
                        'spoke_count': low_degree_neighbors,
                        'pattern': 'hub_and_spoke'
                    })
        
        return hubs
    
    def detect_funnel_accounts(self, graph, account_id=None):
        """
        Detect funnel patterns
        Many inbound edges, few outbound (aggregation point)
        
        Returns:
            List of funnel accounts
        """
        funnels = []
        
        nodes_to_check = [account_id] if account_id else graph.nodes()
        
        for node in nodes_to_check:
            if node not in graph:
                continue
                
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            
            # Funnel: many in, few out
            if in_degree >= self.funnel_threshold and out_degree <= 2:
                funnels.append({
                    'account_id': node,
                    'in_degree': in_degree,
                    'out_degree': out_degree,
                    'funnel_ratio': in_degree / max(out_degree, 1),
                    'pattern': 'funnel'
                })
        
        return funnels
    
    def detect_layering_chains(self, graph, min_path_length=3):
        """
        Detect layering chains (paths of length >= min_path_length)
        
        Returns:
            List of suspicious paths
        """
        chains = []
        
        # Sample nodes to avoid exponential explosion
        nodes = list(graph.nodes())
        sample_size = min(50, len(nodes))
        sample_nodes = np.random.choice(nodes, sample_size, replace=False) if len(nodes) > sample_size else nodes
        
        for source in sample_nodes:
            for target in sample_nodes:
                if source == target:
                    continue
                
                try:
                    # Find all simple paths up to length 6
                    paths = list(nx.all_simple_paths(graph, source, target, cutoff=6))
                    
                    for path in paths:
                        if len(path) >= min_path_length:
                            # Calculate total amount through path
                            total_amount = 0
                            for i in range(len(path) - 1):
                                edge_data = graph.get_edge_data(path[i], path[i+1])
                                if edge_data:
                                    total_amount += edge_data.get('weight', 0)
                            
                            chains.append({
                                'path': path,
                                'length': len(path),
                                'total_amount': total_amount,
                                'pattern': 'layering_chain'
                            })
                except nx.NetworkXNoPath:
                    continue
                except Exception:
                    continue
        
        # Sort by length and amount
        chains.sort(key=lambda x: (x['length'], x['total_amount']), reverse=True)
        
        return chains[:100]  # Return top 100 chains
    
    def analyze_account_network(self, account_id):
        """
        Complete network analysis for a specific account
        
        Returns:
            Comprehensive network analysis results
        """
        # Build graph
        graph = self.build_transaction_graph()
        
        if account_id not in graph:
            return {
                'account_id': account_id,
                'error': 'Account not found in transaction network'
            }
        
        # Compute metrics
        metrics = self.compute_network_metrics(graph, account_id)
        
        # Check patterns
        is_hub = len(self.detect_hub_and_spoke(graph, account_id)) > 0
        is_funnel = len(self.detect_funnel_accounts(graph, account_id)) > 0
        
        # Get layering chains involving this account
        all_chains = self.detect_layering_chains(graph)
        account_chains = [
            chain for chain in all_chains 
            if account_id in chain['path']
        ]
        
        return {
            'account_id': account_id,
            'metrics': metrics,
            'is_hub': is_hub,
            'is_funnel': is_funnel,
            'layering_chains': len(account_chains),
            'network_risk_score': self._calculate_network_risk(metrics, is_hub, is_funnel, len(account_chains)),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_network_risk(self, metrics, is_hub, is_funnel, chain_count):
        """Calculate network-based risk score (0-1)"""
        score = 0.0
        
        # High betweenness centrality
        if metrics.get('betweenness_centrality', 0) > 0.1:
            score += 0.3
        
        # Hub pattern
        if is_hub:
            score += 0.25
        
        # Funnel pattern
        if is_funnel:
            score += 0.25
        
        # Involved in layering chains
        if chain_count > 0:
            score += min(0.2, chain_count * 0.05)
        
        return min(score, 1.0)
    
    def get_network_visualization_data(self):
        """
        Prepare network data for D3.js visualization
        
        Returns:
            Dictionary with nodes and links for visualization
        """
        graph = self.build_transaction_graph()
        metrics = self.compute_network_metrics(graph)
        
        # Prepare nodes
        nodes = []
        for node_id in graph.nodes():
            node_metrics = metrics.get(node_id, {})
            nodes.append({
                'id': node_id,
                'degree': graph.degree(node_id),
                'betweenness': node_metrics.get('betweenness_centrality', 0),
                'pagerank': node_metrics.get('pagerank', 0)
            })
        
        # Prepare links
        links = []
        for source, target, data in graph.edges(data=True):
            links.append({
                'source': source,
                'target': target,
                'weight': data.get('weight', 0),
                'count': data.get('count', 1)
            })
        
        return {
            'nodes': nodes,
            'links': links
        }
