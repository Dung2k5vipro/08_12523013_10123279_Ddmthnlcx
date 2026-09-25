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
  { value: 'Compact', label: 'Xe nhỏ gọn' },
  { value: 'Mid-size', label: 'Xe hạng trung' },
  { value: 'Pickup truck', label: 'Xe bán tải' },
  { value: 'Van', label: 'Xe van' },
  { value: 'Minicompact', label: 'Xe siêu nhỏ' },
  { value: 'Subcompact', label: 'Xe hạng nhỏ' },
  { value: 'Two-seater', label: 'Xe hai chỗ' },
  { value: 'Full-size', label: 'Xe cỡ lớn' },
];

export const TRANSMISSION_SUGGESTIONS: Suggestion[] = [
  { value: 'Automatic', label: 'Số tự động' },
  { value: 'Manual', label: 'Số sàn' },
  { value: 'AM', label: 'Tự động chuyển sàn' },
  { value: 'AS', label: 'Tự động thể thao' },
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