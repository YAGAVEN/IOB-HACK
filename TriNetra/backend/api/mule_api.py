from flask import Blueprint, jsonify, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.mule_behavior_engine import MuleBehaviorEngine
from services.network_engine import NetworkEngine
from services.layering_engine import LayeringEngine
from services.risk_scoring_engine import RiskScoringEngine
from services.explainability_engine import ExplainabilityEngine
from services.auto_sar import MuleAutoSAR

mule_bp = Blueprint('mule', __name__)

# Initialize engines
behavior_engine = MuleBehaviorEngine()
network_engine = NetworkEngine()
layering_engine = LayeringEngine()
risk_engine = RiskScoringEngine()
explain_engine = ExplainabilityEngine()
sar_generator = MuleAutoSAR()

@mule_bp.route('/mule-risk/<account_id>', methods=['GET'])
def get_mule_risk(account_id):
    """Get comprehensive mule risk assessment for an account"""
    try:
        risk_analysis = risk_engine.calculate_mule_risk(account_id)
        return jsonify(risk_analysis), 200
    except Exception as e:
        return jsonify({'error': str(e), 'account_id': account_id}), 500

@mule_bp.route('/network-metrics/<account_id>', methods=['GET'])
def get_network_metrics(account_id):
    """Get network analysis metrics for an account"""
    try:
        network_analysis = network_engine.analyze_account_network(account_id)
        return jsonify(network_analysis), 200
    except Exception as e:
        return jsonify({'error': str(e), 'account_id': account_id}), 500

@mule_bp.route('/layering-detection/<account_id>', methods=['GET'])
def get_layering_detection(account_id):
    """Get layering detection results for an account"""
    try:
        layering_analysis = layering_engine.analyze_layering_risk(account_id)
        return jsonify(layering_analysis), 200
    except Exception as e:
        return jsonify({'error': str(e), 'account_id': account_id}), 500

@mule_bp.route('/explain-risk/<account_id>', methods=['GET'])
def explain_risk(account_id):
    """Get explainable AI analysis for account risk"""
    try:
        explanation = explain_engine.explain_account_risk(account_id)
        return jsonify(explanation), 200
    except Exception as e:
        return jsonify({'error': str(e), 'account_id': account_id}), 500

@mule_bp.route('/generate-mule-sar/<account_id>', methods=['POST'])
def generate_mule_sar(account_id):
    """Generate Suspicious Activity Report for suspected mule account"""
    try:
        output_format = request.args.get('format', 'json')
        
        if output_format == 'summary':
            sar = sar_generator.generate_sar_summary(account_id)
            return sar, 200, {'Content-Type': 'text/plain'}
        else:
            sar = sar_generator.generate_mule_sar(account_id)
            return jsonify(sar), 200
    except Exception as e:
        return jsonify({'error': str(e), 'account_id': account_id}), 500

@mule_bp.route('/behavioral-profile/<account_id>', methods=['GET'])
def get_behavioral_profile(account_id):
    """Get behavioral profiling for an account"""
    try:
        analysis = behavior_engine.analyze_account(account_id)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e), 'account_id': account_id}), 500

@mule_bp.route('/network-visualization', methods=['GET'])
def get_network_visualization():
    """Get network data for D3.js visualization"""
    try:
        viz_data = network_engine.get_network_visualization_data()
        return jsonify(viz_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mule_bp.route('/high-risk-accounts', methods=['GET'])
def get_high_risk_accounts():
    """Get list of high-risk accounts"""
    try:
        threshold = float(request.args.get('threshold', 70))
        limit = int(request.args.get('limit', 50))
        
        high_risk = risk_engine.get_high_risk_accounts(threshold, limit)
        return jsonify({
            'threshold': threshold,
            'count': len(high_risk),
            'accounts': high_risk
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mule_bp.route('/detect-patterns', methods=['GET'])
def detect_patterns():
    """Detect various mule patterns across all accounts"""
    try:
        pattern_type = request.args.get('type', 'all')
        
        results = {}
        
        if pattern_type in ['all', 'hub-spoke']:
            graph = network_engine.build_transaction_graph()
            results['hub_and_spoke'] = network_engine.detect_hub_and_spoke(graph)
        
        if pattern_type in ['all', 'funnel']:
            graph = network_engine.build_transaction_graph()
            results['funnels'] = network_engine.detect_funnel_accounts(graph)
        
        if pattern_type in ['all', 'layering']:
            graph = network_engine.build_transaction_graph()
            results['layering_chains'] = layering_engine.detect_multi_hop_paths(graph)
        
        if pattern_type in ['all', 'circular']:
            graph = network_engine.build_transaction_graph()
            results['circular_flows'] = layering_engine.detect_circular_flows(graph)
        
        if pattern_type in ['all', 'structuring']:
            results['structuring'] = layering_engine.detect_structuring()
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mule_bp.route('/batch-risk-update', methods=['POST'])
def batch_risk_update():
    """Batch update risk scores for multiple accounts"""
    try:
        data = request.get_json() or {}
        account_ids = data.get('account_ids', None)
        
        updated = risk_engine.batch_update_risk_scores(account_ids)
        
        return jsonify({
            'status': 'completed',
            'accounts_updated': updated
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mule_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get overall mule detection statistics"""
    try:
        # Get high risk account counts
        critical = len(risk_engine.get_high_risk_accounts(threshold=70, limit=1000))
        high = len(risk_engine.get_high_risk_accounts(threshold=50, limit=1000))
        
        # Get pattern counts
        graph = network_engine.build_transaction_graph()
        hubs = len(network_engine.detect_hub_and_spoke(graph))
        funnels = len(network_engine.detect_funnel_accounts(graph))
        circular = len(layering_engine.detect_circular_flows(graph))
        structuring = len(layering_engine.detect_structuring())
        
        stats = {
            'risk_levels': {
                'critical': critical,
                'high': high - critical,
                'total_high_risk': high
            },
            'patterns_detected': {
                'hub_and_spoke': hubs,
                'funnels': funnels,
                'circular_flows': circular,
                'structuring': structuring
            },
            'network_stats': {
                'total_nodes': graph.number_of_nodes(),
                'total_edges': graph.number_of_edges()
            },
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
