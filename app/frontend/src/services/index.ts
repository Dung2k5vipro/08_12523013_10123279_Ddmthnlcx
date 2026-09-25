export { ApiError, apiRequest, getErrorMessage } from './api-client';
export {
  getPredictionStats,
  getPredictions,
  predictFuelConsumption,
} from './prediction-service';
export {
  getFieldsConfig,
  getHealth,
  getModelInfo,
} from './system-service';
export type { GetPredictionsOptions } from './prediction-service';