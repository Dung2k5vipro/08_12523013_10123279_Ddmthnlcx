# 🚗 Dự Đoán Mức Tiêu Hao Nhiên Liệu Của Xe (Vehicle Fuel Consumption Prediction)

> **Dự án Bài tập lớn môn Học máy cơ bản (Machine Learning)**  
> Hệ thống Machine Learning end-to-end dự đoán mức tiêu thụ nhiên liệu kết hợp (`fuel_consumption_comb` - đơn vị `L/100 km`) dựa trên thông số kỹ thuật xe ô tô. Triển khai hoàn chỉnh với **AI Service (FastAPI)**, **Backend (Node.js/Express + MongoDB)**, và **Frontend (Next.js 14 App Router + TypeScript)**.

---

## ⚡ HƯỚNG DẪN TEST NHANH API (QUICK START - 4 BƯỚC)

Dành cho Giảng viên / Người đánh giá / Sinh viên test nhanh hệ thống chỉ trong 1 phút.

### 🔹 Bước 1: Khởi động hệ thống
Mở Terminal tại thư mục dự án và chạy:
```bash
docker compose up --build -d
```
*(Hoặc nếu chạy local không dùng Docker: chạy file `scripts\run-local.bat`)*

---

### 🔹 Bước 2: Kiểm tra sức khỏe hệ thống (Health Check)
Mở trình duyệt hoặc chạy cURL để xác nhận Backend, AI Service và Database đã sẵn sàng:
```bash
curl -X GET http://localhost:8000/api/health
```
**Kết quả mong đợi (200 OK):**
```json
{
  "overall_status": "ok",
  "backend": { "status": "ok" },
  "ai_service": { "status": "ok", "model_loaded": true, "model_version": "1.0.0" },
  "mongodb": { "status": "connected" }
}
```

---

### 🔹 Bước 3: Gửi Request Test Dự Đoán (cURL One-Liner)
Copy và dán lệnh sau vào Terminal (PowerShell / Git Bash / CMD / Linux):

```bash
curl -X POST http://localhost:8000/api/predict -H "Content-Type: application/json" -d "{\"model_year\":2022,\"make\":\"TOYOTA\",\"vehicle_class\":\"COMPACT\",\"engine_size\":2.0,\"cylinders\":4,\"transmission\":\"AS6\",\"fuel_type\":\"X\"}"
```

**Kết quả trả về ngay lập tức (200 OK):**
```json
{
  "prediction": 7.82,
  "unit": "L/100 km",
  "model_version": "1.0.0",
  "request_id": "06e8b4e7-2391-4101-8b4e-723912a10123",
  "created_at": "2026-09-28T13:30:00.123Z"
}
```

---

### 🔹 Bước 4: Chạy công cụ Spam Load Test tự động (Trước giờ G)
Dự án đã tích hợp sẵn công cụ tự động gửi hàng loạt request (spam test / load test / benchmark) để kiểm tra độ ổn định và độ trễ của server:

```bash
# Chạy script test tự động (Gửi 50 requests song song):
scripts\test.bat

# Hoặc tùy biến số lượng request và số worker:
python scripts/test_api.py --url http://localhost:8000 --spam 100 --concurrency 10
```

---

## 📋 Mục lục Chi tiết

1. [Hướng dẫn Xem Log Realtime khi nhận Spam Test](#-hướng-dẫn-xem-log-realtime-khi-nhận-spam-test)
2. [Các phương thức Kiểm thử API (cURL, Postman, Swagger, UI)](#-các-phương-thức-kiểm-thử-api)
3. [Đặc tả Chi tiết Danh mục API (API Specification)](#-đặc-tả-chi-tiết-danh-mục-api)
4. [Bộ Test Cases mẫu để nghiệm thu kết quả](#-bộ-test-cases-mẫu-để-nghiệm-thu-kết-quả)
5. [Kiến trúc Hệ thống & Luồng Dữ liệu](#-kiến-trúc-hệ-thống--luồng-dữ-liệu)
6. [Mô hình Học máy & Pipeline](#-mô-hình-học-máy--pipeline)
7. [Cấu hình Biến môi trường (.env)](#-cấu-hình-biến-môi-trường-env)
8. [Hướng dẫn Cài đặt & Triển khai chi tiết](#-hướng-dẫn-cài-đặt--triển-khai-chi-tiết)
9. [Bảng Mã Lỗi & Troubleshooting](#-bảng-mã-lỗi--troubleshooting)

---

## 📊 Hướng dẫn Xem Log Realtime khi nhận Spam Test

Khi có lượng lớn request spam test bắn vào server, bạn cần mở một cửa sổ Terminal riêng để theo dõi log trực tiếp:

### 1. Nếu chạy bằng Docker (Khuyên dùng)
```bash
# Xem log toàn bộ hệ thống (kết hợp cả Backend, AI Service, Database):
docker compose logs -f

# Chỉ xem log Backend (theo dõi các request đến và mã HTTP status):
docker compose logs -f backend

# Chỉ xem log AI Service (theo dõi tốc độ suy luận của model ML):
docker compose logs -f ai-service
```

### 2. Nếu chạy Local (Terminal độc lập)
- **Terminal Backend**: Quan sát dòng log:
  ```text
  [INFO] 2026-09-28 20:30:15 POST /api/predict 200 - 14.25ms [req=spam-req-0042]
  ```
- **Terminal AI Service**: Quan sát dòng log:
  ```text
  [INFO] req=spam-req-0042 prediction=7.82 unit='L/100 km' version=1.0.0 time=3.12ms
  ```

### 3. Cấu trúc log chuẩn Traceability:
Mỗi request đi qua hệ thống đều được in ra với:
- `X-Request-ID`: Mã định danh để truy vết đúng request bị lỗi giữa Backend và AI Service.
- `Latency`: Thời gian xử lý (ms).
- `Status`: Mã HTTP (`200` thành công, `400/422` dữ liệu sai, `502/503` lỗi kết nối AI).

---

## 🛠 Các phương thức Kiểm thử API

### Cách 1: Sử dụng Postman / Thunder Client / Insomnia
1. **Method**: `POST`
2. **URL**: `http://localhost:8000/api/predict`
3. **Headers**:
   - `Content-Type`: `application/json`
   - `X-Request-ID`: `postman-test-01` *(Tùy chọn)*
4. **Body (Raw JSON)**:
   ```json
   {
     "model_year": 2022,
     "make": "HONDA",
     "vehicle_class": "MID-SIZE",
     "engine_size": 2.0,
     "cylinders": 4,
     "transmission": "AS10",
     "fuel_type": "X"
   }
   ```

---

### Cách 2: Sử dụng Swagger UI trực tiếp của AI Service
- Truy cập trình duyệt: [http://localhost:8001/docs](http://localhost:8001/docs)
- Chọn endpoint `POST /predict` $\rightarrow$ Nhấn **Try it out** $\rightarrow$ Dán JSON $\rightarrow$ Nhấn **Execute**.

---

### Cách 3: Sử dụng Giao diện Web Frontend
- Mở trình duyệt tại [http://localhost:3000](http://localhost:3000).
- Chọn hãng xe, năm sản xuất, dung tích xi-lanh và nhấn **"Dự đoán ngay"**.
- Xem kết quả hiển thị trực quan và tra cứu lại lịch sử trong bảng phía dưới.

---

## 📡 Đặc tả Chi tiết Danh mục API

Tất cả các API được gọi thông qua **Backend Gateway** (Mặc định: `http://localhost:8000`).

---

### 1. `POST /api/predict` - Dự đoán mức tiêu hao nhiên liệu

Nhận thông số kỹ thuật 7 trường của xe và trả về mức tiêu hao nhiên liệu dự đoán.

#### Danh sách 7 Trường đầu vào (Parameters):
| Thuộc tính | Kiểu | Bắt buộc | Ràng buộc giá trị | Mô tả |
| :--- | :--- | :---: | :--- | :--- |
| `model_year` | Integer | Có | `1995 - 2023` | Năm sản xuất |
| `make` | String | Có | Danh sách 55 hãng (VD: `TOYOTA`, `HONDA`, `FORD`, `BMW`...) | Hãng sản xuất xe |
| `vehicle_class` | String | Có | VD: `COMPACT`, `MID-SIZE`, `SUV - SMALL`, `PICKUP TRUCK - STANDARD` | Phân khúc dòng xe |
| `engine_size` | Float | Có | `0.8 - 8.4` (Lít) | Dung tích động cơ |
| `cylinders` | Integer | Có | `2, 3, 4, 5, 6, 8, 10, 12, 16` | Số xi-lanh |
| `transmission` | String | Có | VD: `AS6`, `AS10`, `AV`, `AM8`, `M6` (32 loại) | Loại hộp số |
| `fuel_type` | String | Có | `X` (Xăng thường), `Z` (Xăng cao cấp), `D` (Diesel), `E` (Ethanol), `N` (Khí tự nhiên) | Loại nhiên liệu |

#### Request cURL (Dòng xe phổ thông):
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req-toyota-001" \
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
  "request_id": "req-toyota-001",
  "created_at": "2026-09-28T13:30:00.123Z"
}
```

---

#### Test Case lỗi Validation (400 Bad Request):
*Trường hợp truyền `engine_size = 25.0` (vượt ngưỡng 8.4) và thiếu trường `fuel_type`:*

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2022,
    "make": "TOYOTA",
    "vehicle_class": "COMPACT",
    "engine_size": 25.0,
    "cylinders": 4,
    "transmission": "AS6"
  }'
```

#### Response lỗi chi tiết (400 Bad Request):
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

### 2. `GET /api/health` - Trạng thái sức khỏe hệ thống
```bash
curl -X GET http://localhost:8000/api/health
```

---

### 3. `GET /api/model-info` - Metadata & Metrics của Model ML
```bash
curl -X GET http://localhost:8000/api/model-info
```
**Response mẫu:**
```json
{
  "model_name": "svr",
  "model_version": "1.0.0",
  "problem_type": "regression",
  "target": "fuel_consumption_comb",
  "target_unit": "L/100 km",
  "metrics": {
    "mae": 0.4293,
    "mse": 0.4222,
    "rmse": 0.6498,
    "r2": 0.9583,
    "r2_train": 0.9677
  },
  "trained_at": "2026-09-25 17:05:50"
}
```

---

### 4. `GET /api/predictions` - Lịch sử dự đoán (Phân trang)
```bash
curl -X GET "http://localhost:8000/api/predictions?page=1&limit=5&sort=-created_at"
```

---

### 5. `GET /api/predictions/stats` - Thống kê tổng quan
```bash
curl -X GET http://localhost:8000/api/predictions/stats
```

---

## 🧪 Bộ Test Cases mẫu để nghiệm thu kết quả

| ID | Dòng xe đại diện | Body JSON Test | Kết quả dự kiến ($L/100km$) | Đánh giá |
| :--- | :--- | :--- | :---: | :--- |
| **TC-01** | Toyota Corolla (Sedan tiết kiệm) | `{"model_year":2022,"make":"TOYOTA","vehicle_class":"COMPACT","engine_size":1.8,"cylinders":4,"transmission":"AV","fuel_type":"X"}` | **$6.5 - 7.5$** | ✅ Đạt chuẩn xe đô thị |
| **TC-02** | Honda Accord (Sedan hạng D) | `{"model_year":2021,"make":"HONDA","vehicle_class":"MID-SIZE","engine_size":2.0,"cylinders":4,"transmission":"AS10","fuel_type":"X"}` | **$7.8 - 8.8$** | ✅ Mức trung bình |
| **TC-03** | Ford F-150 (Bán tải cỡ lớn) | `{"model_year":2023,"make":"FORD","vehicle_class":"PICKUP TRUCK - STANDARD","engine_size":5.0,"cylinders":8,"transmission":"AS10","fuel_type":"X"}` | **$13.0 - 14.5$** | ✅ Tiêu hao cao (Động cơ V8) |
| **TC-04** | Porsche 911 (Xe thể thao) | `{"model_year":2023,"make":"PORSCHE","vehicle_class":"TWO-SEATER","engine_size":3.0,"cylinders":6,"transmission":"AM8","fuel_type":"Z"}` | **$10.5 - 12.0$** | ✅ Xăng cao cấp (Z) |

---

## 🏗 Kiến trúc Hệ thống & Luồng Dữ liệu

```text
+-----------------------------------------------------------------------------+
|                                FRONTEND                                     |
|           Next.js 14 (App Router) + TypeScript + CSS Modules                |
+--------------------------------------|--------------------------------------+
                                       | HTTP REST API (Port 8000)
                                       v
+-----------------------------------------------------------------------------+
|                                BACKEND                                      |
|                 Node.js + Express.js + Mongoose + Joi                       |
|           - Validate Schema, gán X-Request-ID, gọi AI Service               |
|           - Lưu trữ lịch sử vào MongoDB                                     |
+-------------------|--------------------------------------|------------------+
                    |                                      |
       Lưu lịch sử  |                        Chuyển tiếp   | HTTP REST (8001)
                    v                                      v
+-----------------------+              +--------------------------------------+
|       DATABASE        |              |              AI SERVICE              |
|        MongoDB        |              |     Python FastAPI + Scikit-Learn    |
|   (Port 27017)        |              | - Load model sẵn vào RAM             |
|                       |              | - Thuật toán SVR ($R^2=0.9583$)      |
+-----------------------+              +--------------------------------------+
```

---

## 🤖 Mô hình Học máy & Pipeline

- **Bài toán**: Hồi quy (Regression).
- **Target**: `fuel_consumption_comb` (L/100 km).
- **So sánh 4 thuật toán**:
  - *Linear Regression*: $R^2 = 0.8690, MAE = 0.8120$
  - *Decision Tree Regressor*: $R^2 = 0.9385, MAE = 0.5140$
  - *KNN Regressor*: $R^2 = 0.9210, MAE = 0.5820$
  - **Support Vector Regressor (SVR)** ⭐: **$R^2 = 0.9583, MAE = 0.4293$** (Model chính thức).

---

## ⚙️ Cấu hình Biến môi trường (.env)

Tạo file `.env` tại thư mục gốc của dự án (`.env`) dựa trên file mẫu `.env.example`:

```ini
# ENVIRONMENT
NODE_ENV=development
LOG_LEVEL=info

# FRONTEND
FRONTEND_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# BACKEND
PORT=8000
BACKEND_PORT=8000
AI_SERVICE_URL=http://localhost:8001
MONGODB_URI=mongodb://localhost:27017/fuel_consumption
CORS_ORIGIN=http://localhost:3000

# AI SERVICE
AI_SERVICE_PORT=8001
MODEL_PATH=../models/model.joblib
SCHEMA_PATH=../models/schema.json
METADATA_PATH=../models/metadata.json
```

---

## 🚀 Hướng dẫn Cài đặt & Triển khai chi tiết

### Cách 1: Khởi chạy bằng Docker Compose (Khuyên dùng)
```bash
# 1. Clone và vào thư mục repo
cd fuel-consumption-prediction

# 2. Khởi động hệ thống
docker compose up --build -d

# 3. Xem log hoạt động
docker compose logs -f

# 4. Dừng hệ thống khi kết thúc
docker compose down
```

### Cách 2: Khởi chạy thủ công từng Service (Local)
1. **AI Service** (Terminal 1):
   ```bash
   .venv\Scripts\activate
   pip install -r ai-models/requirements.txt
   uvicorn service.main:app --host 0.0.0.0 --port 8001 --reload
   ```
2. **Backend Gateway** (Terminal 2):
   ```bash
   cd app/backend
   npm install
   npm run dev
   ```
3. **Frontend UI** (Terminal 3):
   ```bash
   cd app/frontend
   npm install
   npm run dev
   ```

---

## 🚨 Bảng Mã Lỗi & Troubleshooting

| HTTP Code | Error Code | Nguyên nhân | Hướng khắc phục |
| :---: | :--- | :--- | :--- |
| `200` | `OK` | Dự đoán thành công | Bình thường |
| `400` | `INVALID_JSON` / `VALIDATION_ERROR` | Thiếu trường hoặc sai kiểu dữ liệu | Kiểm tra lại body JSON theo schema |
| `422` | `OUT_OF_RANGE` | Giá trị nằm ngoài khoảng biên cho phép | Đối chiếu bảng giới hạn min/max |
| `502` | `AI_SERVICE_UNAVAILABLE` | Backend không kết nối được AI Service | Kiểm tra port `8001` hoặc container `ai-service` |
| `503` | `SERVICE_UNAVAILABLE` | Model ML đang nạp hoặc service khởi động lại | Chờ 5 giây và thử lại |
| `500` | `INTERNAL_ERROR` | Lỗi cơ sở dữ liệu MongoDB | Kiểm tra kết nối MongoDB qua `docker compose logs mongodb` |
