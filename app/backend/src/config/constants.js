const DEFAULT_UNIT = 'L/100 km';
const MIN_MODEL_YEAR = 1995;
const MAX_MODEL_YEAR = 2023;
const MIN_ENGINE_SIZE = 0.8;
const MAX_ENGINE_SIZE = 8.4;
const MIN_CYLINDERS = 2;
const MAX_CYLINDERS = 16;
const DEFAULT_PAGE = 1;
const DEFAULT_LIMIT = 10;
const MIN_PAGE = 1;
const MIN_LIMIT = 1;
const MAX_LIMIT = 100;
const DEFAULT_SORT = '-created_at';
const REQUEST_ID_HEADER = 'X-Request-ID';
const FEATURE_FIELDS = [
  'model_year',
  'make',
  'vehicle_class',
  'engine_size',
  'cylinders',
  'transmission',
  'fuel_type'
];

module.exports = {
  DEFAULT_UNIT,
  MIN_MODEL_YEAR,
  MAX_MODEL_YEAR,
  MIN_ENGINE_SIZE,
  MAX_ENGINE_SIZE,
  MIN_CYLINDERS,
  MAX_CYLINDERS,
  DEFAULT_PAGE,
  DEFAULT_LIMIT,
  MIN_PAGE,
  MIN_LIMIT,
  MAX_LIMIT,
  DEFAULT_SORT,
  REQUEST_ID_HEADER,
  FEATURE_FIELDS
};