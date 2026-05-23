from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from bson import ObjectId
import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Mendaftarkan pengguna baru ke database MongoDB.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    # Validasi input
    if not username or not email or not password:
        return jsonify({"error": "Username, email, dan password wajib diisi"}), 400
        
    if len(password) < 6:
        return jsonify({"error": "Password harus minimal 6 karakter"}), 400
        
    # Periksa apakah username atau email sudah terdaftar
    existing_user = db.users.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        return jsonify({"error": "Username atau Email sudah terdaftar"}), 400
        
    # Hash password dengan aman
    hashed_password = generate_password_hash(password)
    
    # Buat dokumen user baru
    new_user = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.datetime.utcnow()
    }
    
    # Simpan ke MongoDB
    result = db.users.insert_one(new_user)
    
    return jsonify({
        "message": "User berhasil terdaftar!",
        "user_id": str(result.inserted_id)
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user dan mengembalikan Access Token serta Refresh Token JWT.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500

    data = request.get_json() or {}
    identifier = data.get("identifier")  # Bisa berupa username ATAU email
    password = data.get("password")
    
    if not identifier or not password:
        return jsonify({"error": "Username/email dan password wajib diisi"}), 400
        
    # Cari user berdasarkan username atau email
    user = db.users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
    
    # Verifikasi keberadaan user dan kecocokan password
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Username/email atau password salah"}), 401
        
    # Buat JWT tokens
    # Identity token diisi dengan string ID unik user dari MongoDB
    user_id_str = str(user["_id"])
    access_token = create_access_token(identity=user_id_str)
    refresh_token = create_refresh_token(identity=user_id_str)
    
    return jsonify({
        "message": "Login berhasil!",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user_id_str,
            "username": user["username"],
            "email": user["email"]
        }
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Mengambil data profil pengguna yang sedang login berdasarkan JWT token.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    # Ambil user ID dari payload token JWT
    current_user_id = get_jwt_identity()
    
    try:
        user = db.users.find_one({"_id": ObjectId(current_user_id)})
        if not user:
            return jsonify({"error": "User tidak ditemukan"}), 404
            
        return jsonify({
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "created_at": user.get("created_at")
        }), 200
    except Exception as e:
        return jsonify({"error": f"Invalid User ID format: {e}"}), 400
