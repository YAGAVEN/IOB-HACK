import json
from datetime import datetime
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import Config
from services.risk_scoring_engine import RiskScoringEngine
from services.explainability_engine import ExplainabilityEngine
from services.network_engine import NetworkEngine

class MuleAutoSAR:
    """
    Mule-Specific Suspicious Activity Report (SAR) Generator
    Generates comprehensive SARs for money mule accounts
    """
    
    def __init__(self):
        self.risk_engine = RiskScoringEngine()
        self.explain_engine = ExplainabilityEngine()
        self.network_engine = NetworkEngine()
    
    def generate_mule_sar(self, account_id):
        """
        Generate comprehensive SAR for suspected mule account
        
        Args:
            account_id: Account identifier
        
        Returns:
            Dictionary containing complete SAR report
        """
        # Get comprehensive risk analysis
        risk_analysis = self.risk_engine.calculate_mule_risk(account_id)
        
        # Get explanations
        explanations = self.explain_engine.explain_account_risk(account_id)
        
        # Get network snapshot
        network_data = self._get_network_snapshot(account_id)
        
        # Get multi-hop evidence
        layering_details = risk_analysis['details']['layering']
        
        # Map to FATF red flags
        fatf_flags = self._map_fatf_red_flags(risk_analysis, explanations)
        
        # Get account details
        account_info = self._get_account_info(account_id)
        
        # Generate SAR
        sar_report = {
            'sar_id': self._generate_sar_id(),
            'generated_at': datetime.now().isoformat(),
            'account_information': {
                'account_id': account_id,
                'account_details': account_info,
                'risk_score': risk_analysis['risk_score'],
                'risk_level': risk_analysis['risk_level']
            },
            'risk_assessment': {
                'overall_score': risk_analysis['risk_score'],
                'component_scores': risk_analysis['components'],
                'risk_classification': risk_analysis['risk_level']
            },
            'suspicious_indicators': {
                'primary_reasons': explanations['top_reasons'],
                'behavioral_flags': self._extract_behavioral_flags(risk_analysis),
                'network_flags': self._extract_network_flags(risk_analysis),
                'layering_flags': self._extract_layering_flags(layering_details)
            },
            'fatf_red_flags': fatf_flags,
            'network_analysis': network_data,
            'evidence': {
                'multi_hop_paths': layering_details.get('details', {}).get('multi_hop_examples', []),
                'circular_flows': layering_details.get('details', {}).get('circular_examples', []),
                'structuring_patterns': layering_details.get('details', {}).get('structuring_examples', [])
            },
            'recommendations': self._generate_recommendations(risk_analysis),
            'compliance_actions': self._suggest_compliance_actions(risk_analysis['risk_score'])
        }
        
        return sar_report
    
    def _generate_sar_id(self):
        """Generate unique SAR ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f'SAR-MULE-{timestamp}'
    
    def _get_account_info(self, account_id):
        """Get basic account information"""
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            cursor = conn.cursor()
            
            # Try to get from accounts table
            cursor.execute('SELECT * FROM accounts WHERE account_id = ?', (account_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                account_info = dict(zip(columns, result))
            else:
                account_info = {'account_id': account_id, 'status': 'Limited information available'}
            
            # Get transaction summary
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(amount) as total_volume,
                    MIN(timestamp) as first_transaction,
                    MAX(timestamp) as last_transaction
                FROM transactions
                WHERE from_account = ? OR to_account = ?
            ''', (account_id, account_id))
            
            tx_summary = cursor.fetchone()
            if tx_summary:
                account_info.update({
                    'total_transactions': tx_summary[0],
                    'total_volume': tx_summary[1],
                    'first_transaction': tx_summary[2],
                    'last_transaction': tx_summary[3]
                })
            
            conn.close()
            return account_info
            
        except Exception as e:
            print(f"Error getting account info: {e}")
            return {'account_id': account_id, 'error': str(e)}
    
    def _get_network_snapshot(self, account_id):
        """Get network visualization data for account"""
        try:
            # Get ego network (account and immediate neighbors)
            graph = self.network_engine.build_transaction_graph()
            
            if account_id not in graph:
                return {'error': 'Account not in network'}
            
            # Get ego graph (1-hop neighborhood)
            ego_graph = nx.ego_graph(graph, account_id, radius=1)
            
            nodes = []
            for node in ego_graph.nodes():
                nodes.append({
                    'id': node,
                    'is_subject': node == account_id,
                    'degree': ego_graph.degree(node)
                })
            
            links = []
            for source, target, data in ego_graph.edges(data=True):
                links.append({
                    'source': source,
                    'target': target,
                    'weight': data.get('weight', 0),
                    'count': data.get('count', 1)
                })
            
            return {
                'nodes': nodes,
                'links': links,
                'total_nodes': len(nodes),
                'total_edges': len(links)
            }
            
        except Exception as e:
            print(f"Error getting network snapshot: {e}")
            return {'error': str(e)}
    
    def _extract_behavioral_flags(self, risk_analysis):
        """Extract behavioral red flags"""
        behavioral = risk_analysis['details']['behavioral']['features']
        flags = []
        
        if behavioral.get('rapid_in_out'):
            flags.append('Rapid in-out transaction pattern')
        
        if behavioral.get('dormant_activation_flag'):
            flags.append('Dormant account suddenly activated')
        
        if behavioral.get('small_inbound_large_outbound_pattern'):
            flags.append('Multiple small inbound followed by large outbound')
        
        if behavioral.get('high_throughput_flag'):
            flags.append('Unusually high transaction throughput')
        
        if behavioral.get('account_age_days', 999) < 30:
            flags.append('Newly created account with suspicious activity')
        
        return flags
    
    def _extract_network_flags(self, risk_analysis):
        """Extract network-based red flags"""
        network = risk_analysis['details']['network']
        flags = []
        
        if network.get('is_hub'):
            flags.append('Hub-and-spoke distribution pattern detected')
        
        if network.get('is_funnel'):
            flags.append('Funnel account behavior (aggregation point)')
        
        metrics = network.get('metrics', {})
        if metrics.get('betweenness_centrality', 0) > 0.1:
            flags.append('High betweenness centrality (key intermediary in network)')
        
        if network.get('layering_chains', 0) > 0:
            flags.append(f'Involved in {network.get("layering_chains")} layering chains')
        
        return flags
    
    def _extract_layering_flags(self, layering_details):
        """Extract layering-based red flags"""
        flags = []
        
        if layering_details.get('multi_hop_paths', 0) > 0:
            flags.append(f'Involved in {layering_details["multi_hop_paths"]} multi-hop transaction paths')
        
        if layering_details.get('circular_flows', 0) > 0:
            flags.append(f'Involved in {layering_details["circular_flows"]} circular money flows')
        
        if layering_details.get('structuring_patterns', 0) > 0:
            flags.append(f'{layering_details["structuring_patterns"]} structuring patterns detected')
        
        return flags
    
    def _map_fatf_red_flags(self, risk_analysis, explanations):
        """Map detected patterns to FATF red flags"""
        fatf_flags = []
        
        behavioral = risk_analysis['details']['behavioral']['features']
        layering = risk_analysis['details']['layering']
        
        # Structuring
        if layering.get('structuring_patterns', 0) > 0:
            fatf_flags.append({
                'category': 'Structuring',
                'description': 'Multiple transactions structured to avoid reporting thresholds',
                'severity': 'HIGH'
            })
        
        # Rapid pass-through
        if behavioral.get('rapid_in_out'):
            fatf_flags.append({
                'category': 'Rapid Pass-Through',
                'description': 'Funds received and immediately transferred out',
                'severity': 'HIGH'
            })
        
        # Funnel account
        if risk_analysis['details']['network'].get('is_funnel'):
            fatf_flags.append({
                'category': 'Funnel Account',
                'description': 'Account used to aggregate funds from multiple sources',
                'severity': 'MEDIUM'
            })
        
        # Layering
        if layering.get('multi_hop_paths', 0) > 0:
            fatf_flags.append({
                'category': 'Layering',
                'description': 'Complex multi-hop transaction chains to obscure fund origin',
                'severity': 'HIGH'
            })
        
        # Circular transactions
        if layering.get('circular_flows', 0) > 0:
            fatf_flags.append({
                'category': 'Circular Transactions',
                'description': 'Circular money flows detected',
                'severity': 'MEDIUM'
            })
        
        # Dormant account activation
        if behavioral.get('dormant_activation_flag'):
            fatf_flags.append({
                'category': 'Account Anomaly',
                'description': 'Dormant account suddenly reactivated with high activity',
                'severity': 'MEDIUM'
            })
        
        return fatf_flags
    
    def _generate_recommendations(self, risk_analysis):
        """Generate investigation recommendations"""
        recommendations = []
        score = risk_analysis['risk_score']
        
        if score >= 70:
            recommendations.append('IMMEDIATE: Freeze account and initiate investigation')
            recommendations.append('File SAR with financial intelligence unit')
            recommendations.append('Review all connected accounts in network')
        elif score >= 50:
            recommendations.append('Enhanced monitoring for 30 days')
            recommendations.append('Request additional KYC documentation')
            recommendations.append('Manual review of recent transactions')
        else:
            recommendations.append('Continued automated monitoring')
            recommendations.append('Periodic review of activity patterns')
        
        # Specific recommendations based on patterns
        if risk_analysis['details']['network'].get('is_hub'):
            recommendations.append('Investigate all downstream accounts in hub-spoke network')
        
        if risk_analysis['details']['layering'].get('structuring_patterns', 0) > 0:
            recommendations.append('Review all transactions near reporting thresholds')
        
        return recommendations
    
    def _suggest_compliance_actions(self, risk_score):
        """Suggest compliance actions based on risk score"""
        actions = []
        
        if risk_score >= 70:
            actions.extend([
                'File Suspicious Activity Report (SAR)',
                'Alert compliance officer',
                'Consider account restriction',
                'Notify law enforcement if criminal activity suspected'
            ])
        elif risk_score >= 50:
            actions.extend([
                'Enhanced Due Diligence (EDD)',
                'Transaction monitoring increase',
                'Request source of funds documentation'
            ])
        else:
            actions.extend([
                'Standard monitoring',
                'Periodic review'
            ])
        
        return actions
    
    def generate_sar_json(self, account_id):
        """Generate SAR in JSON format"""
        sar = self.generate_mule_sar(account_id)
        return json.dumps(sar, indent=2)
    
    def generate_sar_summary(self, account_id):
        """Generate concise SAR summary"""
        sar = self.generate_mule_sar(account_id)
        
        summary = f"""
SUSPICIOUS ACTIVITY REPORT - MULE ACCOUNT
SAR ID: {sar['sar_id']}
Generated: {sar['generated_at']}

ACCOUNT: {account_id}
RISK SCORE: {sar['risk_assessment']['overall_score']}/100 ({sar['risk_assessment']['risk_classification']})

PRIMARY CONCERNS:
{chr(10).join(f'  • {reason}' for reason in sar['suspicious_indicators']['primary_reasons'])}

FATF RED FLAGS:
{chr(10).join(f'  • [{flag["severity"]}] {flag["category"]}: {flag["description"]}' for flag in sar['fatf_red_flags'])}

RECOMMENDED ACTIONS:
{chr(10).join(f'  • {action}' for action in sar['recommendations'])}
"""
        return summary.strip()

import networkx as nx
