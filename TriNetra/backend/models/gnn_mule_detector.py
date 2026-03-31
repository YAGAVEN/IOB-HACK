"""
Graph Convolutional Network (GCN) for Money Mule Detection
Graph deep learning for transaction network node classification
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from typing import Dict, List, Tuple, Optional
import networkx as nx

class GCNLayer(nn.Module):
    """
    Graph Convolutional Layer
    Implements GCN as described in Kipf & Welling (2017)
    """
    
    def __init__(self, in_features, out_features, use_bias=True):
        super(GCNLayer, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if use_bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.weight)
        if self.bias is not None:
            nn.init.zeros_(self.bias)
    
    def forward(self, X, A):
        """
        Forward pass
        
        Args:
            X: Node features (n_nodes, in_features)
            A: Normalized adjacency matrix (n_nodes, n_nodes)
            
        Returns:
            H: Output features (n_nodes, out_features)
        """
        support = torch.mm(X, self.weight)
        output = torch.mm(A, support)
        
        if self.bias is not None:
            output = output + self.bias
        
        return output

class GCN_MuleDetector(nn.Module):
    """
    Graph Convolutional Network for Money Mule Detection
    Multi-layer GCN for node classification
    """
    
    def __init__(self, 
                 n_features, 
                 n_hidden1=64, 
                 n_hidden2=32, 
                 n_classes=2, 
                 dropout=0.5):
        super(GCN_MuleDetector, self).__init__()
        
        self.gcn1 = GCNLayer(n_features, n_hidden1)
        self.gcn2 = GCNLayer(n_hidden1, n_hidden2)
        self.gcn3 = GCNLayer(n_hidden2, n_classes)
        
        self.dropout = dropout
    
    def forward(self, X, A):
        """
        Forward pass through GCN
        
        Args:
            X: Node features
            A: Normalized adjacency matrix
            
        Returns:
            Output logits for classification
        """
        # First GCN layer
        H = self.gcn1(X, A)
        H = F.relu(H)
        H = F.dropout(H, self.dropout, training=self.training)
        
        # Second GCN layer
        H = self.gcn2(H, A)
        H = F.relu(H)
        H = F.dropout(H, self.dropout, training=self.training)
        
        # Output layer
        H = self.gcn3(H, A)
        
        return F.log_softmax(H, dim=1)

class GNN_MuleDetectionSystem:
    """
    Complete GNN-based Money Mule Detection System
    """
    
    def __init__(self, n_features, device='cpu'):
        """
        Initialize GNN detection system
        
        Args:
            n_features: Number of node features
            device: 'cpu' or 'cuda'
        """
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.n_features = n_features
        
        self.model = GCN_MuleDetector(
            n_features=n_features,
            n_hidden1=64,
            n_hidden2=32,
            n_classes=2,
            dropout=0.5
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01, weight_decay=5e-4)
        self.criterion = nn.NLLLoss()
        
        self.is_trained = False
        self.training_history = {
            'train_losses': [],
            'val_losses': [],
            'train_accuracies': [],
            'val_accuracies': [],
            'epochs': 0
        }
    
    def normalize_adjacency(self, A):
        """
        Normalize adjacency matrix using symmetric normalization
        A_norm = D^(-1/2) * A * D^(-1/2)
        
        Args:
            A: Adjacency matrix (torch tensor)
            
        Returns:
            A_norm: Normalized adjacency matrix
        """
        # Add self-loops
        A = A + torch.eye(A.size(0)).to(A.device)
        
        # Degree matrix
        D = torch.sum(A, dim=1)
        D_inv_sqrt = torch.pow(D, -0.5)
        D_inv_sqrt[torch.isinf(D_inv_sqrt)] = 0.0
        
        D_inv_sqrt = torch.diag(D_inv_sqrt)
        
        # Symmetric normalization
        A_norm = torch.mm(torch.mm(D_inv_sqrt, A), D_inv_sqrt)
        
        return A_norm
    
    def train(self, X, A, y, train_mask, val_mask, epochs=200):
        """
        Train the GCN model
        
        Args:
            X: Node features (n_nodes, n_features)
            A: Adjacency matrix (n_nodes, n_nodes)
            y: Node labels (n_nodes,)
            train_mask: Training node mask
            val_mask: Validation node mask
            epochs: Number of training epochs
            
        Returns:
            training_history: Training metrics
        """
        # Convert to tensors
        if isinstance(X, np.ndarray):
            X = torch.FloatTensor(X).to(self.device)
        if isinstance(A, np.ndarray):
            A = torch.FloatTensor(A).to(self.device)
        if isinstance(y, np.ndarray):
            y = torch.LongTensor(y).to(self.device)
        if isinstance(train_mask, np.ndarray):
            train_mask = torch.BoolTensor(train_mask).to(self.device)
        if isinstance(val_mask, np.ndarray):
            val_mask = torch.BoolTensor(val_mask).to(self.device)
        
        # Normalize adjacency matrix
        A_norm = self.normalize_adjacency(A)
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            self.optimizer.zero_grad()
            
            output = self.model(X, A_norm)
            loss_train = self.criterion(output[train_mask], y[train_mask])
            
            loss_train.backward()
            self.optimizer.step()
            
            # Validation
            self.model.eval()
            with torch.no_grad():
                output = self.model(X, A_norm)
                loss_val = self.criterion(output[val_mask], y[val_mask])
                
                # Accuracy
                pred_train = output[train_mask].max(1)[1]
                acc_train = pred_train.eq(y[train_mask]).sum().item() / train_mask.sum().item()
                
                pred_val = output[val_mask].max(1)[1]
                acc_val = pred_val.eq(y[val_mask]).sum().item() / val_mask.sum().item()
            
            # Record metrics
            self.training_history['train_losses'].append(loss_train.item())
            self.training_history['val_losses'].append(loss_val.item())
            self.training_history['train_accuracies'].append(acc_train)
            self.training_history['val_accuracies'].append(acc_val)
            self.training_history['epochs'] += 1
            
            if (epoch + 1) % 20 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - "
                      f"Train Loss: {loss_train.item():.4f}, "
                      f"Val Loss: {loss_val.item():.4f}, "
                      f"Train Acc: {acc_train:.4f}, "
                      f"Val Acc: {acc_val:.4f}")
        
        self.is_trained = True
        return self.training_history
    
    def predict(self, X, A):
        """
        Predict node classes
        
        Args:
            X: Node features
            A: Adjacency matrix
            
        Returns:
            predictions: Class predictions
            probabilities: Class probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        self.model.eval()
        
        if isinstance(X, np.ndarray):
            X = torch.FloatTensor(X).to(self.device)
        if isinstance(A, np.ndarray):
            A = torch.FloatTensor(A).to(self.device)
        
        A_norm = self.normalize_adjacency(A)
        
        with torch.no_grad():
            output = self.model(X, A_norm)
            probabilities = torch.exp(output)
            predictions = output.max(1)[1]
        
        return predictions.cpu().numpy(), probabilities.cpu().numpy()
    
    def get_mule_risk_scores(self, X, A):
        """
        Get mule risk scores for all nodes
        
        Args:
            X: Node features
            A: Adjacency matrix
            
        Returns:
            risk_scores: Probability of being a mule (0-1)
        """
        predictions, probabilities = self.predict(X, A)
        return probabilities[:, 1]  # Probability of class 1 (mule)
    
    def evaluate(self, X, A, y, test_mask):
        """
        Evaluate model on test set
        
        Args:
            X: Node features
            A: Adjacency matrix
            y: True labels
            test_mask: Test node mask
            
        Returns:
            metrics: Evaluation metrics
        """
        predictions, probabilities = self.predict(X, A)
        
        if isinstance(y, np.ndarray):
            y_test = y[test_mask]
        else:
            y_test = y[test_mask].cpu().numpy()
        
        pred_test = predictions[test_mask]
        proba_test = probabilities[test_mask]
        
        accuracy = (pred_test == y_test).mean()
        
        # Calculate precision, recall, F1
        tp = ((pred_test == 1) & (y_test == 1)).sum()
        fp = ((pred_test == 1) & (y_test == 0)).sum()
        fn = ((pred_test == 0) & (y_test == 1)).sum()
        tn = ((pred_test == 0) & (y_test == 0)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'confusion_matrix': {
                'tp': int(tp),
                'fp': int(fp),
                'fn': int(fn),
                'tn': int(tn)
            }
        }
    
    def save_model(self, filepath):
        """Save trained model"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_history': self.training_history,
            'n_features': self.n_features,
            'is_trained': self.is_trained
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.training_history = checkpoint['training_history']
        self.is_trained = checkpoint['is_trained']
        
        print(f"Model loaded from {filepath}")


def generate_synthetic_graph(n_nodes=100, n_features=10, mule_ratio=0.3):
    """
    Generate synthetic transaction graph for testing
    
    Args:
        n_nodes: Number of nodes (accounts)
        n_features: Number of features per node
        mule_ratio: Ratio of mule accounts
        
    Returns:
        X: Node features
        A: Adjacency matrix
        y: Node labels
        train_mask, val_mask, test_mask: Data splits
    """
    # Generate graph structure
    G = nx.erdos_renyi_graph(n_nodes, 0.05)
    A = nx.adjacency_matrix(G).todense()
    A = np.array(A, dtype=np.float32)
    
    # Generate features
    n_mules = int(n_nodes * mule_ratio)
    n_normal = n_nodes - n_mules
    
    # Normal account features
    X_normal = np.random.randn(n_normal, n_features) * 0.5
    
    # Mule account features (higher risk indicators)
    X_mule = np.random.randn(n_mules, n_features) * 0.5 + 1.5
    
    X = np.vstack([X_normal, X_mule])
    y = np.array([0] * n_normal + [1] * n_mules)
    
    # Shuffle
    indices = np.random.permutation(n_nodes)
    X = X[indices]
    y = y[indices]
    A = A[indices][:, indices]
    
    # Create masks
    train_size = int(0.6 * n_nodes)
    val_size = int(0.2 * n_nodes)
    
    train_mask = np.zeros(n_nodes, dtype=bool)
    val_mask = np.zeros(n_nodes, dtype=bool)
    test_mask = np.zeros(n_nodes, dtype=bool)
    
    train_mask[:train_size] = True
    val_mask[train_size:train_size + val_size] = True
    test_mask[train_size + val_size:] = True
    
    return X, A, y, train_mask, val_mask, test_mask


if __name__ == "__main__":
    print("GNN Money Mule Detection System Test\n")
    
    # Generate synthetic graph
    print("Generating synthetic transaction graph...")
    X, A, y, train_mask, val_mask, test_mask = generate_synthetic_graph(
        n_nodes=200, n_features=10, mule_ratio=0.3
    )
    print(f"Graph: {X.shape[0]} nodes, {A.sum()} edges, {y.sum()} mules")
    
    # Initialize and train model
    print("\nTraining GCN model...")
    gnn = GNN_MuleDetectionSystem(n_features=10, device='cpu')
    
    history = gnn.train(X, A, y, train_mask, val_mask, epochs=100)
    
    # Evaluate
    print("\nEvaluating on test set...")
    metrics = gnn.evaluate(X, A, y, test_mask)
    
    print(f"\nTest Results:")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall: {metrics['recall']:.4f}")
    print(f"  F1 Score: {metrics['f1_score']:.4f}")
    
    # Get risk scores
    risk_scores = gnn.get_mule_risk_scores(X, A)
    print(f"\nRisk Score Statistics:")
    print(f"  Mean: {risk_scores.mean():.4f}")
    print(f"  Std: {risk_scores.std():.4f}")
    print(f"  Min: {risk_scores.min():.4f}")
    print(f"  Max: {risk_scores.max():.4f}")
