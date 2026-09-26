import type {
  PaginatedPredictions,
  PredictionRequest,
  PredictionResponse,
  PredictionStats,
} from '@/types';
import { apiRequest } from './api-client';

export interface GetPredictionsOptions {
  page: number;
  limit: number;
  sort: '-created_at' | 'created_at';
}

export interface ServiceRequestOptions {
  signal?: AbortSignal;
}

export function predictFuelConsumption(payload: PredictionRequest, options: ServiceRequestOptions = {}): Promise<PredictionResponse> {
  return apiRequest<PredictionResponse>('/api/predict', {
    method: 'POST',
    body: payload,
    signal: options.signal,
  });
}

export function getPredictions({ page, limit, sort }: GetPredictionsOptions): Promise<PaginatedPredictions> {
  const query = new URLSearchParams({
    page: String(page),
    limit: String(limit),
    sort,
  });

  return apiRequest<PaginatedPredictions>(`/api/predictions?${query.toString()}`, {
    method: 'GET',
  });
}

export function getPredictionStats(options: ServiceRequestOptions = {}): Promise<PredictionStats> {
  return apiRequest<PredictionStats>('/api/predictions/stats', {
    method: 'GET',
    signal: options.signal,
  });
}