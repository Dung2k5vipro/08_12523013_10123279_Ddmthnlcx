export const DEFAULT_PAGE_SIZE = 10;

export const CONSUMPTION_THRESHOLDS = {
  efficient: 6,
  high: 10,
} as const;

export interface Suggestion {
  value: string;
  label: string;
}

export const VEHICLE_CLASS_SUGGESTIONS: Suggestion[] = [
  { value: 'SUV', label: 'Xe thể thao đa dụng' },
  { value: 'SUV - SMALL', label: 'SUV nhỏ' },
  { value: 'SUV - STANDARD', label: 'SUV tiêu chuẩn' },
  { value: 'COMPACT', label: 'Xe nhỏ gọn' },
  { value: 'MID-SIZE', label: 'Xe hạng trung' },
  { value: 'PICKUP TRUCK - SMALL', label: 'Xe bán tải nhỏ' },
  { value: 'PICKUP TRUCK - STANDARD', label: 'Xe bán tải tiêu chuẩn' },
  { value: 'VAN - PASSENGER', label: 'Xe van chở khách' },
  { value: 'MINICOMPACT', label: 'Xe siêu nhỏ' },
  { value: 'SUBCOMPACT', label: 'Xe hạng nhỏ' },
  { value: 'TWO-SEATER', label: 'Xe hai chỗ' },
  { value: 'FULL-SIZE', label: 'Xe cỡ lớn' },
];

export const TRANSMISSION_SUGGESTIONS: Suggestion[] = [
  { value: 'AS6', label: 'Tự động thể thao 6 cấp' },
  { value: 'A6', label: 'Tự động 6 cấp' },
  { value: 'A8', label: 'Tự động 8 cấp' },
  { value: 'M6', label: 'Số sàn 6 cấp' },
  { value: 'M5', label: 'Số sàn 5 cấp' },
  { value: 'AM6', label: 'Tự động chuyển sàn 6 cấp' },
  { value: 'AV', label: 'Vô cấp' },
];

export const FUEL_TYPE_SUGGESTIONS: Suggestion[] = [
  { value: 'X', label: 'Xăng thường' },
  { value: 'Z', label: 'Xăng cao cấp' },
  { value: 'D', label: 'Diesel' },
  { value: 'E', label: 'Ethanol E85' },
  { value: 'N', label: 'Khí tự nhiên' },
];

export const MAKE_SUGGESTIONS = [
  'Toyota',
  'Honda',
  'Ford',
  'Chevrolet',
  'Nissan',
  'Hyundai',
  'Kia',
  'Mazda',
  'BMW',
  'Mercedes-Benz',
];