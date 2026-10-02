const DEFAULT_REQUEST_TIMEOUT_MS = 15000;

function getApiUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

  if (!apiUrl) {
    return '';
  }

  return apiUrl.replace(/\/+$/, '');
}

function getRequestTimeoutMs(): number {
  const parsedTimeout = Number(process.env.NEXT_PUBLIC_REQUEST_TIMEOUT_MS);
  return Number.isFinite(parsedTimeout) && parsedTimeout > 0
    ? parsedTimeout
    : DEFAULT_REQUEST_TIMEOUT_MS;
}

export const env = {
  get apiUrl() { return getApiUrl(); },
  get requestTimeoutMs() { return getRequestTimeoutMs(); },
  get NEXT_PUBLIC_API_URL() { return getApiUrl(); },
  get NEXT_PUBLIC_REQUEST_TIMEOUT_MS() { return getRequestTimeoutMs(); },
} as const;