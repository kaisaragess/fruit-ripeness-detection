from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import os

# Globals untuk MongoDB
mongo_client = None
db = None

def create_app():
    global mongo_client, db
    
    app = Flask(__name__)
    
    # Load Configuration
    app.config.from_object("config.Config")
    
    # Enable CORS (Cross-Origin Resource Sharing)
    # Ini sangat penting agar aplikasi Next.js / Electron bisa mengakses API ini
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Setup JWT Manager
    jwt = JWTManager(app)
    
    # Setup MongoDB Atlas Connection
    mongo_uri = app.config.get("MONGO_URI")
    try:
        mongo_client = MongoClient(mongo_uri)
        # Mengambil database 'fruit_db' (nama database default)
        # Catatan: PyMongo bersifat lazy, koneksi sesungguhnya baru terjadi saat query pertama dijalankan
        db = mongo_client.get_default_database(default="fruit_db")
        print(f"MongoDB Client initialized with database: {db.name}")
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")
        db = None
    
    # Pastikan folder upload lokal static/uploads/ tersedia
    upload_folder = app.config.get("UPLOAD_FOLDER")
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
        print(f"Upload directory ready at: {upload_folder}")
    
    # Custom JWT Error Handlers
    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired", "sub_status": "token_expired"}), 401

    @jwt.invalid_token_loader
    def my_invalid_token_callback(error_string):
        return jsonify({"error": "Invalid token provided", "reason": error_string}), 401

    @jwt.unauthorized_loader
    def my_unauthorized_callback(error_string):
        return jsonify({"error": "Authorization header missing", "reason": error_string}), 401

    # Register Blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.detection_controller import detect_bp
    from app.controllers.history_controller import history_bp
    from app.controllers.analytics_controller import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(detect_bp, url_prefix="/api/detect")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    
    # Route default untuk memastikan API berjalan
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "status": "running",
            "message": "Rotten/Fresh Fruit Detection Flask API is fully operational!",
            "database_connected": db is not None
        })
        
    return app
