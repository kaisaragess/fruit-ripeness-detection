from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.services.roboflow_service import RoboflowService
from bson import ObjectId
import os
import uuid
import datetime

detect_bp = Blueprint("detect", __name__)

def parse_predictions(predictions):
    """
    Menganalisis list prediksi dari Roboflow untuk mengklasifikasikan buah segar vs busuk,
    serta menghitung jumlah masing-masing kelas (17 kelas).
    """
    fresh_count = 0
    rotten_count = 0
    breakdown = {}
    
    for pred in predictions:
        class_name = pred.get("class", "").lower()
        if not class_name:
            continue
            
        # Update breakdown kelas buah
        breakdown[class_name] = breakdown.get(class_name, 0) + 1
        
        # Klasifikasikan segar (fresh) vs busuk (rotten)
        if "rotten" in class_name or "busuk" in class_name:
            rotten_count += 1
        elif "fresh" in class_name or "segar" in class_name:
            fresh_count += 1
        else:
            # Jika tidak mengandung keduanya, anggap fresh sebagai default atau abaikan
            fresh_count += 1
            
    return fresh_count, rotten_count, breakdown


@detect_bp.route("/", methods=["POST"])
@jwt_required()
def detect():
    """
    Menerima upload gambar, memprosesnya dengan Roboflow, 
    menyimpannya ke folder lokal dan database MongoDB.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    current_user_id = get_jwt_identity()
    
    # Validasi input gambar
    if "image" not in request.files:
        return jsonify({"error": "File gambar wajib diunggah dengan key 'image'"}), 400
        
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Nama file kosong"}), 400
        
    # Ambil upload folder dari konfigurasi
    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    
    # Buat nama file unik untuk menghindari tabrakan nama file
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        return jsonify({"error": "Format file tidak didukung. Gunakan JPG, JPEG, atau PNG."}), 400
        
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(upload_folder, unique_filename)
    
    try:
        # Simpan file di server lokal
        file.save(saved_path)
        
        # Panggil service Roboflow untuk mendeteksi gambar
        detection_result = RoboflowService.run_detection(saved_path)
        
        predictions = detection_result.get("predictions", [])
        
        # Ekstrak data sains: hitung segar vs busuk & sebaran kelas buah
        fresh_count, rotten_count, breakdown = parse_predictions(predictions)
        total_objects = len(predictions)
        
        # Buat dokumen log deteksi baru untuk disimpan ke MongoDB Atlas
        new_detection = {
            "user_id": ObjectId(current_user_id),
            "filename": unique_filename,
            "image_url": f"/static/uploads/{unique_filename}",
            "count_objects": total_objects,
            "fresh_count": fresh_count,
            "rotten_count": rotten_count,
            "predictions": predictions,  # Menyimpan koordinat & detail bounding box asli
            "breakdown": breakdown,       # Jumlah per jenis buah (misal: {"fresh_apple": 3})
            "timestamp": datetime.datetime.utcnow()
        }
        
        # Simpan ke MongoDB Atlas
        result = db.detections.insert_one(new_detection)
        
        # URL web dari gambar hasil deteksi
        web_image_url = f"{request.host_url.rstrip('/')}/static/uploads/{unique_filename}"
        
        # Bangun respons API yang bersih dan informatif
        response_data = {
            "message": "Deteksi buah berhasil diselesaikan dan dicatat!",
            "detection_id": str(result.inserted_id),
            "image_url": web_image_url,
            "summary": {
                "total_detected": total_objects,
                "fresh_count": fresh_count,
                "rotten_count": rotten_count
            },
            "breakdown": breakdown,
            "predictions": predictions
        }
        
        # Jika workflow Roboflow mengembalikan gambar yang telah dianotasi (base64)
        if detection_result.get("annotated_image"):
            response_data["annotated_image_base64"] = detection_result["annotated_image"]
            
        return jsonify(response_data), 200
        
    except Exception as e:
        # Jika terjadi error saat proses, hapus file yang telanjur disimpan agar tidak sampah
        if os.path.exists(saved_path):
            try:
                os.remove(saved_path)
            except:
                pass
        return jsonify({"error": f"Gagal mendeteksi gambar: {str(e)}"}), 500
