# Implementation Plan - Flask Backend API for Rotten/Fresh Fruit Detection

A comprehensive, modular, and professional Flask API backend integrated with Roboflow Inference, MongoDB Atlas, and JWT Authentication. This API will be consumed by a Next.js + Electron.js desktop/mobile client.

---

## Architecture Overview

We will transform the single-file `app.py` script into a clean, modular **MVC-like (Blueprints & Controllers)** architecture.

```mermaid
graph TD
    Client[Next.js + Electron Client] <-->|HTTP JSON/JWT| API[Flask API Entrypoint]
    API <-->|Route Blueprints| AuthCtrl[Auth Controller]
    API <-->|Route Blueprints| DetectCtrl[Detection Controller]
    API <-->|Route Blueprints| HistCtrl[History Controller]
    API <-->|Route Blueprints| AnalytCtrl[Analytics Controller]
    
    DetectCtrl <-->|Service Call| Roboflow[Roboflow Service]
    DetectCtrl -->|Save Local File| Storage[(Local static/uploads/)]
    
    AuthCtrl <-->|DB Queries| DB[(MongoDB Atlas Cloud)]
    DetectCtrl <-->|Save Logs| DB
    HistCtrl <-->|Fetch Logs| DB
    AnalytCtrl <-->|Aggregate Stats| DB
```

---

## User Review Required

Please review the following key architectural decisions:
> [!IMPORTANT]
> - **CORS Configuration:** We will use `Flask-CORS` configured to allow requests from any origin (`*`) or specific development ports (like `http://localhost:3000`) so that Next.js and Electron can communicate with the backend without browser security blocks.
> - **MongoDB Connection String:** You will need to provide a MongoDB Atlas Connection String (`MONGO_URI`) in your `.env` file (e.g., `mongodb+srv://<username>:<password>@cluster.mongodb.net/dbname?retryWrites=true&w=majority`).
> - **Local Image Storage:** The uploaded images will be saved in `app/static/uploads/` on the Flask server. The MongoDB database will store the relative web URL (e.g., `/static/uploads/image_name.jpg`) to keep the database lightweight.

---

## Proposed Changes

We will create a structured package under the `app/` directory and update our entrypoint file `app.py`.

### 1. External Dependencies
We will install the following packages in our Python 3.12 virtual environment:
- `pymongo` (MongoDB driver)
- `dnspython` (Required for `mongodb+srv://` URIs)
- `flask-cors` (For cross-origin requests)
- `flask-jwt-extended` (For JWT Authentication)

---

### 2. Configuration & Entrypoint

#### [MODIFY] [app.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app.py)
Re-engineer the entrypoint script to initialize the Flask app package, register Blueprints, and start the development server.

#### [NEW] [config.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/config.py)
Define application settings, database connection strings, JWT configurations, and path constants.

#### [MODIFY] [.env](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/.env)
Add configuration variables for MongoDB, JWT, and upload limits.
```env
MONGO_URI=mongodb+srv://YOUR_USER:YOUR_PASSWORD@cluster0.xxx.mongodb.net/fruit_db?retryWrites=true&w=majority
JWT_SECRET_KEY=super-secret-jwt-key-change-this
UPLOAD_FOLDER=app/static/uploads
```

---

### 3. App Core Package (`app/`)

#### [NEW] [__init__.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app/__init__.py)
Initialize the Flask application, configure CORS, setup `Flask-JWT-Extended`, instantiate the PyMongo client, create upload directories, and register all Blueprints.

---

### 4. Services

#### [NEW] [roboflow_service.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app/services/roboflow_service.py)
Encapsulate all Roboflow Workflow interactions here.
- `run_detection(image_path)`: Send the image to Roboflow and return structured predictions, bounding boxes, and object counts.

---

### 5. Controllers

#### [NEW] [auth_controller.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app/controllers/auth_controller.py)
Handle user registration, login, password hashing, and user profile retrieval.
- `POST /api/auth/register`: Create a new user (with password hashing using `werkzeug.security`).
- `POST /api/auth/login`: Verify credentials and issue access/refresh JWT tokens.
- `GET /api/auth/me` (`@jwt_required`): Fetch currently logged-in user profile details.

#### [NEW] [detection_controller.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app/controllers/detection_controller.py)
Handle the image uploading, model prediction, and log saving.
- `POST /api/detect` (`@jwt_required`):
  1. Save uploaded image to `app/static/uploads/`.
  2. Send it to `RoboflowService`.
  3. Extract rotten/fresh classes and counts.
  4. Save a complete detection log to MongoDB (associated with `current_user_id`).
  5. Return predictions and image metadata.

#### [NEW] [history_controller.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app/controllers/history_controller.py)
Handle retrieval and deletion of past detections.
- `GET /api/history` (`@jwt_required`): Fetch all detection logs associated with the current user, ordered by timestamp.
- `GET /api/history/<id>` (`@jwt_required`): Fetch specific details of a single detection log.
- `DELETE /api/history/<id>` (`@jwt_required`): Delete a detection log and optionally remove the corresponding file from `static/uploads/`.

#### [NEW] [analytics_controller.py](file:///d:/Kuliah/semester4/data%20sains/roboflow-api/app/controllers/analytics_controller.py)
Process detection data to provide insights for your Data Science coursework.
- `GET /api/analytics/summary` (`@jwt_required`): Aggregate statistics for the logged-in user:
  - Total detections performed.
  - Total count of rotten fruits vs fresh fruits.
  - Distribution of the 17 fruit classes.
  - Daily detection volume trend.

---

## Verification Plan

### Automated / API Tests
- Use `curl` or a python test script to run full system tests:
  1. **Register** a test user (`POST /api/auth/register`).
  2. **Login** (`POST /api/auth/login`) to receive a JWT token.
  3. **Upload an image** (`POST /api/detect`) with the JWT header and verify the Roboflow predictions are saved in MongoDB and local storage.
  4. **Fetch history** (`GET /api/history`) and verify the log shows up.
  5. **Fetch analytics** (`GET /api/analytics/summary`) and verify object aggregations.

### Manual Verification
- Share API documentation (endpoints, payloads, and JWT headers) with your classmate so they can hook it up seamlessly to the Next.js / Electron client.
