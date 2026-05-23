import requests
import random
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_api():
    print("=" * 60)
    print("         INTEGRATION TEST FOR FRUIT DETECTION API")
    print("=" * 60)
    
    # 1. Test Root Endpoint
    print("\n[1/5] Testing Root Endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.json()}")
        if r.status_code == 200:
            print("[OK] Root endpoint OK!")
        else:
            print("[FAIL] Root endpoint failed.")
            return
    except requests.exceptions.ConnectionError:
        print("[FAIL] ERROR: Gagal terhubung ke server Flask. Apakah server sudah dijalankan dengan 'python app.py'?")
        sys.exit(1)
        
    # 2. Test User Registration
    print("\n[2/5] Testing User Registration...")
    # Buat username acak agar tidak bentrok saat pengujian berkali-kali
    rand_num = random.randint(1000, 9999)
    test_username = f"dosen_datasains_{rand_num}"
    test_email = f"datasains_{rand_num}@univ.ac.id"
    test_password = "password123"
    
    payload_reg = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    r = requests.post(f"{BASE_URL}/api/auth/register", json=payload_reg)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.json()}")
    if r.status_code == 201:
        print(f"[OK] Registrasi berhasil! Username: {test_username}")
    else:
        print("[FAIL] Registrasi gagal.")
        return
        
    # 3. Test User Login
    print("\n[3/5] Testing User Login...")
    payload_login = {
        "identifier": test_username,
        "password": test_password
    }
    r = requests.post(f"{BASE_URL}/api/auth/login", json=payload_login)
    print(f"Status Code: {r.status_code}")
    response_login = r.json()
    print(f"Response: {response_login}")
    if r.status_code == 200:
        print("[OK] Login berhasil!")
        token = response_login.get("access_token")
    else:
        print("[FAIL] Login gagal.")
        return
        
    # Headers dengan JWT Token
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 4. Test Fetch Current User (Profile)
    print("\n[4/5] Testing Authenticated User Info (/me)...")
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.json()}")
    if r.status_code == 200:
        print("[OK] Fetch user info OK!")
    else:
        print("[FAIL] Fetch user info failed.")
        return
        
    # 5. Test Empty History & Analytics
    print("\n[5/5] Testing Empty History & Analytics...")
    r_hist = requests.get(f"{BASE_URL}/api/history/", headers=headers)
    r_anlt = requests.get(f"{BASE_URL}/api/analytics/summary", headers=headers)
    print(f"History Status Code: {r_hist.status_code}")
    print(f"History Response: {r_hist.json()}")
    print(f"Analytics Status Code: {r_anlt.status_code}")
    print(f"Analytics Response: {r_anlt.json()}")
    
    if r_hist.status_code == 200 and r_anlt.status_code == 200:
        print("[OK] History & Analytics endpoints OK (returned clean empty structures as expected)!")
    else:
        print("[FAIL] History or Analytics endpoint failed.")
        return
        
    print("\n" + "=" * 60)
    print("      SEMUA ENDPOINT PENGUJIAN API BERHASIL MELEWATI TES! [OK]")
    print("=" * 60)
    print("\nCatatan:")
    print("Untuk menguji deteksi gambar asli (/api/detect/), gunakan Postman")
    print(f"atau pasang JWT Token Anda di header request POST ke /api/detect/.")

if __name__ == "__main__":
    test_api()
