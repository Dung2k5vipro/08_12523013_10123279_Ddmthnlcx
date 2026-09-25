# Fuel Consumption Backend

Backend Express/CommonJS cho API dự đoán mức tiêu hao nhiên liệu xe. Backend nhận payload snake_case, validate dữ liệu, chuyển tiếp yêu cầu tới AI Service, lưu kết quả vào MongoDB và trả response thống nhất có `request_id`.

## Cấu trúc

```text
backend/
├── src/
│   ├── config/        # env, MongoDB, constants
│   ├── controllers/   # lớp HTTP mỏng
│   ├── middlewares/   # request ID, logging, validation, errors
│   ├── models/        # Mongoose models
│   ├── routes/        # API routes
│   ├── services/      # nghiệp vụ, AI client, health
│   ├── utils/         # AppError, logger, async handler
│   ├── validators/    # Joi schemas
│   └── app.js
├── tests/
├── Dockerfile
├── jest.config.js
└── package.json
```

## Biến môi trường

| Biến | Bắt buộc | Mô tả |
|---|---:|---|
| `PORT` | Có | Cổng Backend |
| `NODE_ENV` | Không | `development`, `test` hoặc `production` |
| `MONGODB_URI` | Có | MongoDB URI |
| `AI_SERVICE_URL` | Có | Base URL của AI Service |
| `AI_SERVICE_TIMEOUT_MS` | Không | Timeout gọi AI, mặc định 10000 ms |
| `CORS_ORIGIN` | Không | Origin frontend được phép |
| `LOG_LEVEL` | Không | `error`, `warn`, `info` hoặc `debug` |

Copy `.env.example` thành `.env` trước khi chạy local. Trong Docker, `docker-compose.yml` override `MONGODB_URI` và `AI_SERVICE_URL` bằng tên service nội bộ.

## Chạy local

Đảm bảo MongoDB và AI Service đã sẵn sàng, sau đó chạy:

```bat
scripts\run-backend.bat
```

Hoặc thủ công:

```bat
cd app\backend
npm install
npm run dev
```

Chạy test:

```bat
cd app\backend
npm test
```

## Chạy Docker

Từ thư mục gốc dự án:

```bat
scripts\docker-up.bat
```

Backend trong Docker gọi AI Service qua `AI_SERVICE_URL` của service `ai-service`, không gọi localhost.

## API

Mọi request có thể gửi header `X-Request-ID`. Nếu thiếu, Backend tự sinh UUID v4 và trả lại cùng giá trị trong response header và body khi có body response.

| Method | Path | Body/query | Response thành công | Status |
|---|---|---|---|---|
| `POST` | `/api/predict` | 7 field dự đoán | prediction response | 200 |
| `GET` | `/api/predictions` | `page`, `limit`, `sort` | danh sách phân trang | 200 |
| `GET` | `/api/predictions/stats` | Không có | thống kê | 200 |
| `GET` | `/api/predictions/:id` | Mongo ObjectId | một prediction | 200 |
| `GET` | `/api/health` | Không có | trạng thái hệ thống | 200 hoặc 503 |
| `GET` | `/api/model-info` | Không có | thông tin model từ AI | 200 |
| `GET` | `/api/fields` | Không có | field và giới hạn form | 200 |

### `POST /api/predict`

Request:

```json
{
  "model_year": 2020,
  "make": "Toyota",
  "vehicle_class": "SUV",
  "engine_size": 2.0,
  "cylinders": 4,
  "transmission": "Automatic",
  "fuel_type": "X"
}
```

Response:

```json
{
  "prediction": 7.2,
  "unit": "L/100 km",
  "model_version": "model-v1",
  "request_id": "3d8a0f5a-3e77-4c71-9d53-9f5b3266d4cd",
  "created_at": "2026-09-25T10:00:00.000Z"
}
```

### `GET /api/predictions`

Query mặc định: `page=1`, `limit=10`, `sort=-created_at`. `limit` từ 1 đến 100; `sort` là `created_at` hoặc `-created_at`.

```json
{
  "items": [],
  "page": 1,
  "limit": 10,
  "total": 0,
  "total_pages": 0
}
```

### `GET /api/predictions/stats`

```json
{
  "total_predictions": 10,
  "average_prediction": 7.35,
  "min_prediction": 5.1,
  "max_prediction": 12.4,
  "predictions_by_make": [
    { "make": "Toyota", "count": 4 }
  ]
}
```

### `GET /api/health`

```json
{
  "backend": { "status": "up" },
  "mongodb": { "status": "up", "ready_state": 1 },
  "ai_service": { "status": "up" },
  "overall_status": "ok"
}
```

`overall_status` là `down` và HTTP status là 503 nếu MongoDB hoặc AI Service chưa sẵn sàng.

### `GET /api/model-info`

Proxy response từ AI Service, ví dụ:

```json
{
  "model_version": "model-v1",
  "model_name": "regressor"
}
```

### `GET /api/fields`

```json
{
  "fields": ["model_year", "make", "vehicle_class", "engine_size", "cylinders", "transmission", "fuel_type"],
  "limits": {
    "model_year": { "min": 1995, "max": 2023 },
    "engine_size": { "min": 0.8, "max": 8.4 },
    "cylinders": { "min": 2, "max": 16 }
  }
}
```

## Ví dụ curl

```bash
curl -X POST "$NEXT_PUBLIC_API_URL/api/predict" -H "Content-Type: application/json" -H "X-Request-ID: demo-request-1" -d '{"model_year":2020,"make":"Toyota","vehicle_class":"SUV","engine_size":2.0,"cylinders":4,"transmission":"Automatic","fuel_type":"X"}'
curl "$NEXT_PUBLIC_API_URL/api/predictions?page=1&limit=10&sort=-created_at"
curl "$NEXT_PUBLIC_API_URL/api/predictions/stats"
curl "$NEXT_PUBLIC_API_URL/api/predictions/<prediction_id>"
curl "$NEXT_PUBLIC_API_URL/api/health"
curl "$NEXT_PUBLIC_API_URL/api/model-info"
curl "$NEXT_PUBLIC_API_URL/api/fields"
```

Frontend chỉ gọi Backend qua `NEXT_PUBLIC_API_URL`; không gọi trực tiếp AI Service.

## Hợp đồng với AI Service

Backend gửi `POST /predict` tới `AI_SERVICE_URL`, forward đúng 7 field snake_case và header `X-Request-ID`. AI Service cần trả tối thiểu:

```json
{
  "prediction": 7.2,
  "unit": "L/100 km",
  "model_version": "model-v1"
}
```

Backend gọi thêm `GET /health` và `GET /model-info`, cũng forward `X-Request-ID`. Backend không train model, không load `model.joblib` và không cung cấp endpoint train/upload model.

## Mã lỗi

| HTTP | Code | Ý nghĩa |
|---:|---|---|
| 400 | `BAD_REQUEST` | Request hoặc ObjectId không hợp lệ |
| 400 | `INVALID_JSON` | JSON body không parse được |
| 404 | `NOT_FOUND` | Route hoặc prediction không tồn tại |
| 422 | `VALIDATION_ERROR` | Input Backend không hợp lệ |
| 422 | `AI_VALIDATION_ERROR` | AI Service từ chối input |
| 500 | `INTERNAL_ERROR` | Lỗi nội bộ hoặc không lưu được MongoDB |
| 502 | `AI_SERVICE_UNAVAILABLE` | AI timeout hoặc không kết nối được |
| 502 | `AI_SERVICE_ERROR` | AI lỗi 5xx hoặc response sai định dạng |
| 503 | `MODEL_NOT_READY` | AI Service/model chưa sẵn sàng |

Body lỗi luôn có dạng:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dữ liệu dự đoán không hợp lệ",
    "details": [{ "field": "engine_size", "message": "engine_size phải nằm trong khoảng 0.8 – 8.4" }]
  },
  "request_id": "3d8a0f5a-3e77-4c71-9d53-9f5b3266d4cd"
}
```