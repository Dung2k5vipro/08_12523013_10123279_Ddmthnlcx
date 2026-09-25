export interface PredictionRequest {
  model_year: number;
  make: string;
  vehicle_class: string;
  engine_size: number;
  cylinders: number;
  transmission: string;
  fuel_type: string;
}

export interface PredictionResponse {
  prediction: number;
  unit: string;
  model_version: string;
  request_id: string;
  created_at: string;
}

export interface PredictionRecord extends PredictionRequest {
  id: string;
  request_id: string;
  prediction: number;
  unit: string;
  model_version: string;
  ai_latency_ms?: number;
  created_at: string;
}

export interface PaginatedPredictions {
  items: PredictionRecord[];
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

export interface PredictionsByMake {
  make: string;
  count: number;
}

export interface PredictionStats {
  total_predictions: number;
  average_prediction: number | null;
  min_prediction: number | null;
  max_prediction: number | null;
  predictions_by_make: PredictionsByMake[];
}

export interface NumericLimit {
  min: number;
  max: number;
}

export interface FieldsConfig {
  fields: Array<keyof PredictionRequest>;
  limits: {
    model_year: NumericLimit;
    engine_size: NumericLimit;
    cylinders: NumericLimit;
  };
}

export interface HealthComponent {
  status: string;
}

export interface MongoHealthComponent extends HealthComponent {
  ready_state: number;
}

export interface HealthResponse {
  overall_status: 'ok' | 'down';
  backend: HealthComponent;
  mongodb: MongoHealthComponent;
  ai_service: HealthComponent & Record<string, unknown>;
}

export interface ModelInfo {
  model_version: string;
  model_name: string;
  rmse?: number;
  r2?: number;
  [key: string]: string | number | undefined;
}

export interface ApiErrorDetail {
  field: string;
  message: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: ApiErrorDetail[];
  };
  request_id?: string;
}