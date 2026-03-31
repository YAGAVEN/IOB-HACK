"""
CSV Import API - Import transaction data from CSV files
"""
from flask import Blueprint, request, jsonify
import sqlite3
import csv
import io
from datetime import datetime
import os

import_bp = Blueprint('import_api', __name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/transactions.db')

def validate_transaction_row(row, line_number):
    """Validate a single transaction row from CSV"""
    errors = []
    
    # Required fields
    required_fields = ['from_account', 'to_account', 'amount', 'timestamp']
    for field in required_fields:
        if field not in row or not row[field] or str(row[field]).strip() == '':
            errors.append(f"Line {line_number}: Missing required field '{field}'")
    
    # Validate amount
    try:
        amount = float(row.get('amount', 0))
        if amount <= 0:
            errors.append(f"Line {line_number}: Amount must be positive")
    except ValueError:
        errors.append(f"Line {line_number}: Invalid amount format")
    
    # Validate timestamp format
    timestamp = row.get('timestamp', '')
    try:
        # Accept multiple date formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
            try:
                datetime.strptime(timestamp, fmt)
                break
            except:
                continue
        else:
            errors.append(f"Line {line_number}: Invalid timestamp format (use YYYY-MM-DD HH:MM:SS)")
    except Exception as e:
        errors.append(f"Line {line_number}: Timestamp error - {str(e)}")
    
    # Validate suspicious_score if provided
    if 'suspicious_score' in row and row['suspicious_score']:
        try:
            score = float(row['suspicious_score'])
            if not (0 <= score <= 1):
                errors.append(f"Line {line_number}: Suspicious score must be between 0 and 1")
        except ValueError:
            errors.append(f"Line {line_number}: Invalid suspicious_score format")
    
    return errors

def generate_transaction_id(conn):
    """Generate next transaction ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(SUBSTR(transaction_id, 4) AS INTEGER)) FROM transactions")
    result = cursor.fetchone()[0]
    next_id = (result or 0) + 1
    return f"TXN{next_id:06d}"

@import_bp.route('/import/csv', methods=['POST'])
def import_csv():
    """
    Import transactions from CSV file
    
    Expected CSV format:
    from_account,to_account,amount,timestamp,transaction_type,suspicious_score,pattern_type,scenario
    
    Required fields: from_account, to_account, amount, timestamp
    Optional fields: transaction_type, suspicious_score, pattern_type, scenario
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        # Check if file is CSV
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'message': 'File must be a CSV file'
            }), 400
        
        # Read CSV content
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # Validate all rows first
        rows_data = []
        validation_errors = []
        line_number = 1  # Header is line 0
        
        for row in csv_reader:
            line_number += 1
            errors = validate_transaction_row(row, line_number)
            if errors:
                validation_errors.extend(errors)
            else:
                rows_data.append(row)
        
        # If there are validation errors, return them
        if validation_errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_errors[:10],  # Limit to first 10 errors
                'total_errors': len(validation_errors)
            }), 400
        
        # Connect to database and insert
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        inserted_count = 0
        skipped_count = 0
        
        for row in rows_data:
            try:
                # Generate transaction ID
                transaction_id = generate_transaction_id(conn)
                
                # Prepare data with defaults
                from_account = row['from_account'].strip()
                to_account = row['to_account'].strip()
                amount = float(row['amount'])
                timestamp = row['timestamp'].strip()
                transaction_type = row.get('transaction_type', 'TRANSFER').strip() or 'TRANSFER'
                suspicious_score = float(row.get('suspicious_score', 0)) if row.get('suspicious_score') else 0.0
                pattern_type = row.get('pattern_type', 'normal').strip() or 'normal'
                scenario = row.get('scenario', '').strip()
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO transactions 
                    (transaction_id, from_account, to_account, amount, timestamp, 
                     transaction_type, suspicious_score, pattern_type, scenario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (transaction_id, from_account, to_account, amount, timestamp,
                      transaction_type, suspicious_score, pattern_type, scenario))
                
                inserted_count += 1
                
            except Exception as e:
                skipped_count += 1
                print(f"[ERROR] Failed to insert row: {str(e)}")
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {inserted_count} transactions',
            'inserted': inserted_count,
            'skipped': skipped_count,
            'total_processed': len(rows_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Import failed: {str(e)}'
        }), 500

@import_bp.route('/import/template', methods=['GET'])
def download_template():
    """Download CSV template for importing transactions"""
    try:
        template = """from_account,to_account,amount,timestamp,transaction_type,suspicious_score,pattern_type,scenario
ACC001,ACC002,5000.00,2026-03-31 10:00:00,TRANSFER,0.1,normal,Regular payment
ACC003,ACC004,15000.50,2026-03-31 11:30:00,TRANSFER,0.8,structuring,Large transfer split
ACC005,ACC006,2500.00,2026-03-31 12:00:00,DEPOSIT,0.0,normal,Salary deposit"""
        
        return template, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=transaction_import_template.csv'
        }
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate template: {str(e)}'
        }), 500

@import_bp.route('/import/stats', methods=['GET'])
def get_import_stats():
    """Get statistics about imported data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total = cursor.fetchone()[0]
        
        # By pattern type
        cursor.execute("""
            SELECT pattern_type, COUNT(*) as count 
            FROM transactions 
            GROUP BY pattern_type 
            ORDER BY count DESC
        """)
        by_pattern = [{'pattern': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Recent imports (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM transactions 
            WHERE timestamp > datetime('now', '-1 day')
        """)
        recent = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_transactions': total,
                'by_pattern': by_pattern,
                'recent_24h': recent
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get stats: {str(e)}'
        }), 500
