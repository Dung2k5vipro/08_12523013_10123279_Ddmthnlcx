'use client';

import { useEffect, useState } from 'react';
import type { HealthResponse, ModelInfo } from '@/types';
import { getHealth, getModelInfo } from '@/services/system-service';
import { ApiError, getErrorMessage } from '@/services/api-client';
import Spinner from './Spinner';
import styles from './SystemStatus.module.css';

const REFRESH_INTERVAL_MS = 30000;

function statusText(status: string): string {
  if (status === 'up' || status === 'ok') return 'Hoạt động';
  if (status === 'down') return 'Gián đoạn';
  return 'Đang kiểm tra';
}

function statusClass(status: string): string {
  if (status === 'up' || status === 'ok') return styles.up;
  if (status === 'down') return styles.down;
  return styles.unknown;
}

export default function SystemStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const loadStatus = async () => {
      const [healthResult, modelResult] = await Promise.allSettled([getHealth(), getModelInfo()]);
      if (cancelled) return;
      if (healthResult.status === 'fulfilled') setHealth(healthResult.value);
      else setError(healthResult.reason instanceof ApiError ? healthResult.reason : new ApiError('Không thể tải trạng thái hệ thống.', 0, 'NETWORK_ERROR'));
      if (modelResult.status === 'fulfilled') setModel(modelResult.value);
      setLoading(false);
    };
    void loadStatus();
    const intervalId = window.setInterval(() => { void loadStatus(); }, REFRESH_INTERVAL_MS);
    return () => { cancelled = true; window.clearInterval(intervalId); };
  }, []);

  const components = health ? [['Backend', health.backend.status], ['MongoDB', health.mongodb.status], ['AI Service', health.ai_service.status]] : [];
  const metrics = model ? Object.entries(model).filter(([key, value]) => ['rmse', 'r2', 'mae', 'mse'].includes(key) && typeof value === 'number') : [];
  return <section className={styles.section} aria-labelledby="system-title"><div className={styles.heading}><div><p className={styles.eyebrow}>Giám sát</p><h2 id="system-title">Trạng thái hệ thống</h2></div>{loading && <Spinner label="Đang kiểm tra hệ thống" />}</div>{error && !health && <p className={styles.error}>{getErrorMessage(error)}</p>}{health && <div className={styles.badges}>{components.map(([label, status]) => <div className={`${styles.badge} ${statusClass(status)}`} key={label}><span className={styles.dot} aria-hidden="true" /><span><strong>{label}</strong><small>{statusText(status)}</small></span></div>)}</div>}{model && <div className={styles.model}><span>Model: <strong>{model.model_version}</strong> ({model.model_name})</span>{metrics.map(([key, value]) => <span key={key}>{key.toUpperCase()}: <strong>{String(value)}</strong></span>)}</div>}{!loading && !health && !error && <p className={styles.empty}>Chưa có thông tin trạng thái.</p>}</section>;
}