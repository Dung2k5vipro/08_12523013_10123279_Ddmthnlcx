'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { FieldsConfig, PredictionRequest, PredictionResponse } from '@/types';
import { ApiError } from '@/services/api-client';
import { getFieldsConfig } from '@/services/system-service';
import { predictFuelConsumption } from '@/services/prediction-service';
import ErrorAlert from '@/components/ErrorAlert';
import HistoryTable from '@/components/HistoryTable';
import PredictionForm from '@/components/PredictionForm';
import ResultCard from '@/components/ResultCard';
import StatsCards from '@/components/StatsCards';
import styles from './page.module.css';

export default function HomePage() {
  const [fieldsConfig, setFieldsConfig] = useState<FieldsConfig | null>(null);
  const [fieldsError, setFieldsError] = useState<ApiError | null>(null);
  const [predictionError, setPredictionError] = useState<ApiError | null>(null);
  const [serverErrors, setServerErrors] = useState<NonNullable<ApiError['details']>>([]);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [lastRequest, setLastRequest] = useState<PredictionRequest | null>(null);
  const [fieldsReloadKey, setFieldsReloadKey] = useState(0);
  const [dataRefreshKey, setDataRefreshKey] = useState(0);
  const [predicting, setPredicting] = useState(false);
  const fieldsControllerRef = useRef<AbortController | null>(null);
  const predictionControllerRef = useRef<AbortController | null>(null);
  const resultRef = useRef<HTMLDivElement | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      fieldsControllerRef.current?.abort();
      predictionControllerRef.current?.abort();
    };
  }, []);

  const loadFields = useCallback(async () => {
    fieldsControllerRef.current?.abort();
    const controller = new AbortController();
    fieldsControllerRef.current = controller;
    setFieldsError(null);
    try {
      const config = await getFieldsConfig({ signal: controller.signal });
      if (mountedRef.current) setFieldsConfig(config);
    } catch (error) {
      if (mountedRef.current && !controller.signal.aborted) {
        setFieldsError(error instanceof ApiError ? error : new ApiError('Không thể tải cấu hình trường dữ liệu.', 0, 'NETWORK_ERROR'));
      }
    }
  }, []);

  useEffect(() => {
    void loadFields();
    return () => fieldsControllerRef.current?.abort();
  }, [fieldsReloadKey, loadFields]);

  const handleSubmit = useCallback(async (payload: PredictionRequest) => {
    if (predicting) return;
    predictionControllerRef.current?.abort();
    const controller = new AbortController();
    predictionControllerRef.current = controller;
    setPredicting(true);
    setPredictionError(null);
    setServerErrors([]);
    setLastRequest(payload);
    try {
      const response = await predictFuelConsumption(payload, { signal: controller.signal });
      if (!mountedRef.current) return;
      setResult(response);
      setDataRefreshKey((current) => current + 1);
      window.requestAnimationFrame(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        resultRef.current?.focus({ preventScroll: true });
      });
    } catch (error) {
      if (!mountedRef.current || controller.signal.aborted) return;
      const apiError = error instanceof ApiError ? error : new ApiError('Không thể thực hiện dự đoán.', 0, 'NETWORK_ERROR');
      setPredictionError(apiError);
      setServerErrors(apiError.status === 422 ? apiError.details : []);
    } finally {
      if (mountedRef.current) setPredicting(false);
    }
  }, [predicting]);

  const handleReset = () => {
    setPredictionError(null);
    setServerErrors([]);
    setResult(null);
    setLastRequest(null);
  };

  const retryFields = () => {
    setFieldsError(null);
    setFieldsReloadKey((current) => current + 1);
  };

  return (
    <main className={styles.page}>
      <div className={styles.container}>
        <header className={styles.header}>
          <div className={styles.intro}>
            <p className={styles.kicker}>FUEL CONSUMPTION RATINGS</p>
            <h1>Dự đoán mức tiêu hao nhiên liệu xe</h1>
          </div>
        </header>

        {fieldsError && (
          <div className={styles.globalError}>
            <ErrorAlert error={fieldsError} onDismiss={() => setFieldsError(null)} />
            <button type="button" onClick={retryFields}>Thử lại tải cấu hình</button>
          </div>
        )}

        <section className={styles.mainGrid} aria-label="Khu vực dự đoán">
          <div className={styles.panel}>
            <div className={styles.panelHeading}>
              <div>
                <p className={styles.kicker}>THÔNG TIN ĐẦU VÀO</p>
                <h2>Thông tin xe</h2>
              </div>
            </div>
            <PredictionForm
              fieldsConfig={fieldsConfig}
              loading={predicting || Boolean(fieldsError)}
              serverErrors={serverErrors}
              onSubmit={handleSubmit}
              onReset={handleReset}
            />
          </div>
          <div ref={resultRef} className={styles.resultPanel} tabIndex={-1}>
            <ErrorAlert error={predictionError} onDismiss={() => setPredictionError(null)} />
            <ResultCard result={result} request={lastRequest} />
          </div>
        </section>

        <StatsCards refreshKey={dataRefreshKey} />
        <HistoryTable key={dataRefreshKey} refreshKey={dataRefreshKey} />

        <footer className={styles.footer}>
          © 2026 Fuel Consumption Ratings · Dữ liệu dùng cho mục đích tham khảo.
        </footer>
      </div>
    </main>
  );
}
