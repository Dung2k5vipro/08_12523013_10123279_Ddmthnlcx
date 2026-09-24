# QUY TẮC CHUNG CỦA DỰ ÁN

> BẮT BUỘC đọc trước khi tạo hoặc sửa code.

# LUỒNG CHẠY NHANH

## Train model

scripts\train.bat

hoặc:

python ai-models\src\train.py

Kết quả:

ai-models/models/model.joblib

## Chạy local

Terminal 1:

scripts\run-ai.bat

Terminal 2:

scripts\run-backend.bat

Terminal 3:

scripts\run-frontend.bat

## Chạy Docker

scripts\docker-up.bat

## Xem log

scripts\docker-logs.bat

## Dừng Docker

scripts\docker-down.bat

Ghi chú:

Train model không phải bước bắt buộc mỗi lần chạy App.

Nếu model.joblib đã tồn tại và đúng version thì chỉ cần chạy các service.

## 1. Thông tin bài toán

Tên:
Dự đoán mức tiêu hao nhiên liệu của xe

Loại:
Regression

Target:
fuel_consumption_comb

Đơn vị:
L/100 km

4 model:
- Linear Regression
- Decision Tree Regressor
- KNN Regressor
- SVR

## 2. Field chuẩn dùng toàn hệ thống

JSON API luôn dùng snake_case.

Danh sách chuẩn:
- model_year
- make
- vehicle_class
- engine_size
- cylinders
- transmission
- fuel_type

Target:
fuel_consumption_comb

Response:
- prediction
- unit
- model_version
- request_id
- created_at

Không tự ý đổi tên.

## 3. Quy tắc Python

variable: snake_case
function: snake_case
file: snake_case.py
class: PascalCase
constant: UPPER_SNAKE_CASE

## 4. Quy tắc JavaScript/TypeScript

biến nội bộ: camelCase
function: camelCase
React Component: PascalCase
constant: UPPER_SNAKE_CASE

Nhưng API payload vẫn dùng snake_case.

## 5. Quy tắc luồng chạy chung

LUỒNG TRAINING

Dataset Kaggle
      ↓
01_eda.ipynb
      ↓
02_preprocess.ipynb
      ↓
03_train.ipynb / train.py
      ↓
Train 4 model
      ↓
04_evaluate.ipynb
      ↓
Chọn model cuối
      ↓
model.joblib
      ↓
metadata.json

Training do developer chủ động chạy.
Không chạy khi user request.

---

LUỒNG DỰ ĐOÁN

User
  ↓
Frontend
  ↓
POST /api/predict
  ↓
Backend
  ↓
Validate
  ↓
AI Service /predict
  ↓
model.joblib
  ↓
model.predict()
  ↓
AI Response
  ↓
Backend
  ↓
MongoDB
  ↓
Frontend
  ↓
Hiển thị L/100 km

## 6. Luồng khởi động local

Thứ tự:
1. MongoDB
2. AI Service
3. Backend
4. Frontend

AI Service phải sẵn sàng trước khi Backend dự đoán.

## 7. Luồng Docker

docker compose up --build
        ↓
mongodb
ai-service
backend
frontend

Backend gọi:
http://ai-service:8001

Backend KHÔNG gọi:
localhost:8001

## 8. Quy tắc AI model

Production model:
ai-models/models/model.joblib

Schema:
ai-models/models/schema.json

Metadata:
ai-models/models/metadata.json

Candidate models:
ai-models/models/candidates/

Model cũ:
ai-models/models/versions/

AI Service load model khi khởi động.
Không load lại model mỗi request.

## 9. Quy tắc API

Frontend chỉ gọi Backend.
Frontend KHÔNG gọi trực tiếp AI Service.

Backend chịu trách nhiệm:
- validate
- request_id
- gọi AI
- error handling
- lưu MongoDB

AI Service chịu trách nhiệm:
- load model
- preprocessing
- predict
- health
- model info

## 10. Request ID

Header:
X-Request-ID

Một request phải dùng cùng request_id qua:
Frontend
Backend
AI Service
Backend

## 11. HTTP status

200: success
400: invalid input
404: not found
422: validation error
500: internal error
502: AI Service unavailable/error
503: service/model not ready

## 12. Environment

Không hardcode URL, port, secret.

Local:
AI_SERVICE_URL=http://localhost:8001

Docker:
AI_SERVICE_URL=http://ai-service:8001

Frontend gọi Backend qua:
NEXT_PUBLIC_API_URL

Mọi URL, port, database URI, đường dẫn model, schema, metadata, timeout phải đọc từ biến môi trường.
Ví dụ SAI: http://localhost:8001 (viết trực tiếp)
Ví dụ ĐÚNG: process.env.AI_SERVICE_URL (Backend), os.getenv("MODEL_PATH") (Python)

## 13. Quy tắc Git

Không làm tất cả trên main.
Tạo branch theo chức năng.

Ví dụ:
feature/ai-phase-1
feature/ai-training
feature/ai-service
feature/backend
feature/frontend
feature/mongodb
feature/docker

Trước khi tạo branch:
git checkout main
git pull origin main

Sau merge:
git checkout main
git pull origin main

Không force push branch dùng chung.

## 14. File dùng chung

Các file dùng chung:
QUY_TAC_CHUNG.md
.env.example
docker-compose.yml
README.md

Không để 2 người cùng sửa một file dùng chung cùng lúc nếu không cần.
Nếu cần sửa:
1. pull main
2. sửa
3. commit
4. merge
5. người kia pull lại

## 15. Nguyên tắc chống conflict

Người làm AI ưu tiên sửa:
ai-models/

Người làm App ưu tiên sửa:
app/

Không sửa phần của người kia nếu chưa thống nhất.

Notebook .ipynb chỉ nên có 1 người chỉnh tại một thời điểm.
Word/PPT cũng chỉ một người tổng hợp tại một thời điểm.
