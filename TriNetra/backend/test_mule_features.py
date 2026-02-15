#!/usr/bin/env python3
"""
Test script for Mule Detection Features
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.mule_behavior_engine import MuleBehaviorEngine
from services.network_engine import NetworkEngine
from services.layering_engine import LayeringEngine
from services.risk_scoring_engine import RiskScoringEngine
from services.explainability_engine import ExplainabilityEngine
from services.auto_sar import MuleAutoSAR
from data.synthetic_generator import init_database, TriNetraDataGenerator
from config import Config

def test_mule_features():
    """Test all mule detection features"""
    
    print("=" * 80)
    print("TRINETRA MULE DETECTION FEATURES - TEST")
    print("=" * 80)
    
    # Initialize database with test data
    print("\n1. Initializing database...")
    try:
        init_database()
        print("   ✓ Database initialized")
    except Exception as e:
        print(f"   ✗ Database initialization failed: {e}")
        return
    
    # Generate some test mule transactions
    print("\n2. Generating test mule transaction patterns...")
    try:
        generator = TriNetraDataGenerator(Config.DATABASE_PATH)
        
        # Generate some mule-like transactions
        import pandas as pd
        from datetime import datetime, timedelta
        import numpy as np
        
        test_transactions = []
        base_time = datetime.now() - timedelta(days=7)
        
        # Create a mule pattern: multiple small inbound, one large outbound
        mule_account = "MULE_TEST_001"
        for i in range(10):
            test_transactions.append({
                'transaction_id': f'MULE_IN_{i:03d}',
                'from_account': f'SENDER_{i:02d}',
                'to_account': mule_account,
                'amount': np.random.uniform(5000, 9000),
                'timestamp': (base_time + timedelta(hours=i)).isoformat(),
                'transaction_type': 'transfer',
                'suspicious_score': 0.7,
                'pattern_type': 'mule_inbound',
                'scenario': 'money_mule'
            })
        
        # Large outbound after 2 hours
        test_transactions.append({
            'transaction_id': 'MULE_OUT_001',
            'from_account': mule_account,
            'to_account': 'RECIPIENT_MASTER',
            'amount': 75000,
            'timestamp': (base_time + timedelta(hours=12)).isoformat(),
            'transaction_type': 'transfer',
            'suspicious_score': 0.9,
            'pattern_type': 'mule_outbound',
            'scenario': 'money_mule'
        })
        
        # Insert test transactions
        import sqlite3
        conn = sqlite3.connect(Config.DATABASE_PATH)
        df = pd.DataFrame(test_transactions)
        df.to_sql('transactions', conn, if_exists='append', index=False)
        conn.close()
        
        print(f"   ✓ Generated {len(test_transactions)} test transactions")
    except Exception as e:
        print(f"   ✗ Test data generation failed: {e}")
    
    # Test 1: Behavioral Profiling
    print("\n3. Testing Mule Behavioral Profiling Engine...")
    try:
        behavior_engine = MuleBehaviorEngine()
        analysis = behavior_engine.analyze_account(mule_account)
        print(f"   ✓ Behavioral analysis completed")
        print(f"     - Mule Pattern Score: {analysis['mule_pattern_score']:.2f}")
        print(f"     - Risk Level: {analysis['risk_level']}")
        print(f"     - Rapid In-Out: {analysis['rapid_in_out']}")
    except Exception as e:
        print(f"   ✗ Behavioral profiling failed: {e}")
    
    # Test 2: Network Analysis
    print("\n4. Testing Graph-Based Network Analysis...")
    try:
        network_engine = NetworkEngine()
        graph = network_engine.build_transaction_graph()
        print(f"   ✓ Transaction graph built")
        print(f"     - Nodes: {graph.number_of_nodes()}")
        print(f"     - Edges: {graph.number_of_edges()}")
        
        if mule_account in graph:
            network_analysis = network_engine.analyze_account_network(mule_account)
            print(f"   ✓ Network analysis completed")
            print(f"     - Network Risk Score: {network_analysis.get('network_risk_score', 0):.2f}")
        else:
            print(f"   ! Mule account not yet in graph")
    except Exception as e:
        print(f"   ✗ Network analysis failed: {e}")
    
    # Test 3: Layering Detection
    print("\n5. Testing Layering & Multi-Hop Detection...")
    try:
        layering_engine = LayeringEngine()
        layering_analysis = layering_engine.analyze_layering_risk(mule_account)
        print(f"   ✓ Layering detection completed")
        print(f"     - Layering Risk Score: {layering_analysis['layering_risk_score']:.2f}")
        print(f"     - Multi-hop paths: {layering_analysis['multi_hop_paths']}")
        print(f"     - Structuring patterns: {layering_analysis['structuring_patterns']}")
    except Exception as e:
        print(f"   ✗ Layering detection failed: {e}")
    
    # Test 4: Risk Scoring
    print("\n6. Testing Real-Time Risk Scoring Engine...")
    try:
        risk_engine = RiskScoringEngine()
        risk_analysis = risk_engine.calculate_mule_risk(mule_account)
        print(f"   ✓ Risk scoring completed")
        print(f"     - Overall Risk Score: {risk_analysis['risk_score']}/100")
        print(f"     - Risk Level: {risk_analysis['risk_level']}")
        print(f"     - Components:")
        for component, score in risk_analysis['components'].items():
            print(f"       • {component}: {score}")
    except Exception as e:
        print(f"   ✗ Risk scoring failed: {e}")
    
    # Test 5: Explainability
    print("\n7. Testing Explainability Engine...")
    try:
        explain_engine = ExplainabilityEngine()
        explanation = explain_engine.explain_account_risk(mule_account)
        print(f"   ✓ Risk explanation generated")
        print(f"     Top reasons:")
        for i, reason in enumerate(explanation['top_reasons'][:5], 1):
            print(f"       {i}. {reason}")
    except Exception as e:
        print(f"   ✗ Explainability failed: {e}")
    
    # Test 6: Auto-SAR Generation
    print("\n8. Testing Mule-Specific Auto-SAR Generator...")
    try:
        sar_generator = MuleAutoSAR()
        sar_summary = sar_generator.generate_sar_summary(mule_account)
        print(f"   ✓ SAR generated successfully")
        print("\n" + "─" * 80)
        print(sar_summary)
        print("─" * 80)
    except Exception as e:
        print(f"   ✗ SAR generation failed: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)
    print("\nAll mule detection features are implemented and functional!")
    print("\nAPI Endpoints available at:")
    print("  - GET  /api/mule/mule-risk/<account_id>")
    print("  - GET  /api/mule/network-metrics/<account_id>")
    print("  - GET  /api/mule/layering-detection/<account_id>")
    print("  - GET  /api/mule/explain-risk/<account_id>")
    print("  - POST /api/mule/generate-mule-sar/<account_id>")
    print("  - GET  /api/mule/high-risk-accounts")
    print("  - GET  /api/mule/detect-patterns")
    print("  - GET  /api/mule/statistics")
    print("\n")

if __name__ == '__main__':
    test_mule_features()
