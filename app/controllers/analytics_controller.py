from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from bson import ObjectId
import datetime

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_analytics_summary():
    """
    Menyusun analisis data sains lengkap mengenai buah segar vs busuk yang terdeteksi
    oleh pengguna yang sedang login. Output sangat cocok untuk dijadikan bahan visualisasi grafik.
    """
    if db is None:
        return jsonify({"error": "Database connection is not available"}), 500
        
    current_user_id = get_jwt_identity()
    user_oid = ObjectId(current_user_id)
    
    try:
        # Pipeline Agregasi Utama: Menghitung total deteksi, total objek, fresh, dan rotten
        pipeline_summary = [
            {"$match": {"user_id": user_oid}},
            {
                "$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "total_objects": {"$sum": "$count_objects"},
                    "total_fresh": {"$sum": "$fresh_count"},
                    "total_rotten": {"$sum": "$rotten_count"}
                }
            }
        ]
        
        summary_result = list(db.detections.aggregate(pipeline_summary))
        
        if not summary_result:
            # Jika user belum pernah melakukan deteksi
            return jsonify({
                "summary": {
                    "total_sessions": 0,
                    "total_objects": 0,
                    "total_fresh": 0,
                    "total_rotten": 0,
                    "fresh_ratio_percent": 0.0,
                    "rotten_ratio_percent": 0.0
                },
                "class_distribution": {},
                "daily_trend": []
            }), 200
            
        stats = summary_result[0]
        total_objects = stats.get("total_objects", 0)
        total_fresh = stats.get("total_fresh", 0)
        total_rotten = stats.get("total_rotten", 0)
        
        # Hitung rasio persentase
        fresh_ratio = round((total_fresh / total_objects) * 100, 2) if total_objects > 0 else 0.0
        rotten_ratio = round((total_rotten / total_objects) * 100, 2) if total_objects > 0 else 0.0
        
        # Agregasikan distribusi kelas buah (17 kelas)
        # Ambil semua data deteksi milik user
        all_detections = db.detections.find({"user_id": user_oid}, {"breakdown": 1})
        class_distribution = {}
        for doc in all_detections:
            breakdown = doc.get("breakdown", {})
            for fruit_class, count in breakdown.items():
                class_distribution[fruit_class] = class_distribution.get(fruit_class, 0) + count
                
        # Urutkan distribusi kelas dari yang terbanyak
        sorted_distribution = dict(sorted(class_distribution.items(), key=lambda item: item[1], reverse=True))
        
        # Agregasikan tren deteksi harian (14 hari terakhir)
        two_weeks_ago = datetime.datetime.utcnow() - datetime.timedelta(days=14)
        pipeline_trend = [
            {
                "$match": {
                    "user_id": user_oid,
                    "timestamp": {"$gte": two_weeks_ago}
                }
            },
            {
                "$project": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count_objects": 1,
                    "fresh_count": 1,
                    "rotten_count": 1
                }
            },
            {
                "$group": {
                    "_id": "$date",
                    "total_detected": {"$sum": "$count_objects"},
                    "fresh_count": {"$sum": "$fresh_count"},
                    "rotten_count": {"$sum": "$rotten_count"},
                    "sessions": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}  # Urutkan kronologis berdasarkan tanggal
        ]
        
        trend_result = list(db.detections.aggregate(pipeline_trend))
        
        formatted_trends = []
        for day in trend_result:
            formatted_trends.append({
                "date": day["_id"],
                "sessions": day["sessions"],
                "total_detected": day["total_detected"],
                "fresh_count": day["fresh_count"],
                "rotten_count": day["rotten_count"]
            })
            
        return jsonify({
            "summary": {
                "total_sessions": stats.get("total_sessions", 0),
                "total_objects": total_objects,
                "total_fresh": total_fresh,
                "total_rotten": total_rotten,
                "fresh_ratio_percent": fresh_ratio,
                "rotten_ratio_percent": rotten_ratio
            },
            "class_distribution": sorted_distribution,
            "daily_trend": formatted_trends
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Gagal menyusun ringkasan data sains: {str(e)}"}), 500
