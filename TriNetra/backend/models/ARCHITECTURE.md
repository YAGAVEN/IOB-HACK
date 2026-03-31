# Models Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MODEL MANAGER                           │
│                  (Unified Coordination Layer)                   │
│                     model_manager.py                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────────────┐
             │                                                     │
             ▼                                                     ▼
┌────────────────────────┐                        ┌────────────────────────┐
│     ML MODELS          │                        │     DL MODELS          │
├────────────────────────┤                        ├────────────────────────┤
│                        │                        │                        │
│ ┌──────────────────┐   │                        │ ┌──────────────────┐   │
│ │ Random Forest    │   │                        │ │   HYDRA GAN      │   │
│ │  + SHAP          │   │                        │ │  Generator       │   │
│ └──────────────────┘   │                        │ │  Discriminator   │   │
│                        │                        │ └──────────────────┘   │
│ ┌──────────────────┐   │                        │                        │
│ │ Rule-based       │   │                        │ ┌──────────────────┐   │
│ │ Risk Scorer      │   │                        │ │   GNN/GCN        │   │
│ │ 4 Dimensions     │   │                        │ │  Node Classifier │   │
│ └──────────────────┘   │                        │ └──────────────────┘   │
│                        │                        │                        │
└────────────────────────┘                        └────────────────────────┘
             │                                                     │
             └─────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
             ┌─────────────────────────────────────────────────────┐
             │           SUPPORTING ANALYTICS                      │
             ├─────────────────────────────────────────────────────┤
             │                                                     │
             │  ┌──────────────────────────────────────────────┐  │
             │  │ Graph Analytics Engine                       │  │
             │  │ • Centrality Metrics (5 types)              │  │
             │  │ • Community Detection (Louvain)             │  │
             │  │ • Pattern Detection (cycles, hubs, funnels) │  │
             │  └──────────────────────────────────────────────┘  │
             │                                                     │
             │  ┌──────────────────────────────────────────────┐  │
             │  │ SHAP Explainability Engine                  │  │
             │  │ • Feature Contributions                     │  │
             │  │ • Global Importance                         │  │
             │  │ • Human-readable Explanations               │  │
             │  └──────────────────────────────────────────────┘  │
             │                                                     │
             └─────────────────────────────────────────────────────┘
```

## Data Flow

```
Transaction Data
       │
       ▼
┌─────────────┐
│ Feature     │
│ Extraction  │
└──────┬──────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
       ▼                                      ▼
┌──────────────┐                    ┌──────────────┐
│ Random       │                    │ Rule-based   │
│ Forest       │                    │ Risk Scorer  │
│ Prediction   │                    │ Calculation  │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       ├───────────────┬───────────────────┤
       │               │                   │
       ▼               ▼                   ▼
┌─────────────┐  ┌──────────┐  ┌──────────────┐
│ SHAP        │  │ Ensemble │  │ Dimension    │
│ Explanation │  │ Score    │  │ Breakdown    │
└─────────────┘  └──────────┘  └──────────────┘
       │               │                   │
       └───────────────┴───────────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │ Comprehensive    │
            │ Risk Assessment  │
            │ • Score          │
            │ • Level          │
            │ • Explanation    │
            │ • Recommendations│
            └──────────────────┘
```

## Model Integration

### 1. Training Pipeline

```
Data Collection
     ↓
Feature Engineering
     ↓
Train/Val/Test Split
     ↓
Model Training ────────┐
     ↓                 │
Validation            │
     ↓                 │
Hyperparameter Tuning │
     ↓                 │
Final Training ←──────┘
     ↓
Model Persistence
     ↓
Production Deployment
```

### 2. Inference Pipeline

```
New Transaction/Account
          ↓
    Feature Extraction
          ↓
    ┌─────┴─────┐
    │           │
    ▼           ▼
RF Model    Rule-based
Prediction   Scoring
    │           │
    └─────┬─────┘
          ↓
    Ensemble Score
          ↓
    Risk Classification
          ↓
    SHAP Explanation
          ↓
    Final Assessment
```

### 3. Graph Analysis Pipeline

```
Transaction Network
         ↓
   Build Graph
         ↓
   ┌────┴────┐
   │         │
   ▼         ▼
Centrality  Community
Metrics    Detection
   │         │
   └────┬────┘
        ↓
  Pattern Detection
  • Cycles
  • Hubs
  • Funnels
        ↓
  Risk Features
        ↓
  ML Models Input
```

## Component Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                    ModelManager                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ initialize_random_forest()                             │ │
│  │ initialize_hydra_gan()                                 │ │
│  │ initialize_gnn()                                       │ │
│  │                                                        │ │
│  │ train_random_forest()                                  │ │
│  │ train_hydra_gan()                                      │ │
│  │ train_gnn()                                            │ │
│  │                                                        │ │
│  │ predict_mule_risk_rf()                                 │ │
│  │ predict_mule_risk_gnn()                                │ │
│  │ calculate_rule_based_risk()                            │ │
│  │                                                        │ │
│  │ analyze_graph()                                        │ │
│  │ generate_adversarial_pattern()                         │ │
│  │                                                        │ │
│  │ get_comprehensive_risk_assessment() ◄─── Main API     │ │
│  │                                                        │ │
│  │ save_all_models()                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Feature Flow

```
Account Data
     ↓
┌─────────────────────────────────────┐
│ Feature Engineering                 │
├─────────────────────────────────────┤
│                                     │
│ Behavioral Features (7)             │
│  • transaction_velocity             │
│  • in_out_ratio                     │
│  • account_age_days                 │
│  • rapid_in_out                     │
│  • dormant_activation               │
│  • high_throughput                  │
│  • structuring_count                │
│                                     │
│ Network Features (5)                │
│  • degree_centrality                │
│  • betweenness_centrality           │
│  • pagerank                         │
│  • is_hub                           │
│  • is_funnel                        │
│                                     │
│ Layering Features (2)               │
│  • multi_hop_count                  │
│  • circular_flow_count              │
│                                     │
└────────────┬────────────────────────┘
             │
             ├─────────────┬──────────────┐
             ▼             ▼              ▼
    Random Forest    Rule-based      GNN (with
       (14 dim)      (14 dim)        adjacency)
             │             │              │
             └─────────────┴──────────────┘
                           │
                           ▼
                    Risk Assessment
```

## Model Dependencies

```
ModelManager
    │
    ├── MuleDetectionRandomForest
    │   └── sklearn.RandomForestClassifier
    │
    ├── RulBasedRiskScoringModel
    │   └── (pure Python logic)
    │
    ├── HYDRA_GAN
    │   ├── torch.nn.Module
    │   ├── Generator
    │   └── Discriminator
    │
    ├── GNN_MuleDetectionSystem
    │   ├── torch.nn.Module
    │   ├── GCN_MuleDetector
    │   └── GCNLayer
    │
    ├── GraphAnalyticsEngine
    │   ├── networkx
    │   └── python-louvain
    │
    └── SHAPExplainer
        └── shap (optional)
```

## Model Interfaces

### Input Interface
```python
features = {
    # 14 standardized features
    'transaction_velocity': float,
    'in_out_ratio': float,
    # ... etc
}
```

### Output Interface
```python
assessment = {
    'account_id': str,
    'risk_level': str,  # CRITICAL/HIGH/MEDIUM/LOW
    'final_risk_score': float,  # 0-1
    'risk_confidence': float,  # 0-1
    'risk_scores': {
        'random_forest': float,
        'rule_based': float
    },
    'explanations': {
        'random_forest': {...},
        'rule_based': {...}
    },
    'recommendations': [str, ...]
}
```

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Production Environment          │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Flask API                       │ │
│  │   (Backend Service)               │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│              ▼                          │
│  ┌───────────────────────────────────┐ │
│  │   ModelManager                    │ │
│  │   (In-memory models)              │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│              ├──────────┬──────────┐    │
│              ▼          ▼          ▼    │
│         ┌────────┐ ┌────────┐ ┌────┐   │
│         │   RF   │ │  Rule  │ │GNN │   │
│         │ Model  │ │  Model │ │    │   │
│         └────────┘ └────────┘ └────┘   │
│              │          │          │    │
│              └──────────┴──────────┘    │
│                        │                │
│                        ▼                │
│              ┌──────────────────┐       │
│              │  Saved Models    │       │
│              │  Directory       │       │
│              └──────────────────┘       │
│                                         │
└─────────────────────────────────────────┘
```

## Performance Characteristics

| Component | Latency | Throughput | Scalability |
|-----------|---------|------------|-------------|
| Random Forest | <10ms | High | Linear |
| Rule-based | <1ms | Very High | Linear |
| HYDRA GAN | ~50ms | Medium | GPU-dependent |
| GNN | ~100ms | Medium | GPU-dependent |
| Graph Analytics | Variable | Medium | Graph-size dependent |
| SHAP | ~50ms | Medium | Linear |

## Summary

The models architecture provides:
- **Modularity**: Each model is independent
- **Coordination**: ModelManager provides unified interface
- **Scalability**: Models can be deployed independently
- **Explainability**: SHAP integration throughout
- **Flexibility**: Easy to add new models
- **Performance**: Optimized for real-time inference
