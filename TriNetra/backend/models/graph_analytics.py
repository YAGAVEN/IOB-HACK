"""
Graph Analytics Engine
Graph centrality metrics and community detection for transaction networks
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import community as community_louvain  # python-louvain
from dataclasses import dataclass

@dataclass
class GraphMetrics:
    """Container for graph-level metrics"""
    n_nodes: int
    n_edges: int
    density: float
    avg_clustering: float
    n_components: int
    avg_degree: float
    diameter: Optional[int] = None

class GraphAnalyticsEngine:
    """
    Graph analytics engine for transaction network analysis
    Provides centrality metrics and community detection
    """
    
    def __init__(self):
        self.graph = None
        self.metrics_cache = {}
        self.communities = None
    
    def build_graph_from_transactions(self, transactions: List[Dict]):
        """
        Build graph from transaction data
        
        Args:
            transactions: List of transaction dictionaries with 'from', 'to', 'amount'
            
        Returns:
            graph: NetworkX directed graph
        """
        self.graph = nx.DiGraph()
        
        for txn in transactions:
            from_account = txn.get('from_account') or txn.get('from')
            to_account = txn.get('to_account') or txn.get('to')
            amount = txn.get('amount', 0)
            
            if from_account and to_account:
                if self.graph.has_edge(from_account, to_account):
                    # Update existing edge
                    self.graph[from_account][to_account]['weight'] += amount
                    self.graph[from_account][to_account]['count'] += 1
                else:
                    # Create new edge
                    self.graph.add_edge(from_account, to_account, weight=amount, count=1)
        
        self.metrics_cache.clear()
        return self.graph
    
    def get_graph_metrics(self) -> GraphMetrics:
        """
        Calculate overall graph metrics
        
        Returns:
            metrics: GraphMetrics object
        """
        if self.graph is None:
            raise ValueError("Graph not initialized. Call build_graph_from_transactions first.")
        
        n_nodes = self.graph.number_of_nodes()
        n_edges = self.graph.number_of_edges()
        
        # Convert to undirected for some metrics
        undirected = self.graph.to_undirected()
        
        metrics = GraphMetrics(
            n_nodes=n_nodes,
            n_edges=n_edges,
            density=nx.density(self.graph),
            avg_clustering=nx.average_clustering(undirected),
            n_components=nx.number_weakly_connected_components(self.graph),
            avg_degree=sum(dict(self.graph.degree()).values()) / n_nodes if n_nodes > 0 else 0
        )
        
        # Diameter (expensive for large graphs)
        if n_nodes < 1000:
            try:
                largest_cc = max(nx.weakly_connected_components(self.graph), key=len)
                subgraph = self.graph.subgraph(largest_cc)
                metrics.diameter = nx.diameter(subgraph.to_undirected())
            except:
                metrics.diameter = None
        
        return metrics
    
    def calculate_degree_centrality(self) -> Dict[str, float]:
        """
        Calculate degree centrality for all nodes
        Measures number of direct connections
        
        Returns:
            centrality: Dictionary mapping node_id to centrality score
        """
        if 'degree_centrality' not in self.metrics_cache:
            self.metrics_cache['degree_centrality'] = nx.degree_centrality(self.graph)
        return self.metrics_cache['degree_centrality']
    
    def calculate_in_degree_centrality(self) -> Dict[str, float]:
        """
        Calculate in-degree centrality (incoming connections)
        
        Returns:
            centrality: Dictionary mapping node_id to centrality score
        """
        if 'in_degree_centrality' not in self.metrics_cache:
            self.metrics_cache['in_degree_centrality'] = nx.in_degree_centrality(self.graph)
        return self.metrics_cache['in_degree_centrality']
    
    def calculate_out_degree_centrality(self) -> Dict[str, float]:
        """
        Calculate out-degree centrality (outgoing connections)
        
        Returns:
            centrality: Dictionary mapping node_id to centrality score
        """
        if 'out_degree_centrality' not in self.metrics_cache:
            self.metrics_cache['out_degree_centrality'] = nx.out_degree_centrality(self.graph)
        return self.metrics_cache['out_degree_centrality']
    
    def calculate_betweenness_centrality(self, sample_size: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate betweenness centrality for all nodes
        Measures how often a node acts as a bridge between other nodes
        
        Args:
            sample_size: For large graphs, use sampling (None = exact)
            
        Returns:
            centrality: Dictionary mapping node_id to centrality score
        """
        if 'betweenness_centrality' not in self.metrics_cache:
            if sample_size and self.graph.number_of_nodes() > 1000:
                # Use sampling for large graphs
                k = min(sample_size, self.graph.number_of_nodes())
                self.metrics_cache['betweenness_centrality'] = nx.betweenness_centrality(
                    self.graph, k=k, normalized=True
                )
            else:
                self.metrics_cache['betweenness_centrality'] = nx.betweenness_centrality(
                    self.graph, normalized=True
                )
        return self.metrics_cache['betweenness_centrality']
    
    def calculate_closeness_centrality(self) -> Dict[str, float]:
        """
        Calculate closeness centrality for all nodes
        Measures average distance to all other nodes
        
        Returns:
            centrality: Dictionary mapping node_id to centrality score
        """
        if 'closeness_centrality' not in self.metrics_cache:
            try:
                self.metrics_cache['closeness_centrality'] = nx.closeness_centrality(self.graph)
            except:
                # For disconnected graphs
                self.metrics_cache['closeness_centrality'] = {}
                for component in nx.weakly_connected_components(self.graph):
                    subgraph = self.graph.subgraph(component)
                    closeness = nx.closeness_centrality(subgraph)
                    self.metrics_cache['closeness_centrality'].update(closeness)
        
        return self.metrics_cache['closeness_centrality']
    
    def calculate_pagerank(self, alpha=0.85, max_iter=100) -> Dict[str, float]:
        """
        Calculate PageRank for all nodes
        Measures importance based on incoming links
        
        Args:
            alpha: Damping parameter (default: 0.85)
            max_iter: Maximum iterations
            
        Returns:
            pagerank: Dictionary mapping node_id to PageRank score
        """
        if 'pagerank' not in self.metrics_cache:
            self.metrics_cache['pagerank'] = nx.pagerank(
                self.graph, alpha=alpha, max_iter=max_iter
            )
        return self.metrics_cache['pagerank']
    
    def calculate_eigenvector_centrality(self, max_iter=100) -> Dict[str, float]:
        """
        Calculate eigenvector centrality for all nodes
        Measures influence based on connections to influential nodes
        
        Args:
            max_iter: Maximum iterations
            
        Returns:
            centrality: Dictionary mapping node_id to centrality score
        """
        if 'eigenvector_centrality' not in self.metrics_cache:
            try:
                self.metrics_cache['eigenvector_centrality'] = nx.eigenvector_centrality(
                    self.graph, max_iter=max_iter
                )
            except:
                # Fallback for graphs where eigenvector doesn't converge
                self.metrics_cache['eigenvector_centrality'] = {
                    node: 0.0 for node in self.graph.nodes()
                }
        return self.metrics_cache['eigenvector_centrality']
    
    def identify_hubs(self, threshold=0.7) -> List[str]:
        """
        Identify hub nodes (high out-degree)
        
        Args:
            threshold: Centrality threshold for hub classification
            
        Returns:
            hubs: List of hub node IDs
        """
        out_degree = self.calculate_out_degree_centrality()
        hubs = [node for node, centrality in out_degree.items() if centrality >= threshold]
        return hubs
    
    def identify_funnels(self, threshold=0.7) -> List[str]:
        """
        Identify funnel nodes (high in-degree)
        
        Args:
            threshold: Centrality threshold for funnel classification
            
        Returns:
            funnels: List of funnel node IDs
        """
        in_degree = self.calculate_in_degree_centrality()
        funnels = [node for node, centrality in in_degree.items() if centrality >= threshold]
        return funnels
    
    def identify_bridges(self, threshold=0.7) -> List[str]:
        """
        Identify bridge nodes (high betweenness)
        
        Args:
            threshold: Centrality threshold for bridge classification
            
        Returns:
            bridges: List of bridge node IDs
        """
        betweenness = self.calculate_betweenness_centrality()
        bridges = [node for node, centrality in betweenness.items() if centrality >= threshold]
        return bridges
    
    def detect_communities_louvain(self, resolution=1.0) -> Dict[str, int]:
        """
        Detect communities using Louvain algorithm
        
        Args:
            resolution: Resolution parameter (higher = more communities)
            
        Returns:
            communities: Dictionary mapping node_id to community_id
        """
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        self.communities = community_louvain.best_partition(undirected, resolution=resolution)
        return self.communities
    
    def get_community_stats(self) -> Dict:
        """
        Get statistics about detected communities
        
        Returns:
            stats: Dictionary with community statistics
        """
        if self.communities is None:
            raise ValueError("Communities not detected. Call detect_communities_louvain first.")
        
        community_sizes = defaultdict(int)
        for node, comm_id in self.communities.items():
            community_sizes[comm_id] += 1
        
        n_communities = len(community_sizes)
        sizes = list(community_sizes.values())
        
        return {
            'n_communities': n_communities,
            'avg_community_size': np.mean(sizes),
            'min_community_size': min(sizes),
            'max_community_size': max(sizes),
            'community_size_std': np.std(sizes),
            'modularity': community_louvain.modularity(self.communities, self.graph.to_undirected())
        }
    
    def get_node_all_centralities(self, node_id: str) -> Dict[str, float]:
        """
        Get all centrality metrics for a specific node
        
        Args:
            node_id: Node identifier
            
        Returns:
            centralities: Dictionary of all centrality metrics
        """
        return {
            'degree_centrality': self.calculate_degree_centrality().get(node_id, 0),
            'in_degree_centrality': self.calculate_in_degree_centrality().get(node_id, 0),
            'out_degree_centrality': self.calculate_out_degree_centrality().get(node_id, 0),
            'betweenness_centrality': self.calculate_betweenness_centrality().get(node_id, 0),
            'closeness_centrality': self.calculate_closeness_centrality().get(node_id, 0),
            'pagerank': self.calculate_pagerank().get(node_id, 0),
            'eigenvector_centrality': self.calculate_eigenvector_centrality().get(node_id, 0)
        }
    
    def get_top_nodes_by_centrality(self, metric='pagerank', top_k=10) -> List[Tuple[str, float]]:
        """
        Get top-k nodes by centrality metric
        
        Args:
            metric: Centrality metric name
            top_k: Number of top nodes to return
            
        Returns:
            top_nodes: List of (node_id, score) tuples
        """
        metric_functions = {
            'degree': self.calculate_degree_centrality,
            'in_degree': self.calculate_in_degree_centrality,
            'out_degree': self.calculate_out_degree_centrality,
            'betweenness': self.calculate_betweenness_centrality,
            'closeness': self.calculate_closeness_centrality,
            'pagerank': self.calculate_pagerank,
            'eigenvector': self.calculate_eigenvector_centrality
        }
        
        if metric not in metric_functions:
            raise ValueError(f"Unknown metric: {metric}")
        
        centrality = metric_functions[metric]()
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_nodes[:top_k]
    
    def find_cycles(self, max_length=10) -> List[List[str]]:
        """
        Find circular transaction flows (cycles)
        
        Args:
            max_length: Maximum cycle length to search
            
        Returns:
            cycles: List of cycles (each cycle is a list of nodes)
        """
        cycles = []
        
        try:
            # Find simple cycles
            simple_cycles = list(nx.simple_cycles(self.graph))
            
            # Filter by length
            cycles = [cycle for cycle in simple_cycles if len(cycle) <= max_length]
            
        except:
            pass
        
        return cycles
    
    def find_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between two nodes
        
        Args:
            source: Source node ID
            target: Target node ID
            
        Returns:
            path: List of nodes in path (None if no path exists)
        """
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return None


if __name__ == "__main__":
    print("Graph Analytics Engine Test\n")
    
    # Create sample transactions
    transactions = [
        {'from': 'A1', 'to': 'A2', 'amount': 1000},
        {'from': 'A1', 'to': 'A3', 'amount': 2000},
        {'from': 'A2', 'to': 'A4', 'amount': 500},
        {'from': 'A3', 'to': 'A4', 'amount': 1500},
        {'from': 'A4', 'to': 'A5', 'amount': 3000},
        {'from': 'A5', 'to': 'A1', 'amount': 500},  # Circular flow
        {'from': 'A2', 'to': 'A6', 'amount': 800},
        {'from': 'A3', 'to': 'A6', 'amount': 1200},
        {'from': 'A6', 'to': 'A7', 'amount': 2000},
    ]
    
    # Initialize engine
    engine = GraphAnalyticsEngine()
    graph = engine.build_graph_from_transactions(transactions)
    
    print(f"Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges\n")
    
    # Graph metrics
    metrics = engine.get_graph_metrics()
    print("Graph Metrics:")
    print(f"  Density: {metrics.density:.3f}")
    print(f"  Avg Clustering: {metrics.avg_clustering:.3f}")
    print(f"  Components: {metrics.n_components}")
    print(f"  Avg Degree: {metrics.avg_degree:.2f}\n")
    
    # PageRank
    pagerank = engine.calculate_pagerank()
    print("PageRank Scores:")
    for node, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
        print(f"  {node}: {score:.4f}")
    
    # Betweenness
    print("\nBetweenness Centrality:")
    betweenness = engine.calculate_betweenness_centrality()
    for node, score in sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {node}: {score:.4f}")
    
    # Communities
    print("\nDetecting communities...")
    communities = engine.detect_communities_louvain()
    stats = engine.get_community_stats()
    print(f"  Found {stats['n_communities']} communities")
    print(f"  Modularity: {stats['modularity']:.3f}")
    
    # Cycles
    cycles = engine.find_cycles()
    print(f"\nFound {len(cycles)} cycles")
    for i, cycle in enumerate(cycles[:3]):
        print(f"  Cycle {i+1}: {' -> '.join(cycle + [cycle[0]])}")
