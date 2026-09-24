# Dataset

## Tên dataset
MY1995-2023 Fuel Consumption Ratings

## Nguồn
Kaggle / Government of Canada (Official Fuel Consumption Ratings 1995-2023)

## File gốc
MY1995-2023-Fuel-Consumption-Ratings.csv.zip

## File dùng để phân tích
raw/MY1995-2023-Fuel-Consumption-Ratings.csv

## Bài toán
Regression

## Target
Fuel Consumption Comb (L/100 km)

## Target chuẩn nội bộ
fuel_consumption_comb

## Đơn vị
L/100 km

## Thống kê tổng quan
- **Tổng số dòng**: 27,001 (gốc) -> 26,998 (sau khi drop 3 bản ghi trùng lặp)
- **Số lượng feature đầu vào**: 7
- **Missing values**: 0% đối với 7 feature chính và target

## Feature được sử dụng (7 canonical features)
1. `model_year` (integer): Năm sản xuất xe (khoảng giá trị: 1995 - 2023).
2. `make` (category): Hãng sản xuất xe (55 hãng sau khi chuẩn hóa chữ hoa).
3. `vehicle_class` (category): Phân loại kích thước/dáng xe (25 loại sau khi chuẩn hóa).
4. `engine_size` (number): Dung tích động cơ tính bằng Lít (khoảng giá trị: 0.8 - 8.4 L).
5. `cylinders` (integer): Số lượng xy-lanh (các giá trị hợp lệ: 2, 3, 4, 5, 6, 8, 10, 12, 16).
6. `transmission` (category): Mã loại hộp số (30 loại hộp số: A4, A5, AS6, M5, M6, AV,...).
7. `fuel_type` (category): Loại nhiên liệu sử dụng (5 loại: X - Regular gasoline, Z - Premium gasoline, D - Diesel, E - Ethanol E85, N - Natural Gas).

## Feature bị loại và lý do (Data Leakage & Redundancy)
- `Model`: Độ mịn quá cao (4,815 tên model riêng lẻ), nguy cơ gây overfitting. Thông tin xe đã được tổng hợp qua Make, Vehicle Class, Engine Size và Transmission.
- `FuelConsCity_L100km`: Data leakage / Proxy target (mức tiêu thụ trong thành phố trực tiếp cấu thành mức tiêu thụ kết hợp).
- `FuelConsHwy_L100km`: Data leakage / Proxy target (mức tiêu thụ trên cao tốc trực tiếp cấu thành mức tiêu thụ kết hợp).
- `Comb_mpg`: Data leakage / Proxy target (chuyển đổi đơn vị trực tiếp từ L/100 km sang MPG).
- `CO2Emission_g_km`: Data leakage / Proxy target (phát thải CO2 được tính toán tuyến tính từ mức tiêu thụ nhiên liệu).
- `CO2Rating`: Data leakage & Tỷ lệ missing cực lớn (missing ~70.3%, chỉ có từ các đời xe gần đây).
- `SmogRating`: Data leakage & Tỷ lệ missing cực lớn (missing ~74.4%, chỉ có từ các đời xe gần đây).

## License
Open Government Licence - Canada