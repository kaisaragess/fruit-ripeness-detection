from dotenv import load_dotenv
import os

# 1. Load environment variables dari file .env terlebih dahulu
load_dotenv()

# 2. Impor factory function dari app package
from app import create_app

# 3. Buat instance Flask application
app = create_app()

if __name__ == "__main__":
    # Ambil IP Address dari konfigurasi lingkungan (default ke 127.0.0.1)
    host_ip = os.getenv("IP_ADDRESS", "127.0.0.1")
    
    print("=" * 60)
    print("         FRUIT DETECTION MODULAR BACKEND API RUNNING")
    print("=" * 60)
    print(f"Server listens on: http://{host_ip}:5000")
    print("Active Endpoints:")
    print(" - GET  /                      (Welcome & Status Check)")
    print(" - POST /api/auth/register     (User Registration)")
    print(" - POST /api/auth/login        (User Login & Token Issue)")
    print(" - GET  /api/auth/me           (Fetch Authenticated User)")
    print(" - POST /api/detect/           (Upload Fruit Image & Detect)")
    print(" - GET  /api/history/          (Paginated User Detections)")
    print(" - GET  /api/history/<id>      (Specific Detection Details)")
    print(" - DEL  /api/history/<id>      (Delete Log & Local Image)")
    print(" - GET  /api/analytics/summary (Aggregate Data Science Summary)")
    print("=" * 60)
    
    app.run(host=host_ip, port=5000, debug=True)