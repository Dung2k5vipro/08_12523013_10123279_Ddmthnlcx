# QUY TẮC CHO COPILOT – BACKEND DỰ ĐOÁN TIÊU HAO NHIÊN LIỆU XE

Bài toán: Regression, target fuel_consumption_comb, đơn vị L/100 km.
Stack backend: Node.js (CommonJS), Express, Mongoose (MongoDB), Joi, Axios, Jest + Supertest.

BẮT BUỘC:
1. JSON API luôn dùng snake_case. 7 field input chuẩn (không đổi tên):
   model_year, make, vehicle_class, engine_size, cylinders, transmission, fuel_type.
   Response dự đoán: prediction, unit, model_version, request_id, created_at.
2. JS: biến/hàm camelCase, constant UPPER_SNAKE_CASE, file dùng kebab-case hoặc camelCase nhất quán. Payload API vẫn snake_case.
3. Không hardcode URL, port, database URI, timeout, secret. Tất cả đọc từ process.env
   (PORT, NODE_ENV, MONGODB_URI, AI_SERVICE_URL, AI_SERVICE_TIMEOUT_MS, CORS_ORIGIN, LOG_LEVEL).
4. Frontend chỉ gọi Backend. Backend gọi AI Service qua AI_SERVICE_URL.
   Docker: http://ai-service:8001. Local: http://localhost:8001 (chỉ nằm trong .env, KHÔNG viết trong code).
5. Backend chịu trách nhiệm: validate, tạo/chuyển tiếp request_id, gọi AI Service, xử lý lỗi, lưu MongoDB.
   Backend KHÔNG train model, KHÔNG load model.joblib, KHÔNG có endpoint train.
6. Header X-Request-ID: nhận từ client hoặc tự sinh (uuid v4); trả lại ở response header;
   chuyển tiếp sang AI Service; lưu vào MongoDB; có trong mọi log và mọi response lỗi.
7. HTTP status: 200 thành công, 400 input sai định dạng (vd JSON hỏng), 404 not found,
   422 validation error, 500 lỗi nội bộ, 502 AI Service lỗi/không kết nối được/timeout,
   503 service hoặc model chưa sẵn sàng.
8. Cấu trúc thư mục backend/src: config, controllers, routes, services, models, middlewares,
   validators, utils, app.js. Controller mỏng, logic nằm ở services. Không sửa thư mục ai-models/ và app/frontend.
9. Code hoàn chỉnh, chạy được, có xử lý lỗi và comment tiếng Việt ngắn gọn. Không viết pseudo-code, không để TODO.
10. Định dạng lỗi thống nhất:
    { "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] }, "request_id": "..." }

    # QUY TẮC CHO COPILOT – FRONTEND (app/frontend)

Stack: Next.js 14 (App Router) + React 18 + TypeScript strict. CSS Modules + globals.css (KHÔNG dùng Tailwind hay thư viện UI ngoài).
Chỉ có MỘT trang: src/app/page.tsx. Giao diện tiếng Việt.

BẮT BUỘC:
1. Frontend CHỈ gọi Backend qua process.env.NEXT_PUBLIC_API_URL. Tuyệt đối không gọi AI Service, không hardcode URL/port.
2. Payload gửi/nhận từ API luôn snake_case: model_year, make, vehicle_class, engine_size, cylinders, transmission, fuel_type;
   response: prediction, unit, model_version, request_id, created_at. Biến nội bộ TS dùng camelCase,
   Component PascalCase, constant UPPER_SNAKE_CASE. Không tự ý đổi tên field.
3. Mỗi request gửi header X-Request-ID (crypto.randomUUID()). Hiển thị request_id trong kết quả và trong thông báo lỗi.
4. Xử lý status theo backend: 200 thành công; 400 dữ liệu gửi lên sai định dạng; 422 lỗi validate (map details[].field vào đúng ô input);
   404 không tìm thấy; 500 lỗi hệ thống; 502 AI Service lỗi hoặc không kết nối được; 503 hệ thống/model chưa sẵn sàng; lỗi mạng/timeout.
   Body lỗi backend: { error: { code, message, details }, request_id }.
5. Giới hạn giá trị của form lấy từ GET /api/fields (không hardcode min/max trong component).
6. Đơn vị hiển thị: L/100 km (lấy từ response.unit).
7. Cấu trúc: src/app, src/components, src/services, src/types, src/utils. Component chỉ lo hiển thị; gọi API nằm trong services/.
8. Code hoàn chỉnh, chạy được, không pseudo-code, không TODO. Comment tiếng Việt ngắn gọn.
9. Có đủ trạng thái: loading, empty, error, success. Truy cập được bằng bàn phím (label, aria-live cho kết quả/lỗi), responsive mobile.
10. Không sửa thư mục backend/ và ai-models/.