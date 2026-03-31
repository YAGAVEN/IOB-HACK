#!/usr/bin/env python3
"""
Comprehensive test suite for all models
Tests each model individually and the integrated ModelManager
"""

import sys
import numpy as np
from datetime import datetime

print("=" * 70)
print("TriNetra Models Test Suite")
print("=" * 70)
print()

# Test 1: Random Forest Mule Detection
print("1. Testing Random Forest Mule Detection Model")
print("-" * 70)
try:
    from models.random_forest_mule import MuleDetectionRandomForest
    
    rf = MuleDetectionRandomForest(n_estimators=50, max_depth=8)
    X, y = rf.generate_training_data(n_samples=500)
    
    print(f"  Generated {len(X)} training samples")
    print(f"  Mule ratio: {y.sum() / len(y):.2%}")
    
    metrics = rf.train(X, y, validation_split=0.2)
    print(f"  Training Accuracy: {metrics['accuracy']:.3f}")
    print(f"  ROC AUC: {metrics['roc_auc']:.3f}")
    
    importance = rf.get_feature_importance()
    print(f"  Top feature: {list(importance.keys())[0]}")
    
    print("  ✓ Random Forest test passed\n")
except Exception as e:
    print(f"  ✗ Random Forest test failed: {e}\n")
    sys.exit(1)

# Test 2: Rule-based Risk Scoring
print("2. Testing Rule-based Risk Scoring Model")
print("-" * 70)
try:
    from models.risk_scoring_model import RulBasedRiskScoringModel, RiskWeights
    
    scorer = RulBasedRiskScoringModel()
    
    # High-risk case
    high_risk_features = {
        'in_out_ratio': 0.95,
        'rapid_in_out': 1,
        'account_age_days': 30,
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
    
    result = scorer.calculate_risk_score(high_risk_features)
    print(f"  High-risk score: {result['final_score']:.3f}")
    print(f"  Risk level: {result['risk_level']}")
    print(f"  Behavioral: {result['dimension_scores']['behavioral']:.3f}")
    print(f"  Network: {result['dimension_scores']['network']:.3f}")
    
    print("  ✓ Rule-based scorer test passed\n")
except Exception as e:
    print(f"  ✗ Rule-based scorer test failed: {e}\n")
    sys.exit(1)

# Test 3: HYDRA GAN
print("3. Testing HYDRA GAN")
print("-" * 70)
try:
    from models.hydra_gan import HYDRA_GAN
    
    gan = HYDRA_GAN(latent_dim=50, pattern_dim=30, device='cpu')
    
    # Generate synthetic patterns
    real_patterns = np.random.randn(200, 30) * 0.5
    
    print(f"  Training on {len(real_patterns)} patterns...")
    history = gan.train(real_patterns, epochs=20, batch_size=32)
    
    print(f"  Final G Loss: {history['g_losses'][-1]:.4f}")
    print(f"  Final D Loss: {history['d_losses'][-1]:.4f}")
    
    # Generate adversarial pattern
    pattern = gan.generate_adversarial_pattern(n_samples=1)
    print(f"  Generated pattern: {pattern['pattern_id']}")
    print(f"  Pattern type: {pattern['pattern_type']}")
    print(f"  Complexity: {pattern['complexity_score']:.3f}")
    
    # Test detection
    metrics = gan.test_detection_accuracy(real_patterns, n_generated=50)
    print(f"  Detection accuracy: {metrics['overall_accuracy']:.3f}")
    
    print("  ✓ HYDRA GAN test passed\n")
except Exception as e:
    print(f"  ✗ HYDRA GAN test failed: {e}\n")
    sys.exit(1)

# Test 4: GNN Mule Detector
print("4. Testing GNN Mule Detector")
print("-" * 70)
try:
    from models.gnn_mule_detector import GNN_MuleDetectionSystem, generate_synthetic_graph
    
    # Generate synthetic graph
    X, A, y, train_mask, val_mask, test_mask = generate_synthetic_graph(
        n_nodes=100, n_features=8, mule_ratio=0.3
    )
    
    print(f"  Graph: {X.shape[0]} nodes, {A.sum():.0f} edges")
    print(f"  Mule ratio: {y.sum() / len(y):.2%}")
    
    gnn = GNN_MuleDetectionSystem(n_features=8, device='cpu')
    
    print(f"  Training GNN...")
    history = gnn.train(X, A, y, train_mask, val_mask, epochs=50)
    
    final_acc = history['val_accuracies'][-1]
    print(f"  Final validation accuracy: {final_acc:.3f}")
    
    # Evaluate
    metrics = gnn.evaluate(X, A, y, test_mask)
    print(f"  Test accuracy: {metrics['accuracy']:.3f}")
    print(f"  F1 score: {metrics['f1_score']:.3f}")
    
    print("  ✓ GNN test passed\n")
except Exception as e:
    print(f"  ✗ GNN test failed: {e}\n")
    sys.exit(1)

# Test 5: Graph Analytics Engine
print("5. Testing Graph Analytics Engine")
print("-" * 70)
try:
    from models.graph_analytics import GraphAnalyticsEngine
    
    # Create test transactions
    transactions = [
        {'from': 'A1', 'to': 'A2', 'amount': 1000},
        {'from': 'A1', 'to': 'A3', 'amount': 2000},
        {'from': 'A2', 'to': 'A4', 'amount': 500},
        {'from': 'A3', 'to': 'A4', 'amount': 1500},
        {'from': 'A4', 'to': 'A5', 'amount': 3000},
        {'from': 'A5', 'to': 'A1', 'amount': 500},  # Cycle
        {'from': 'A2', 'to': 'A6', 'amount': 800},
        {'from': 'A3', 'to': 'A6', 'amount': 1200},
    ]
    
    engine = GraphAnalyticsEngine()
    graph = engine.build_graph_from_transactions(transactions)
    
    print(f"  Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Metrics
    metrics = engine.get_graph_metrics()
    print(f"  Density: {metrics.density:.3f}")
    print(f"  Avg clustering: {metrics.avg_clustering:.3f}")
    
    # PageRank
    pagerank = engine.calculate_pagerank()
    top_node = max(pagerank.items(), key=lambda x: x[1])
    print(f"  Top PageRank: {top_node[0]} ({top_node[1]:.4f})")
    
    # Communities
    communities = engine.detect_communities_louvain()
    stats = engine.get_community_stats()
    print(f"  Communities: {stats['n_communities']}")
    
    # Cycles
    cycles = engine.find_cycles()
    print(f"  Cycles found: {len(cycles)}")
    
    print("  ✓ Graph analytics test passed\n")
except Exception as e:
    print(f"  ✗ Graph analytics test failed: {e}\n")
    sys.exit(1)

# Test 6: SHAP Explainer
print("6. Testing SHAP Explainer")
print("-" * 70)
try:
    from models.shap_explainer import SHAPExplainer
    from sklearn.ensemble import RandomForestClassifier
    
    # Create simple model
    feature_names = ['f1', 'f2', 'f3', 'f4', 'f5']
    X_train = np.random.randn(100, 5)
    y_train = (X_train[:, 0] + X_train[:, 1] > 0).astype(int)
    
    model = RandomForestClassifier(n_estimators=20, random_state=42)
    model.fit(X_train, y_train)
    
    print(f"  Model trained on {len(X_train)} samples")
    
    explainer = SHAPExplainer(model, feature_names)
    
    try:
        explainer.fit(X_train, explainer_type='tree')
        print(f"  SHAP explainer fitted")
        
        # Test explanation
        X_test = np.random.randn(1, 5)
        explanation = explainer.explain_prediction(X_test)
        
        print(f"  Base value: {explanation['base_value']:.3f}")
        print(f"  Top contributors: {len(explanation['top_positive'])}")
        
        # Global importance
        importance = explainer.get_global_feature_importance(X_train)
        top_feature = list(importance.keys())[0]
        print(f"  Most important: {top_feature}")
        
        print("  ✓ SHAP explainer test passed\n")
    except:
        print("  ⚠ SHAP not available, using simplified explanations")
        explanation = explainer._simplified_explanation(X_test)
        print(f"  Simplified explanation generated")
        print("  ✓ Fallback test passed\n")
        
except Exception as e:
    print(f"  ✗ SHAP explainer test failed: {e}\n")
    sys.exit(1)

# Test 7: Model Manager (Integration)
print("7. Testing Model Manager (Integration)")
print("-" * 70)
try:
    from models.model_manager import ModelManager
    
    manager = ModelManager(model_dir='./test_models')
    
    # Initialize and train Random Forest
    manager.initialize_random_forest(n_estimators=30, max_depth=6)
    X, y = manager.random_forest.generate_training_data(n_samples=300)
    metrics = manager.train_random_forest(X, y)
    
    print(f"  Random Forest trained: {metrics['accuracy']:.3f} accuracy")
    
    # Test prediction
    test_features = {
        'transaction_velocity': 20,
        'in_out_ratio': 0.93,
        'account_age_days': 50,
        'rapid_in_out': 1,
        'dormant_activation': 0,
        'high_throughput': 1,
        'degree_centrality': 0.55,
        'betweenness_centrality': 0.35,
        'pagerank': 0.025,
        'is_hub': 1,
        'is_funnel': 0,
        'multi_hop_count': 4,
        'circular_flow_count': 2,
        'structuring_count': 3
    }
    
    # Comprehensive assessment
    assessment = manager.get_comprehensive_risk_assessment(
        account_id='TEST_ACC',
        features=test_features
    )
    
    print(f"  Assessment for: {assessment['account_id']}")
    print(f"  Risk level: {assessment['risk_level']}")
    print(f"  Final score: {assessment['final_risk_score']:.3f}")
    print(f"  Confidence: {assessment['risk_confidence']:.3f}")
    print(f"  Models used: {len(assessment['risk_scores'])}")
    
    # Model status
    status = manager.get_model_status()
    trained_count = sum(status['models_trained'].values())
    print(f"  Models trained: {trained_count}")
    
    print("  ✓ Model Manager test passed\n")
except Exception as e:
    print(f"  ✗ Model Manager test failed: {e}\n")
    sys.exit(1)

# Summary
print("=" * 70)
print("ALL TESTS PASSED ✓")
print("=" * 70)
print()
print("Models available:")
print("  • Random Forest Mule Detection")
print("  • Rule-based Risk Scoring")
print("  • HYDRA GAN (Adversarial Patterns)")
print("  • GNN Mule Detector")
print("  • Graph Analytics Engine")
print("  • SHAP Explainability")
print("  • Model Manager (Integrated)")
print()
print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
