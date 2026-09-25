import { env } from '@/utils/env';
import { generateRequestId } from '@/utils/request-id';
import type { ApiErrorBody, ApiErrorDetail } from '@/types';

interface ApiRequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  signal?: AbortSignal;
  requestId?: string;
}

type JsonRecord = Record<string, unknown>;

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null;
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (!isRecord(value) || !isRecord(value.error)) {
    return false;
  }

  return typeof value.error.code === 'string' && typeof value.error.message === 'string';
}

function getErrorDetails(value: unknown): ApiErrorDetail[] {
  if (!isApiErrorBody(value) || !Array.isArray(value.error.details)) {
    return [];
  }

  return value.error.details.filter((detail): detail is ApiErrorDetail => (
    isRecord(detail) && typeof detail.field === 'string' && typeof detail.message === 'string'
  ));
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: ApiErrorDetail[];
  readonly requestId?: string;
  readonly responseBody?: unknown;

  constructor(
    message: string,
    status: number,
    code: string,
    details: ApiErrorDetail[] = [],
    requestId?: string,
    responseBody?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
    this.requestId = requestId;
    this.responseBody = responseBody;
  }
}

async function parseJson(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return undefined;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return undefined;
  }
}

export async function apiRequest<T>(
  path: string,
  { method, body, signal, requestId = generateRequestId() }: ApiRequestOptions,
): Promise<T> {
  const controller = new AbortController();
  let timedOut = false;
  const timeoutId = globalThis.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, env.NEXT_PUBLIC_REQUEST_TIMEOUT_MS);

  const abortRequest = () => controller.abort();
  if (signal?.aborted) {
    controller.abort();
  } else {
    signal?.addEventListener('abort', abortRequest, { once: true });
  }

  try {
    const response = await fetch(`${env.NEXT_PUBLIC_API_URL}${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-Request-ID': requestId,
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    const responseBody = await parseJson(response);

    if (!response.ok) {
      const errorBody = isApiErrorBody(responseBody) ? responseBody : undefined;
      const message = errorBody?.error.message ?? 'Backend trả về lỗi không xác định.';
      const code = errorBody?.error.code ?? `HTTP_${response.status}`;
      const responseRequestId = errorBody?.request_id ?? requestId;

      throw new ApiError(
        message,
        response.status,
        code,
        getErrorDetails(responseBody),
        responseRequestId,
        responseBody,
      );
    }

    return responseBody as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    const message = timedOut
      ? 'Request đã hết thời gian chờ. Vui lòng thử lại.'
      : 'Không thể kết nối máy chủ. Vui lòng kiểm tra kết nối mạng.';

    throw new ApiError(message, 0, timedOut ? 'REQUEST_TIMEOUT' : 'NETWORK_ERROR', [], requestId);
  } finally {
    globalThis.clearTimeout(timeoutId);
    signal?.removeEventListener('abort', abortRequest);
  }
}

export function getErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return 'Đã xảy ra lỗi không xác định. Vui lòng thử lại.';
  }

  switch (error.status) {
    case 422:
      return 'Vui lòng kiểm tra lại dữ liệu nhập vào.';
    case 502:
      return 'Dịch vụ AI đang gặp sự cố. Vui lòng thử lại sau.';
    case 503:
      return 'Hệ thống hoặc model chưa sẵn sàng. Vui lòng thử lại sau.';
    case 500:
      return 'Hệ thống đang gặp lỗi. Vui lòng thử lại sau.';
    case 0:
      return 'Không thể kết nối máy chủ. Vui lòng kiểm tra kết nối mạng.';
    default:
      return error.message;
  }
}