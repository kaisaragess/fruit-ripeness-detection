import os
from datetime import timedelta

class Config:
    # Flask Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "default-flask-secret-key-change-this")
    
    # MongoDB Settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/fruit_db")
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-jwt-secret-key-change-this")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Token berlaku 24 jam untuk memudahkan testing mahasiswa
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Roboflow Settings
    ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
    ROBOFLOW_API_URL = os.getenv("ROBOFLOW_API_URL", "https://serverless.roboflow.com")
    ROBOFLOW_WORKSPACE = os.getenv("ROBOFLOW_WORKSPACE", "15240772s-workspace-v3t3g")
    ROBOFLOW_WORKFLOW_ID = os.getenv("ROBOFLOW_WORKFLOW_ID", "detect-count-and-visualize-3")
    
    # Upload Settings
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.abspath(os.path.dirname(__file__)), "app", "static", "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maksimal ukuran upload gambar 16MB
