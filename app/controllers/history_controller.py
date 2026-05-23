from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from bson import ObjectId
import os

history_bp = Blueprint("history", __name__)

@history_bp.route("/", methods=["GET"])
@jwt_required()
def get_history():
    """
    Mengambil riwayat deteksi pengguna yang sedang login (dengan paginasi opsional).
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    current_user_id = get_jwt_identity()
    
    # Ambil parameter paginasi dari query string (default: page=1, limit=20)
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        if page < 1: page = 1
        if limit < 1: limit = 20
    except ValueError:
        page = 1
        limit = 20
        
    skip = (page - 1) * limit
    
    try:
        # Query logs milik user tersebut, diurutkan dari yang terbaru (timestamp DESC)
        query = {"user_id": ObjectId(current_user_id)}
        
        total_records = db.detections.count_documents(query)
        cursor = db.detections.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        
        history_list = []
        for doc in cursor:
            history_list.append({
                "id": str(doc["_id"]),
                "image_url": f"{request.host_url.rstrip('/')}{doc.get('image_url')}",
                "count_objects": doc.get("count_objects", 0),
                "fresh_count": doc.get("fresh_count", 0),
                "rotten_count": doc.get("rotten_count", 0),
                "breakdown": doc.get("breakdown", {}),
                "timestamp": doc.get("timestamp")
            })
            
        return jsonify({
            "history": history_list,
            "pagination": {
                "total_records": total_records,
                "current_page": page,
                "limit": limit,
                "total_pages": (total_records + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Gagal mengambil riwayat: {str(e)}"}), 500


@history_bp.route("/<string:detection_id>", methods=["GET"])
@jwt_required()
def get_detection_detail(detection_id):
    """
    Mengambil detail lengkap dari satu riwayat deteksi buah tertentu milik pengguna.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    current_user_id = get_jwt_identity()
    
    try:
        doc = db.detections.find_one({
            "_id": ObjectId(detection_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not doc:
            return jsonify({"error": "Riwayat deteksi tidak ditemukan atau Anda tidak memiliki akses"}), 404
            
        # Bentuk respon lengkap
        detail = {
            "id": str(doc["_id"]),
            "image_url": f"{request.host_url.rstrip('/')}{doc.get('image_url')}",
            "filename": doc.get("filename"),
            "count_objects": doc.get("count_objects", 0),
            "fresh_count": doc.get("fresh_count", 0),
            "rotten_count": doc.get("rotten_count", 0),
            "breakdown": doc.get("breakdown", {}),
            "predictions": doc.get("predictions", []),
            "timestamp": doc.get("timestamp")
        }
        
        return jsonify(detail), 200
        
    except Exception as e:
        return jsonify({"error": f"Invalid detection ID format atau error: {str(e)}"}), 400


@history_bp.route("/<string:detection_id>", methods=["DELETE"])
@jwt_required()
def delete_detection(detection_id):
    """
    Menghapus riwayat deteksi buah beserta file gambarnya dari server.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    current_user_id = get_jwt_identity()
    
    try:
        # Cari data deteksi terlebih dahulu
        doc = db.detections.find_one({
            "_id": ObjectId(detection_id),
            "user_id": ObjectId(current_user_id)
        })
        
        if not doc:
            return jsonify({"error": "Riwayat deteksi tidak ditemukan atau Anda tidak memiliki akses"}), 404
            
        # Hapus file gambar fisik dari server lokal
        filename = doc.get("filename")
        if filename:
            upload_folder = current_app.config.get("UPLOAD_FOLDER")
            file_path = os.path.join(upload_folder, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted local file: {file_path}")
                except Exception as file_err:
                    print(f"Warning: Failed to delete local file: {file_err}")
                    
        # Hapus dokumen dari MongoDB Atlas
        db.detections.delete_one({"_id": ObjectId(detection_id)})
        
        return jsonify({"message": "Riwayat deteksi dan file gambar berhasil dihapus!"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Gagal menghapus riwayat: {str(e)}"}), 400
