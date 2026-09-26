# Backend API Contract

Frontend chỉ gọi các endpoint Backend qua `NEXT_PUBLIC_API_URL`. Không gọi trực tiếp AI Service.

## Quy ước chung

- Content type: `application/json` cho request body.
- Header tùy chọn: `X-Request-ID`.
- Backend giữ nguyên request ID hoặc tự sinh UUID v4.
- Tên field JSON và field MongoDB dùng snake_case.
- Các response lỗi luôn có `error.code`, `error.message`, `error.details` và `request_id`.

## POST `/api/predict`

Request body bắt buộc đúng 7 field:

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

Rules:

| Field | Type | Constraint |
|---|---|---|
| `model_year` | integer | 1995-2023 |
| `make` | string | trim, 1-50 characters |
| `vehicle_class` | string | trim, 1-60 characters |
| `engine_size` | number | 0.8-8.4 |
| `cylinders` | integer | 2-16 |
| `transmission` | string | trim, 1-20 characters |
| `fuel_type` | string | trim, 1-20 characters |

Numeric strings are converted to numbers. Unknown fields are rejected.

Success `200`:

```json
{
  "prediction": 7.2,
  "unit": "L/100 km",
  "model_version": "model-v1",
  "request_id": "request-123",
  "created_at": "2026-09-25T10:00:00.000Z"
}
```

## GET `/api/predictions`

Query:

| Field | Type | Default/constraint |
|---|---|---|
| `page` | integer | default 1, >= 1 |
| `limit` | integer | default 10, 1-100 |
| `sort` | string | `-created_at` or `created_at` |

Success `200`:

```json
{
  "items": [],
  "page": 1,
  "limit": 10,
  "total": 0,
  "total_pages": 0
}
```

## GET `/api/predictions/stats`

Success `200`:

```json
{
  "total_predictions": 0,
  "average_prediction": null,
  "min_prediction": null,
  "max_prediction": null,
  "predictions_by_make": []
}
```

## GET `/api/predictions/:id`

`id` phải là MongoDB ObjectId.

Success `200` trả một prediction với các field đã lưu, gồm `id`, `request_id`, 7 feature fields, `prediction`, `unit`, `model_version`, `ai_latency_ms` và `created_at`.

## GET `/api/health`

Success `200` khi `overall_status` là `ok`. Khi MongoDB hoặc AI Service down, trả `503` nhưng vẫn trả chi tiết:

```json
{
  "backend": { "status": "up" },
  "mongodb": { "status": "up", "ready_state": 1 },
  "ai_service": { "status": "down" },
  "overall_status": "down"
}
```

## GET `/api/model-info`

Success `200` là response proxy từ AI Service, ví dụ:

```json
{
  "model_version": "model-v1",
  "model_name": "regressor"
}
```

## GET `/api/fields`

Success `200`:

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

## Error contract

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dữ liệu dự đoán không hợp lệ",
    "details": [{ "field": "make", "message": "make không được để trống" }]
  },
  "request_id": "request-123"
}
```

Mã lỗi được sử dụng: `BAD_REQUEST` (400), `INVALID_JSON` (400), `NOT_FOUND` (404), `VALIDATION_ERROR` (422), `AI_VALIDATION_ERROR` (422), `INTERNAL_ERROR` (500), `AI_SERVICE_UNAVAILABLE` (502), `AI_SERVICE_ERROR` (502), `MODEL_NOT_READY` (503).

## AI Service boundary

Backend gửi `POST /predict` với đúng 7 field và `X-Request-ID`; AI Service trả `prediction`, `unit`, `model_version`. Backend cũng gọi `GET /health` và `GET /model-info`. URL AI lấy từ `AI_SERVICE_URL`; không có URL cố định trong source.