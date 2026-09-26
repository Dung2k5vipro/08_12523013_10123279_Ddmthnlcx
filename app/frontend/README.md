# Frontend dự đoán tiêu hao nhiên liệu

Frontend dùng Next.js 14 App Router, React 18 và TypeScript strict. Giao diện tiếng Việt hỗ trợ nhập thông tin xe, gửi dự đoán, xem kết quả, lịch sử, thống kê và trạng thái hệ thống.

## Cấu trúc

```text
src/
  app/          layout, page và CSS toàn cục
  components/   form, kết quả, lỗi, lịch sử, thống kê, trạng thái hệ thống
  services/     API client và các service gọi Backend
  types/        type khớp API snake_case
  utils/        env, request ID, format và gợi ý nhập liệu
```

Frontend chỉ có một trang tại `src/app/page.tsx`. Component không gọi `fetch` trực tiếp; mọi request đi qua `src/services/`.

## Biến môi trường

Sao chép `.env.example` thành `.env.local` khi chạy local:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_REQUEST_TIMEOUT_MS=15000
```

`NEXT_PUBLIC_API_URL` là địa chỉ mà trình duyệt truy cập được. Khi chạy Docker, vẫn dùng địa chỉ host đã publish, ví dụ `http://localhost:8000`; không dùng `http://backend:8000` vì trình duyệt không phân giải được tên service Docker.

Các biến `NEXT_PUBLIC_*` được Next.js nhúng vào bundle lúc build. Khi build Docker phải truyền qua `build.args`, không chỉ đặt ở runtime:

```bash
docker compose build --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 frontend
```

Origin của Backend `CORS_ORIGIN` phải trùng origin frontend, ví dụ `http://localhost:3000`.

## Chạy local

Từ thư mục gốc:

```bat
scripts\run-frontend.bat
```

Hoặc:

```bash
cd app/frontend
npm install
npm run dev
```

Frontend cần Backend đang chạy. Thứ tự local chuẩn là MongoDB, AI Service, Backend, rồi Frontend.

## Chạy Docker

Từ thư mục gốc:

```bash
docker compose up --build
```

Cấu hình trong `.env` cần có tối thiểu `NEXT_PUBLIC_API_URL`, `FRONTEND_PORT`, `BACKEND_PORT` và `CORS_ORIGIN` phù hợp. Compose khởi động theo dependency: MongoDB -> AI Service -> Backend -> Frontend.

## Luồng dữ liệu

```text
Frontend
  -> POST /api/predict
  -> Backend validate và chuyển tiếp
  -> AI Service dự đoán
  -> MongoDB lưu kết quả
  -> Backend trả response
  -> Frontend hiển thị prediction
```

Frontend chỉ gọi các endpoint Backend:

- `POST /api/predict`
- `GET /api/predictions`
- `GET /api/predictions/stats`
- `GET /api/health`
- `GET /api/model-info`
- `GET /api/fields`

Mỗi request có `X-Request-ID`. Lỗi `422` được gắn vào đúng ô nhập; lỗi `502`, `503`, mất kết nối và timeout được hiển thị bằng thông báo tiếng Việt thân thiện.

## Kiểm tra

```bash
npx tsc --noEmit
npm run build
```
