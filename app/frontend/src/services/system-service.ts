import type { FieldsConfig, HealthResponse, ModelInfo } from '@/types';
import { ApiError, apiRequest } from './api-client';

interface ServiceRequestOptions {
  signal?: AbortSignal;
}

function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== 'object' || value === null) {
    return false;
  }

  const record = value as Record<string, unknown>;
  const backend = record.backend;
  const mongodb = record.mongodb;
  const aiService = record.ai_service;

  return (record.overall_status === 'ok' || record.overall_status === 'down')
    && typeof backend === 'object' && backend !== null
    && typeof (backend as Record<string, unknown>).status === 'string'
    && typeof mongodb === 'object' && mongodb !== null
    && typeof (mongodb as Record<string, unknown>).status === 'string'
    && typeof (mongodb as Record<string, unknown>).ready_state === 'number'
    && typeof aiService === 'object' && aiService !== null
    && typeof (aiService as Record<string, unknown>).status === 'string';
}

export async function getHealth(options: ServiceRequestOptions = {}): Promise<HealthResponse> {
  try {
    return await apiRequest<HealthResponse>('/api/health', { method: 'GET', signal: options.signal });
  } catch (error) {
    if (error instanceof ApiError && error.status === 503 && isHealthResponse(error.responseBody)) {
      return error.responseBody;
    }

    throw error;
  }
}

export function getModelInfo(options: ServiceRequestOptions = {}): Promise<ModelInfo> {
  return apiRequest<ModelInfo>('/api/model-info', { method: 'GET', signal: options.signal });
}

export function getFieldsConfig(options: ServiceRequestOptions = {}): Promise<FieldsConfig> {
  return apiRequest<FieldsConfig>('/api/fields', { method: 'GET', signal: options.signal });
}