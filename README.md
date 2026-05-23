# Fruit Ripeness Detection Flask API 🍎🍌

Backend API modular berbasis Python Flask untuk mendeteksi tingkat kematangan buah (17 kelas, segar/rotten) terintegrasi dengan **Roboflow Inference SDK** dan **MongoDB**. API ini dirancang untuk dapat dikonsumsi dengan mudah oleh aplikasi frontend berbasis **Next.js** dan **Electron.js**.

---

## 🚀 Panduan Setup & Menjalankan di Lokal (Untuk Teman Kelompok)

Gunakan panduan ini untuk menyalin (*fork*), mengunduh, dan menjalankan backend ini di laptop Anda secara mandiri.

### 1. Lakukan Fork & Clone Repository
Langkah ini penting agar Anda memiliki salinan repository sendiri di akun GitHub Anda sebelum mengunduhnya:

1. Buka halaman utama repository GitHub ini.
2. Klik tombol **Fork** di pojok kanan atas halaman untuk menduplikat repository ini ke akun GitHub Anda.
3. Setelah proses fork selesai, buka terminal/command prompt di komputer Anda, lalu jalankan perintah berikut untuk mengunduhnya ke laptop Anda (ganti `<username-kamu>` dengan username GitHub Anda):
   ```bash
   git clone https://github.com/<username-kamu>/fruit-ripeness-detection.git
   cd fruit-ripeness-detection
   ```

---

### 2. Prasyarat Sistem (Prerequisites)
Sebelum menjalankan, pastikan laptop Anda sudah memiliki komponen berikut:

* **Python 3.12 (PENTING! ⚠️):** Roboflow SDK saat ini belum mendukung Python 3.13 ke atas. Pastikan laptop Anda menggunakan Python 3.12.
  * *Tip Windows:* Jika belum ada, Anda bisa memasangnya lewat command prompt dengan perintah: `winget install --id Python.Python.3.12 --exact`.
* **MongoDB Community Server:** Pastikan MongoDB Lokal sudah terpasang dan berstatus **Running** pada Windows Service Anda.

---

### 3. Pembuatan Virtual Environment & Instalasi Library
Masuk ke direktori proyek utama di terminal Anda, lalu jalankan langkah berikut:

**A. Membuat Virtual Environment (venv):**
```powershell
py -3.12 -m venv venv
```

**B. Mengaktifkan Virtual Environment:**
* **PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Command Prompt (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
*(Setelah aktif, akan muncul tulisan `(venv)` di sebelah kiri baris terminal Anda).*

**C. Menginstal Semua Library Pendukung:**
Jalankan perintah berikut untuk memasang seluruh kebutuhan dependensi sekaligus:
```powershell
pip install -r requirements.txt
```

---

### 4. Konfigurasi Environment Variables (`.env`)
Karena file `.env` yang berisi kode rahasia diabaikan oleh Git, Anda perlu membuat file konfigurasi baru di laptop Anda secara manual:

1. Buat file baru bernama **`.env`** tepat di root folder proyek (`fruit-ripeness-detection/`).
2. Salin dan tempel (paste) kode templat konfigurasi di bawah ini:

```env
# Roboflow API Configuration
ROBOFLOW_API_KEY=0b1jJp0GBdd7Obqtewf2
ROBOFLOW_API_URL=https://serverless.roboflow.com
ROBOFLOW_WORKSPACE=15240772s-workspace-v3t3g
ROBOFLOW_WORKFLOW_ID=detect-count-and-visualize-3

# Flask & JWT Security Keys
SECRET_KEY=9b827efc9281a021bc829cd128a38719
JWT_SECRET_KEY=738dfc10928bb8c983a91c28c8efd918

# Database Configuration (MongoDB Lokal)
MONGO_URI=mongodb://localhost:27017/fruit_db

# Network Configuration
IP_ADDRESS=127.0.0.1
```

---

### 5. Menjalankan Server API Lokal
Pastikan virtual environment `(venv)` dalam keadaan aktif, lalu jalankan server:
```powershell
python app.py
```

Jika server berhasil menyala, Anda akan melihat tampilan log info daftar endpoint aktif di terminal Anda:
```text
============================================================
         FRUIT DETECTION MODULAR BACKEND API RUNNING
============================================================
Server listens on: http://127.0.0.1:5000
...
```

---

### 6. Verifikasi & Pengujian Otomatis
Untuk memastikan seluruh endpoint (Root, Registrasi, Login JWT, Profile `/me`, History, dan Analytics) berjalan tanpa ada kendala di laptop Anda, buka terminal baru (pastikan `venv` aktif) dan jalankan script pengujian terintegrasi:
```powershell
python test_api.py
```
*Jika semuanya berjalan lancar, Anda akan melihat pesan penutup:* 
`SEMUA ENDPOINT PENGUJIAN API BERHASIL MELEWATI TES! [OK]`

---

## 🛠️ Ringkasan Endpoints API (Untuk Pengembangan Next.js / Electron)

Seluruh request API di bawah ini menggunakan format JSON (kecuali upload gambar).

| Method | Endpoint | Keterangan | Proteksi | Content-Type |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | Cek status running server & koneksi MongoDB | Public | `application/json` |
| **POST** | `/api/auth/register` | Mendaftarkan akun pengguna baru | Public | `application/json` |
| **POST** | `/api/auth/login` | Login user untuk mendapatkan Token JWT | Public | `application/json` |
| **GET** | `/api/auth/me` | Mengambil data profil user yang sedang login | `JWT Bearer` | `application/json` |
| **POST** | `/api/detect/` | Mengunggah gambar buah untuk dideteksi & di-log | `JWT Bearer` | `multipart/form-data` |
| **GET** | `/api/history/` | Mengambil daftar riwayat deteksi user (Paginasi) | `JWT Bearer` | `application/json` |
| **GET** | `/api/history/<id>` | Detail satu riwayat deteksi buah tertentu | `JWT Bearer` | `application/json` |
| **DELETE** | `/api/history/<id>` | Menghapus riwayat deteksi & gambar fisiknya | `JWT Bearer` | `application/json` |
| **GET** | `/api/analytics/summary` | Agregasi data statistik segar/busuk & tren harian | `JWT Bearer` | `application/json` |

---

## 📈 Struktur Payload Utama `/api/analytics/summary` (Untuk Grafik)

Endpoint ini sangat ramah untuk data sains karena mengembalikan data agregat terstruktur yang siap digambar menjadi diagram/grafik di Next.js:

```json
{
  "summary": {
    "total_sessions": 12,
    "total_objects": 48,
    "total_fresh": 36,
    "total_rotten": 12,
    "fresh_ratio_percent": 75.0,
    "rotten_ratio_percent": 25.0
  },
  "class_distribution": {
    "fresh-apple": 18,
    "rotten-apple": 8,
    "fresh-banana": 12,
    "rotten-banana": 4,
    "fresh-orange": 6
  },
  "daily_trend": [
    {
      "date": "2026-05-22",
      "sessions": 2,
      "total_detected": 8,
      "fresh_count": 6,
      "rotten_count": 2
    },
    {
      "date": "2026-05-23",
      "sessions": 5,
      "total_detected": 15,
      "fresh_count": 12,
      "rotten_count": 3
    }
  ]
}
```
*Gunakan `class_distribution` untuk membuat **Donut/Pie Chart** dan `daily_trend` untuk membuat **Line/Bar Chart**.*
