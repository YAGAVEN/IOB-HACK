from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from config import Config
from api.chronos_api import chronos_bp
from api.hydra_api import hydra_bp  
from api.autosar_api import autosar_bp
from api.mule_api import mule_bp
from api.import_api import import_bp
from data.synthetic_generator import init_database

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(chronos_bp, url_prefix='/api/chronos')
    app.register_blueprint(hydra_bp, url_prefix='/api/hydra')
    app.register_blueprint(autosar_bp, url_prefix='/api/autosar')
    app.register_blueprint(mule_bp, url_prefix='/api/mule')
    app.register_blueprint(import_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'TriNetra API'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Initialize database on first run
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    print("🔹 TriNetra Backend Starting...")
    print(f"🔹 Server running at: http://localhost:{Config.PORT}")
    print("🔹 API endpoints:")
    print(f"🔹   - Health: http://localhost:{Config.PORT}/api/health")
    print(f"🔹   - Timeline: http://localhost:{Config.PORT}/api/chronos/timeline")
    print("🔹 Press Ctrl+C to stop")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )