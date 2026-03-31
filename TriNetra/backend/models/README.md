# Models Directory

This directory contains all ML/DL models and analytics engines for money mule detection and risk scoring.

## Directory Structure

```
models/
├── __init__.py                 # Package initialization
├── model_manager.py            # Central model management system
│
├── ML Models (Currently Used)
│   ├── random_forest_mule.py   # Random Forest classifier with SHAP
│   └── risk_scoring_model.py   # Rule-based risk scoring model
│
├── DL Models (Required/Planned)
│   ├── hydra_gan.py            # GAN for adversarial pattern generation
│   └── gnn_mule_detector.py    # GNN/GCN for graph-based detection
│
└── Supporting Analytics
    ├── graph_analytics.py       # Graph centrality & community detection
    └── shap_explainer.py        # SHAP explainability engine
```

## Models Overview

### 1. Random Forest Classifier (`random_forest_mule.py`)
**Purpose**: Mule account detection with explainability

**Features**:
- Sklearn-based Random Forest with balanced class weights
- 14 behavioral, network, layering, and velocity features
- SHAP integration for explainable predictions
- Model persistence (save/load)
- Synthetic data generation for testing

**Usage**:
```python
from models import MuleDetectionRandomForest

model = MuleDetectionRandomForest()
X, y = model.generate_training_data(n_samples=1000)
metrics = model.train(X, y)
risk_score = model.get_mule_risk_score(X_test)
```

### 2. Rule-based Risk Scoring (`risk_scoring_model.py`)
**Purpose**: Weighted ensemble logic for multi-dimensional risk scoring

**Risk Dimensions**:
- **Behavioral** (30%): Rapid in-out, dormancy activation, structuring
- **Network** (25%): Degree, betweenness, PageRank, hub/funnel status
- **Layering** (25%): Multi-hop, circular flow, integration depth
- **Velocity** (20%): Transaction rate, amount velocity, spikes

**Usage**:
```python
from models import RulBasedRiskScoringModel

scorer = RulBasedRiskScoringModel()
result = scorer.calculate_risk_score(features)
# Returns: final_score, risk_level, dimension_scores, contributions
```

### 3. HYDRA GAN (`hydra_gan.py`)
**Purpose**: Adversarial pattern generation and detection

**Components**:
- **Generator**: Creates synthetic money laundering patterns
- **Discriminator**: Detects real vs. generated patterns
- Supports 8 pattern types (smurfing, layering, crypto mixing, etc.)

**Usage**:
```python
from models import HYDRA_GAN

gan = HYDRA_GAN(latent_dim=100, pattern_dim=50)
gan.train(real_patterns, epochs=100)
adversarial_pattern = gan.generate_adversarial_pattern()
detection = gan.detect_pattern(pattern_vector)
```

### 4. GNN Mule Detector (`gnn_mule_detector.py`)
**Purpose**: Graph neural network for transaction network classification

**Architecture**:
- 3-layer Graph Convolutional Network (GCN)
- Node classification (mule vs. normal)
- Leverages network structure and node features
- Symmetric adjacency normalization

**Usage**:
```python
from models import GNN_MuleDetectionSystem

gnn = GNN_MuleDetectionSystem(n_features=10)
gnn.train(X, A, y, train_mask, val_mask, epochs=200)
risk_scores = gnn.get_mule_risk_scores(X, A)
```

### 5. Graph Analytics Engine (`graph_analytics.py`)
**Purpose**: Network analysis with centrality metrics and community detection

**Features**:
- **Centrality Metrics**: Degree, betweenness, closeness, PageRank, eigenvector
- **Community Detection**: Louvain algorithm
- **Pattern Detection**: Cycles, hubs, funnels, bridges
- **Graph Metrics**: Density, clustering, components, diameter

**Usage**:
```python
from models import GraphAnalyticsEngine

engine = GraphAnalyticsEngine()
graph = engine.build_graph_from_transactions(transactions)
pagerank = engine.calculate_pagerank()
communities = engine.detect_communities_louvain()
cycles = engine.find_cycles()
```

### 6. SHAP Explainer (`shap_explainer.py`)
**Purpose**: Model-agnostic explainability using SHAP values

**Features**:
- Tree explainer for Random Forest
- Kernel explainer for any model
- Feature contribution analysis
- Global feature importance
- Human-readable explanations

**Usage**:
```python
from models import SHAPExplainer

explainer = SHAPExplainer(model, feature_names)
explainer.fit(X_train, explainer_type='tree')
explanation = explainer.explain_prediction(X_test)
importance = explainer.get_global_feature_importance(X_train)
```

## Model Manager

The `ModelManager` class provides a unified interface for all models:

```python
from models import ModelManager

# Initialize
manager = ModelManager()

# Train models
manager.initialize_random_forest()
manager.train_random_forest(X, y)

manager.initialize_hydra_gan()
manager.train_hydra_gan(patterns)

# Predictions
rf_result = manager.predict_mule_risk_rf(features)
rule_risk = manager.calculate_rule_based_risk(features)

# Comprehensive assessment
assessment = manager.get_comprehensive_risk_assessment(
    account_id='ACC123',
    features=features
)

# Save models
manager.save_all_models()
```

## Dependencies

```bash
# Core ML
numpy
pandas
scikit-learn
joblib

# Deep Learning
torch
torch-geometric  # For GNN

# Graph Analytics
networkx
python-louvain

# Explainability
shap

# Optional
matplotlib  # For visualizations
seaborn     # For plots
```

Install all dependencies:
```bash
pip install numpy pandas scikit-learn torch networkx python-louvain shap joblib
```

## Testing

Test individual models:
```bash
# Test Random Forest
python -m models.random_forest_mule

# Test Rule-based Scorer
python -m models.risk_scoring_model

# Test HYDRA GAN
python -m models.hydra_gan

# Test GNN
python -m models.gnn_mule_detector

# Test Graph Analytics
python -m models.graph_analytics

# Test SHAP Explainer
python -m models.shap_explainer

# Test Model Manager
python -m models.model_manager
```

Or run the comprehensive test suite:
```bash
python test_models.py
```

## Feature Schema

All models expect features in the following schema:

```python
features = {
    # Behavioral
    'transaction_velocity': float,      # Transactions per day
    'in_out_ratio': float,              # Inflow/outflow ratio
    'account_age_days': int,            # Account age in days
    'rapid_in_out': int,                # Binary: rapid in-out pattern
    'dormant_activation': int,          # Binary: dormant reactivation
    'high_throughput': int,             # Binary: high volume
    'structuring_count': int,           # Number of structuring patterns
    
    # Network
    'degree_centrality': float,         # Normalized degree centrality
    'betweenness_centrality': float,    # Normalized betweenness
    'pagerank': float,                  # PageRank score
    'is_hub': int,                      # Binary: hub node
    'is_funnel': int,                   # Binary: funnel node
    
    # Layering
    'multi_hop_count': int,             # Number of multi-hop paths
    'circular_flow_count': int,         # Number of circular flows
    'integration_depth': int,           # Integration layer depth
    
    # Velocity (optional)
    'amount_velocity': float,           # $ per day
    'avg_velocity': float,              # Historical average
    'total_throughput': float,          # Total transaction volume
}
```

## Model Performance

### Random Forest (1000 samples, 30/70 mule/normal split)
- Accuracy: ~0.92
- ROC AUC: ~0.95
- Top Features: transaction_velocity, rapid_in_out, degree_centrality

### GNN (200 nodes, 30% mule ratio)
- Accuracy: ~0.85
- F1 Score: ~0.80
- Best for: Network-based detection

### HYDRA GAN
- Detection Accuracy: ~0.75
- Pattern Types: 8 categories
- Generation Quality: Medium-High

### Rule-based Scorer
- Explainability: High
- Speed: Very Fast
- Suitable for: Real-time scoring

## Integration with Backend Services

Models integrate with existing services:

```python
# In services/explainability_engine.py
from models import MuleDetectionRandomForest, SHAPExplainer

# In services/risk_scoring_engine.py
from models import RulBasedRiskScoringModel

# In services/network_engine.py
from models import GraphAnalyticsEngine

# In api/hydra_api.py
from models import HYDRA_GAN
```

## Future Enhancements

1. **Ensemble Models**: Combine RF + GNN predictions
2. **Online Learning**: Incremental model updates
3. **Transfer Learning**: Pre-trained embeddings
4. **Attention Mechanisms**: For GNN improvements
5. **Anomaly Detection**: Isolation Forest, Autoencoders
6. **Time Series**: LSTM for temporal patterns

## Support

For questions or issues:
- Check test scripts for usage examples
- Review docstrings in each model file
- Consult model_manager.py for unified interface
