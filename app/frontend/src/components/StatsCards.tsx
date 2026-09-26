'use client';

import { useEffect, useState } from 'react';
import type { PredictionStats } from '@/types';
import { getPredictionStats } from '@/services/prediction-service';
import { ApiError, getErrorMessage } from '@/services/api-client';
import { formatConsumption } from '@/utils/format';
import Spinner from './Spinner';
import styles from './StatsCards.module.css';

interface StatsCardsProps { refreshKey?: number; }

export default function StatsCards({ refreshKey = 0 }: StatsCardsProps) {
  const [stats, setStats] = useState<PredictionStats | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPredictionStats().then(setStats).catch((reason: unknown) => setError(reason instanceof ApiError ? reason : new ApiError('Không thể tải thống kê.', 0, 'NETWORK_ERROR'))).finally(() => setLoading(false));
  }, [refreshKey]);

  if (loading) return <div className={styles.loading}><Spinner label="Đang tải thống kê" /> Đang tải thống kê...</div>;
  if (error) return <p className={styles.error}>{getErrorMessage(error)}</p>;
  if (!stats) return <p className={styles.empty}>Chưa có dữ liệu thống kê.</p>;
  const topMake = stats.predictions_by_make[0];
  const values = [
    ['Tổng số dự đoán', String(stats.total_predictions)],
    ['Trung bình', stats.average_prediction === null ? 'Chưa có' : formatConsumption(stats.average_prediction, 'L/100 km')],
    ['Thấp nhất', stats.min_prediction === null ? 'Chưa có' : formatConsumption(stats.min_prediction, 'L/100 km')],
    ['Cao nhất', stats.max_prediction === null ? 'Chưa có' : formatConsumption(stats.max_prediction, 'L/100 km')],
  ];
  return <section aria-labelledby="stats-title"><h2 id="stats-title" className={styles.title}>Tổng quan</h2><div className={styles.grid}>{values.map(([label, value]) => <article className={styles.card} key={label}><span>{label}</span><strong>{value}</strong></article>)}{topMake && <article className={`${styles.card} ${styles.top}`}><span>Hãng xuất hiện nhiều nhất</span><strong>{topMake.make}</strong><small>{topMake.count} dự đoán</small></article>}</div></section>;
}