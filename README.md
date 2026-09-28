# 🚗 Dự Đoán Mức Tiêu Hao Nhiên Liệu Của Xe (Vehicle Fuel Consumption Prediction)

> **Dự án Bài tập lớn môn Học máy cơ bản (Machine Learning)**  
> Hệ thống Machine Learning end-to-end dự đoán mức tiêu thụ nhiên liệu kết hợp (`fuel_consumption_comb` - đơn vị `L/100 km`) dựa trên thông số kỹ thuật xe ô tô. Triển khai hoàn chỉnh với **AI Service (FastAPI)**, **Backend (Node.js/Express + MongoDB)**, và **Frontend (Next.js 14 App Router + TypeScript)**.

---

## 📋 Mục lục

1. [Tổng quan & Kiến trúc hệ thống](#-tổng-quan--kiến-trúc-hệ-thống)
2. [Cấu trúc thư mục dự án](#-cấu-trúc-thư-mục-dự-án)
3. [Mô hình Học máy & Pipeline Huấn luyện](#-mô-hình-học-máy--pipeline-huấn-luyện)
4. [Đặc tả API & Lệnh cURL Kiểm thử Chi tiết](#-đặc-tả-api--lệnh-curl-kiểm-thử-chi-tiết)
   - [POST /api/predict (Dự đoán mức tiêu hao)](#1-post-apipredict---dự-đoán-mức-tiêu-hao-nhiên-liệu)
   - [GET /api/health (Kiểm tra sức khỏe hệ thống)](#2-get-apihealth---kiểm-tra-sức-khỏe-hệ-thống)
   - [GET /api/model-info (Thông tin metadata model)](#3-get-apimodel-info---thông-tin-metadata-model)
   - [GET /api/fields (Danh mục trường & Ngưỡng hợp lệ)](#4-get-apifields---danh-mục-các-trường-và-ngưỡng)
   - [GET /api/predictions (Lịch sử dự đoán phân trang)](#5-get-apipredictions---lấy-danh-sách-lịch-sử-dự-đoán)
   - [GET /api/predictions/stats (Thống kê dự đoán)](#6-get-apipredictionsstats---thống-kê-dữ-liệu-dự-đoán)
   - [Direct AI Service cURL (FastAPI Port 8001)](#7-gọi-trực-tiếp-ai-service-port-8001)
5. [Cấu hình Biến môi trường (.env)](#-cấu-hình-biến-môi-trường-env)
6. [Hướng dẫn Cài đặt & Triển khai](#-hướng-dẫn-cài-đặt--triển-khai)
   - [Cách 1: Khởi chạy nhanh bằng Docker Compose (Khuyên dùng)](#cách-1-khởi-chạy-toàn-bộ-bằng-docker-compose-khuyên-dùng)
   - [Cách 2: Khởi chạy thủ công từng Service (Local)](#cách-2-khởi-chạy-thủ-công-từng-service-local-development)
7. [Kiểm thử Hệ thống (Testing & QA)](#-kiểm-thử-hệ-thống-testing--qa)
8. [Bảng Mã Lỗi & Xử lý Sự Cố (Troubleshooting)](#-bảng-mã-lỗi--xử-lý-sự-cố-troubleshooting)

---

## 🏗 Tổng quan & Kiến trúc hệ thống

Hệ thống được thiết kế theo kiến trúc Microservices phân lớp rõ ràng, đảm bảo tính mở rộng và độc lập giữa các thành phần:

```text
+-----------------------------------------------------------------------------+
|                                FRONTEND                                     |
|           Next.js 14 (App Router) + TypeScript + CSS Modules                |
|           - Giao diện nhập thông số xe & hiển thị kết quả trực quan        |
|           - Dashboard thống kê & Lịch sử tra cứu                            |
+--------------------------------------|--------------------------------------+
                                       | HTTP REST API (Port 8000)
                                       v
+-----------------------------------------------------------------------------+
|                                BACKEND                                      |
|                 Node.js + Express.js + Mongoose + Joi                       |
|           - Request Validation & Serialization                              |
|           - Traceability (Gán X-Request-ID xuyên suốt request)             |
|           - Điều phối và gọi AI Service, ghi log & cache                    |
|           - Lưu trữ lịch sử dự đoán vào MongoDB                             |
+-------------------|--------------------------------------|------------------+
                    |                                      |
       Lưu lịch sử  |                        Chuyển tiếp   | HTTP REST (8001)
                    v                                      v
+-----------------------+              +--------------------------------------+
|       DATABASE        |              |              AI SERVICE              |
|        MongoDB        |              |     Python FastAPI + Scikit-Learn    |
| - Collection:         |              | - Load model 1 lần khi startup       |
|   predictions         |              | - Pipeline tiền xử lý dữ liệu       |
| - Index: request_id   |              | - Model: Support Vector Regressor    |
+-----------------------+              | - Output: fuel_consumption_comb      |
                                       +--------------------------------------+
```

### Nguyên tắc thiết kế (Design Principles):
1. **Traceability**: Mỗi request từ Frontend/Backend đều mang mã định danh duy nhất `X-Request-ID` để truy vết log đồng bộ qua toàn bộ các service.
2. **Schema Uniformity**: Mọi payload JSON trao đổi giữa các tầng đều tuân thủ chuẩn `snake_case`.
3. **High Availability ML Service**: Model ML được nạp sẵn vào bộ nhớ (in-memory) tại thời điểm khởi động AI Service (`lifespan context manager`), tối ưu hóa độ trễ phản hồi (latency < 20ms).

---

## 📁 Cấu trúc thư mục dự án

```text
fuel-consumption-prediction/
├── app/
│   ├── frontend/                   # Ứng dụng giao diện người dùng (Next.js 14)
│   │   ├── src/
│   │   │   ├── app/                # App Router pages & layouts
│   │   │   ├── components/         # UI components (Form, History, Stats, Charts)
│   │   │   ├── services/           # HTTP API client
│   │   │   └── types/              # TypeScript interfaces & types
│   │   ├── Dockerfile              # Docker container cho Frontend
│   │   └── package.json
│   └── backend/                    # API Gateway & Data persistence (Express)
│       ├── src/
│       │   ├── config/             # Cấu hình môi trường & Constants
│       │   ├── controllers/        # Điều phối request (Predict, System)
│       │   ├── middlewares/        # Error handling, Request ID, Validation
│       │   ├── models/             # Mongoose Schema (Prediction)
│       │   ├── routes/             # Định tuyến API
│       │   ├── services/           # Business logic (AI Client, Health, Data)
│       │   └── validators/         # Joi schema validation
│       ├── tests/                  # Unit & Integration tests (Jest, Supertest)
│       ├── Dockerfile              # Docker container cho Backend
│       └── package.json
├── ai-models/                      # Khu vực huấn luyện & AI Microservice
│   ├── colab/                      # Jupyter Notebooks thực nghiệm
│   │   ├── 01_eda.ipynb            # Khám phá và phân tích dữ liệu (EDA)
│   │   ├── 02_preprocess.ipynb     # Tiền xử lý dữ liệu & Feature Engineering
│   │   ├── 03_train.ipynb          # Huấn luyện 4 mô hình Machine Learning
│   │   └── 04_evaluate.ipynb       # Đánh giá, so sánh và chọn mô hình tối ưu
│   ├── data/
│   │   ├── raw/                    # Dữ liệu gốc từ Kaggle
│   │   └── processed/              # Dữ liệu sạch sau tiền xử lý
│   ├── models/
│   │   ├── model.joblib            # Production model đã lưu
│   │   ├── schema.json             # Quy định kiểu dữ liệu & ràng buộc features
│   │   └── metadata.json           # Thông số metrics & phiên bản của model
│   ├── service/                    # FastAPI AI Service
│   │   ├── main.py                 # FastAPI application endpoints
│   │   ├── model_loader.py         # In-memory Model & Schema Loader
│   │   ├── schemas.py              # Pydantic Schemas
│   │   └── Dockerfile              # Docker container cho AI Service
│   ├── src/                        # Python scripts huấn luyện độc lập
│   └── requirements.txt            # Thư viện Python (scikit-learn, fastapi, pandas...)
├── docs/                           # Tài liệu thiết kế, báo cáo, biểu đồ thực nghiệm
├── scripts/                        # Các script khởi chạy nhanh (.bat / .sh)
│   ├── train.bat                   # Huấn luyện mô hình
│   ├── run-local.bat               # Chạy toàn bộ services trên máy local
│   ├── docker-up.bat               # Khởi động Docker Compose
│   └── docker-down.bat             # Dừng và dọn dẹp Docker
├── docker-compose.yml              # Cấu hình triển khai đa container
├── .env.example                    # File mẫu biến môi trường
└── README.md                       # Tài liệu hướng dẫn sử dụng
```

---

## 🤖 Mô hình Học máy & Pipeline Huấn luyện

### 1. Bài toán
- **Loại bài toán**: Hồi quy (Regression).
- **Mục tiêu (Target)**: `fuel_consumption_comb` — Mức tiêu thụ nhiên liệu kết hợp giữa đô thị và đường trường (Đơn vị: **L/100 km**).

### 2. Danh sách 7 Đặc trưng đầu vào (Input Features)
| Tên thuộc tính | Kiểu dữ liệu | Mô tả | Miền giá trị / Ràng buộc |
| :--- | :--- | :--- | :--- |
| `model_year` | Integer | Năm sản xuất xe | `1995` đến `2023` |
| `make` | Category | Hãng xe sản xuất | `TOYOTA`, `HONDA`, `FORD`, `BMW`, `MERCEDES-BENZ`... (55 hãng) |
| `vehicle_class` | Category | Phân khúc dòng xe | `COMPACT`, `SUV - SMALL`, `MID-SIZE`, `PICKUP TRUCK - STANDARD`... |
| `engine_size` | Float | Dung tích động cơ (Lít) | `0.8` đến `8.4` (L) |
| `cylinders` | Integer | Số lượng xi-lanh | `2, 3, 4, 5, 6, 8, 10, 12, 16` |
| `transmission` | Category | Loại hộp số | `A4, A6, A8, A10, AS6, AV, M5, M6...` (32 loại) |
| `fuel_type` | Category | Loại nhiên liệu xe sử dụng | `X` (Xăng thường), `Z` (Xăng cao cấp), `D` (Diesel), `E` (Ethanol E85), `N` (Khí tự nhiên) |

### 3. Kết quả Huấn luyện & So sánh 4 Mô hình
Qua quá trình thực nghiệm và cross-validation trên tập kiểm thử (Test Set):

| Mô hình (Algorithm) | MAE (L/100km) | RMSE (L/100km) | $R^2$ Score (Test) | $R^2$ (Train) | Trạng thái lựa chọn |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Linear Regression** | 0.8120 | 1.1540 | 0.8690 | 0.8710 | Baseline tham chiếu |
| **Decision Tree Regressor** | 0.5140 | 0.7890 | 0.9385 | 0.9850 | Dễ bị quá khớp (overfitting) |
| **KNN Regressor** | 0.5820 | 0.8920 | 0.9210 | 0.9430 | Tốc độ suy luận chậm với dataset lớn |
| **Support Vector Regressor (SVR)** ⭐ | **0.4293** | **0.6498** | **0.9583** | **0.9677** | **Được chọn làm Production Model** |

> **Quyết định**: **SVR** đạt điểm số vượt trội với sai số tuyệt đối trung bình $MAE \approx 0.43$ L/100km và hệ số xác định $R^2 > 95.8\%$, đồng thời có tính tổng quát hóa (generalization) cao nhất.

---

## 📡 Đặc tả API & Lệnh cURL Kiểm thử Chi tiết

Tất cả các API được gọi thông qua **Backend Gateway** (Mặc định: `http://localhost:8000`).

---

### 1. `POST /api/predict` - Dự đoán mức tiêu hao nhiên liệu

Nhận thông tin 7 thông số kỹ thuật của xe và trả về mức tiêu hao nhiên liệu dự đoán.

#### Header:
```http
Content-Type: application/json
X-Request-ID: c56a4180-65aa-42ec-a945-5fd21dec0538 (Tùy chọn, hệ thống tự sinh nếu thiếu)
```

#### Request Body mẫu (JSON):
```json
{
  "model_year": 2022,
  "make": "TOYOTA",
  "vehicle_class": "COMPACT",
  "engine_size": 2.0,
  "cylinders": 4,
  "transmission": "AS6",
  "fuel_type": "X"
}
```

#### Lệnh cURL kiểm thử thành công (200 OK):
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-req-001" \
  -d '{
    "model_year": 2022,
    "make": "TOYOTA",
    "vehicle_class": "COMPACT",
    "engine_size": 2.0,
    "cylinders": 4,
    "transmission": "AS6",
    "fuel_type": "X"
  }'
```

#### Response thành công (200 OK):
```json
{
  "prediction": 7.82,
  "unit": "L/100 km",
  "model_version": "1.0.0",
  "request_id": "test-req-001",
  "created_at": "2026-09-28T13:30:00.123Z"
}
```

---

#### Lệnh cURL kiểm thử dữ liệu xe bán tải (Động cơ lớn):
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2023,
    "make": "FORD",
    "vehicle_class": "PICKUP TRUCK - STANDARD",
    "engine_size": 5.0,
    "cylinders": 8,
    "transmission": "AS10",
    "fuel_type": "X"
  }'
```

#### Response (200 OK):
```json
{
  "prediction": 13.45,
  "unit": "L/100 km",
  "model_version": "1.0.0",
  "request_id": "8fa3211b-7a8e-4a67-b5bb-9d7a8e235e12",
  "created_at": "2026-09-28T13:31:15.890Z"
}
```

---

#### Lệnh cURL kiểm thử dữ liệu SAI / Lỗi Validate (400 Bad Request):
*Trường hợp: `engine_size` vượt quá giới hạn (ví dụ `12.5` L > max `8.4` L) và thiếu trường `fuel_type`.*

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2022,
    "make": "TOYOTA",
    "vehicle_class": "COMPACT",
    "engine_size": 12.5,
    "cylinders": 4,
    "transmission": "AS6"
  }'
```

#### Response lỗi chuẩn hóa (400 Bad Request):
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dữ liệu dự đoán không hợp lệ",
    "details": [
      {
        "field": "engine_size",
        "message": "engine_size phải nằm trong khoảng 0.8 – 8.4"
      },
      {
        "field": "fuel_type",
        "message": "fuel_type là bắt buộc"
      }
    ]
  },
  "request_id": "e81d1ef9-8d19-4822-a9a3-5c74384e5659"
}
```

---

### 2. `GET /api/health` - Kiểm tra sức khỏe hệ thống

Kiểm tra trạng thái kết nối của Backend, AI Service và MongoDB.

#### Lệnh cURL:
```bash
curl -X GET http://localhost:8000/api/health
```

#### Response (200 OK):
```json
{
  "overall_status": "ok",
  "backend": {
    "status": "ok",
    "uptime_seconds": 3600
  },
  "ai_service": {
    "status": "ok",
    "model_loaded": true,
    "model_version": "1.0.0"
  },
  "mongodb": {
    "status": "connected"
  },
  "request_id": "8939e6a7-bfa8-4447-b86e-99042b3ebbf5"
}
```

---

### 3. `GET /api/model-info` - Thông tin metadata model

Lấy thông tin chi tiết về phiên bản thuật toán, ngày huấn luyện, và các chỉ số sai số của model đang phục vụ.

#### Lệnh cURL:
```bash
curl -X GET http://localhost:8000/api/model-info
```

#### Response (200 OK):
```json
{
  "model_name": "svr",
  "model_version": "1.0.0",
  "problem_type": "regression",
  "target": "fuel_consumption_comb",
  "target_unit": "L/100 km",
  "features": [
    "model_year",
    "make",
    "vehicle_class",
    "engine_size",
    "cylinders",
    "transmission",
    "fuel_type"
  ],
  "metrics": {
    "mae": 0.4293,
    "mse": 0.4222,
    "rmse": 0.6498,
    "r2": 0.9583,
    "r2_train": 0.9677
  },
  "trained_at": "2026-09-25 17:05:50",
  "library_versions": {
    "python": "3.14.3",
    "scikit_learn": "1.9.1",
    "numpy": "2.5.3",
    "pandas": "3.0.6"
  }
}
```

---

### 4. `GET /api/fields` - Danh mục các trường và ngưỡng

Cung cấp cho Frontend danh sách các trường và các giá trị biên min/max để cấu hình form validation.

#### Lệnh cURL:
```bash
curl -X GET http://localhost:8000/api/fields
```

#### Response (200 OK):
```json
{
  "fields": [
    "model_year",
    "make",
    "vehicle_class",
    "engine_size",
    "cylinders",
    "transmission",
    "fuel_type"
  ],
  "limits": {
    "model_year": { "min": 1995, "max": 2023 },
    "engine_size": { "min": 0.8, "max": 8.4 },
    "cylinders": { "min": 2, "max": 16 }
  }
}
```

---

### 5. `GET /api/predictions` - Lấy danh sách lịch sử dự đoán

Hỗ trợ phân trang và sắp xếp kết quả từ MongoDB.

#### Query Parameters:
| Tham số | Kiểu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `page` | Integer | `1` | Số thứ tự trang (>= 1) |
| `limit` | Integer | `10` | Số lượng bản ghi trên 1 trang (1 - 100) |
| `sort` | String | `-created_at` | Chiều sắp xếp (`-created_at`: mới nhất, `created_at`: cũ nhất) |

#### Lệnh cURL:
```bash
curl -X GET "http://localhost:8000/api/predictions?page=1&limit=5&sort=-created_at"
```

#### Response (200 OK):
```json
{
  "items": [
    {
      "_id": "6741b2c45e8b4e723912a101",
      "model_year": 2022,
      "make": "TOYOTA",
      "vehicle_class": "COMPACT",
      "engine_size": 2.0,
      "cylinders": 4,
      "transmission": "AS6",
      "fuel_type": "X",
      "prediction": 7.82,
      "unit": "L/100 km",
      "model_version": "1.0.0",
      "request_id": "test-req-001",
      "ai_latency_ms": 12.45,
      "created_at": "2026-09-28T13:30:00.123Z"
    }
  ],
  "page": 1,
  "limit": 5,
  "total": 42,
  "total_pages": 9
}
```

---

### 6. `GET /api/predictions/stats` - Thống kê dữ liệu dự đoán

Tổng hợp các chỉ số thống kê từ MongoDB Aggregation Pipeline.

#### Lệnh cURL:
```bash
curl -X GET http://localhost:8000/api/predictions/stats
```

#### Response (200 OK):
```json
{
  "total_predictions": 42,
  "average_prediction": 9.35,
  "min_prediction": 4.10,
  "max_prediction": 18.20,
  "predictions_by_make": [
    { "make": "FORD", "count": 12 },
    { "make": "TOYOTA", "count": 10 },
    { "make": "HONDA", "count": 8 }
  ]
}
```

---

### 7. Gọi trực tiếp AI Service (Port 8001)

Trong quá trình debug độc lập AI Microservice (FastAPI), có thể gửi request trực tiếp tới port 8001:

#### Lệnh cURL:
```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: direct-ai-test" \
  -d '{
    "features": {
      "model_year": 2021,
      "make": "HONDA",
      "vehicle_class": "MID-SIZE",
      "engine_size": 1.5,
      "cylinders": 4,
      "transmission": "AV",
      "fuel_type": "X"
    }
  }'
```

#### Response:
```json
{
  "prediction": 6.95,
  "unit": "L/100 km",
  "model_version": "1.0.0",
  "request_id": "direct-ai-test"
}
```

---

## ⚙️ Cấu hình Biến môi trường (.env)

Tạo file `.env` tại thư mục gốc của dự án (`/d:/hocmaycoban_btl/.env`) dựa trên `.env.example`:

```ini
# ============================================
# APPLICATION ENVIRONMENT
# ============================================
NODE_ENV=development
ENVIRONMENT=development
LOG_LEVEL=info

# ============================================
# FRONTEND CONFIGURATION
# ============================================
FRONTEND_PORT=3000
# Trình duyệt Client luôn truy cập Backend qua localhost
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_REQUEST_TIMEOUT_MS=15000

# ============================================
# BACKEND CONFIGURATION
# ============================================
PORT=8000
BACKEND_PORT=8000

# Local dev dùng localhost; Docker compose sẽ ghi đè thành http://ai-service:8001
AI_SERVICE_URL=http://localhost:8001
MONGODB_URI=mongodb://localhost:27017/fuel_consumption

REQUEST_TIMEOUT_MS=10000
AI_SERVICE_TIMEOUT_MS=10000
CORS_ORIGIN=http://localhost:3000

# ============================================
# AI SERVICE CONFIGURATION
# ============================================
AI_SERVICE_PORT=8001
MODEL_PATH=../models/model.joblib
SCHEMA_PATH=../models/schema.json
METADATA_PATH=../models/metadata.json
```

---

## 🚀 Hướng dẫn Cài đặt & Triển khai

### Yêu cầu hệ thống (Prerequisites):
- **Docker** & **Docker Compose** (Khuyên dùng)
- Hoặc cài đặt cục bộ:
  - **Node.js**: phiên bản `>= 18.x`
  - **Python**: phiên bản `3.10` - `3.14`
  - **MongoDB Community Server**: phiên bản `>= 6.0` (đang chạy ở port `27017`)

---

### Cách 1: Khởi chạy toàn bộ bằng Docker Compose (Khuyên dùng)

Chỉ với một câu lệnh duy nhất, toàn bộ 4 containers (**MongoDB**, **AI Service**, **Backend Gateway**, **Frontend Client**) sẽ được tự động build và chạy:

```bash
# 1. Clone source code và vào thư mục dự án
cd d:\hocmaycoban_btl

# 2. Tạo file .env từ mẫu (nếu chưa có)
copy .env.example .env

# 3. Khởi động hệ thống (Build và chạy nền)
docker compose up --build -d

# Hoặc dùng script tiện ích trên Windows:
scripts\docker-up.bat
```

#### Kiểm tra trạng thái & Log:
```bash
# Xem log toàn bộ hệ thống theo thời gian thực
docker compose logs -f

# Hoặc xem log từng service
docker compose logs -f ai-service
docker compose logs -f backend

# Dừng hệ thống khi không sử dụng
docker compose down
# Hoặc:
scripts\docker-down.bat
```

#### Truy cập các dịch vụ:
- 🌐 **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- 🔌 **Backend REST API**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- 🧠 **FastAPI Swagger Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)

---

### Cách 2: Khởi chạy thủ công từng Service (Local Development)

#### Bước 1: Chuẩn bị môi trường Python & Train Model
```bash
# Tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo (Windows)
.venv\Scripts\activate

# Cài đặt thư viện AI
pip install -r ai-models/requirements.txt

# (Tùy chọn) Huấn luyện lại model
python ai-models/src/train.py
# Hoặc chạy script:
scripts\train.bat
```

#### Bước 2: Chạy AI Service (Terminal 1)
```bash
.venv\Scripts\activate
cd ai-models
uvicorn service.main:app --host 0.0.0.0 --port 8001 --reload

# Hoặc sử dụng script:
scripts\run-ai.bat
```

#### Bước 3: Chạy Backend (Terminal 2)
```bash
cd app/backend
npm install
npm run dev

# Hoặc sử dụng script:
scripts\run-backend.bat
```

#### Bước 4: Chạy Frontend (Terminal 3)
```bash
cd app/frontend
npm install
npm run dev

# Hoặc sử dụng script:
scripts\run-frontend.bat
```

---

## 🧪 Kiểm thử Hệ thống (Testing & QA)

### 1. Chạy Backend Unit & Integration Tests
Backend sử dụng **Jest** và **mongodb-memory-server** để test độc lập không phụ thuộc database thật:

```bash
cd app/backend
npm test
```

### 2. Test Cases tham chiếu chuẩn để nghiệm thu

| Test Case ID | Xe thử nghiệm | Input Parameters | Kết quả dự kiến ($L/100km$) | Tiêu chí đánh giá |
| :--- | :--- | :--- | :---: | :--- |
| **TC-01** | Toyota Corolla (Sedan cỡ nhỏ) | `year=2022`, `make=TOYOTA`, `class=COMPACT`, `engine=1.8`, `cyl=4`, `trans=AV`, `fuel=X` | **$6.5 - 7.5$** | Tiết kiệm nhiên liệu, phù hợp xe đô thị |
| **TC-02** | Honda Accord (Sedan hạng D) | `year=2021`, `make=HONDA`, `class=MID-SIZE`, `engine=2.0`, `cyl=4`, `trans=AS10`, `fuel=X` | **$7.8 - 8.8$** | Mức tiêu thụ trung bình |
| **TC-03** | Ford F-150 (Bán tải cỡ lớn) | `year=2023`, `make=FORD`, `class=PICKUP TRUCK - STANDARD`, `engine=5.0`, `cyl=8`, `trans=AS10`, `fuel=X` | **$13.0 - 14.5$** | Động cơ V8, tiêu hao nhiên liệu cao |
| **TC-04** | Porsche 911 (Xe thể thao) | `year=2023`, `make=PORSCHE`, `class=TWO-SEATER`, `engine=3.0`, `cyl=6`, `trans=AM8`, `fuel=Z` | **$10.5 - 12.0$** | Xăng cao cấp (Z), công suất cao |

---

## 🚨 Bảng Mã Lỗi & Xử lý Sự Cố (Troubleshooting)

### 1. Bảng mã lỗi HTTP Status Code
| HTTP Code | Error Code | Nguyên nhân | Hướng xử lý |
| :---: | :--- | :--- | :--- |
| `200` | `OK` | Thành công | Không |
| `400` | `INVALID_JSON` / `BAD_REQUEST` | Cú pháp JSON sai hoặc thiếu field | Kiểm tra lại cú pháp request body |
| `422` | `VALIDATION_ERROR` | Giá trị nằm ngoài khoảng cho phép (min/max/category) | Đọc mảng `details` trong response để sửa trường bị lỗi |
| `502` | `AI_SERVICE_UNAVAILABLE` | Backend không thể kết nối tới AI Service | Kiểm tra container `ai-service` hoặc port `8001` đã start chưa |
| `503` | `SERVICE_UNAVAILABLE` | Model ML chưa load xong hoặc service đang khởi động | Đợi 5-10s cho `ai-service` khởi tạo hoàn tất |
| `500` | `INTERNAL_ERROR` | Lỗi server nội bộ hoặc kết nối MongoDB | Kiểm tra log chi tiết qua `docker compose logs` |

### 2. Các sự cố thường gặp & Khắc phục
- **Lỗi `AI Service trả về status 503 (Model not loaded)`**:
  - *Nguyên nhân*: Chưa tìm thấy file `ai-models/models/model.joblib`.
  - *Khắc phục*: Chạy lệnh `python ai-models/src/train.py` để sinh file model trước khi khởi động server.
- **Lỗi `CORS error` khi gọi từ Frontend**:
  - *Nguyên nhân*: Biến `CORS_ORIGIN` trong Backend chưa khớp với URL của Frontend.
  - *Khắc phục*: Đặt `CORS_ORIGIN=http://localhost:3000` trong `.env`.
- **Lỗi `ECONNREFUSED mongodb:27017`**:
  - *Nguyên nhân*: Backend chạy local nhưng để URI của Docker hoặc MongoDB chưa được bật.
  - *Khắc phục*: Đổi `MONGODB_URI=mongodb://localhost:27017/fuel_consumption` khi chạy local.

---

## 👥 Nhóm Tác giả & Đóng góp
- **Đề tài**: Dự đoán mức tiêu hao nhiên liệu của xe (Bài tập lớn Học máy cơ bản)
- **Công nghệ**: Python / FastAPI / Scikit-learn / Node.js / Next.js / MongoDB / Docker
