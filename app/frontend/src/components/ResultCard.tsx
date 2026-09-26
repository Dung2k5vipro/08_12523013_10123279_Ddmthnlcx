'use client';

import type { PredictionRequest, PredictionResponse } from '@/types';
import { CONSUMPTION_THRESHOLDS } from '@/utils/constants';
import { formatConsumption, formatDateTime } from '@/utils/format';
import styles from './ResultCard.module.css';

interface ResultCardProps {
  result: PredictionResponse | null;
  request?: PredictionRequest | null;
}

function getRating(value: number): { label: string; className: string } {
  if (value <= CONSUMPTION_THRESHOLDS.efficient) return { label: 'Tiết kiệm', className: styles.efficient };
  if (value >= CONSUMPTION_THRESHOLDS.high) return { label: 'Cao', className: styles.high };
  return { label: 'Trung bình', className: styles.average };
}

export default function ResultCard({ result, request }: ResultCardProps) {
  if (!result) {
    return <section className={styles.empty} aria-live="polite"><strong>Chưa có kết quả</strong><span>Nhập thông tin xe và bấm Dự đoán.</span></section>;
  }

  const rating = getRating(result.prediction);
  const vehicleName = request ? `${request.make} ${request.vehicle_class}` : 'Xe của bạn';
  const meterWidth = Math.min(100, (result.prediction / (CONSUMPTION_THRESHOLDS.high * 1.5)) * 100);

  return (
    <section className={styles.card} aria-live="polite">
      <p className={styles.eyebrow}>Kết quả ước tính</p>
      <p className={styles.value}>{formatConsumption(result.prediction, result.unit)}</p>
      <div className={`${styles.rating} ${rating.className}`}><span>{rating.label}</span><div className={styles.meter} role="meter" aria-label={`Mức tiêu hao ${rating.label}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(meterWidth)}><span style={{ width: `${meterWidth}%` }} /></div><small>Ngưỡng tham khảo, không thay thế đánh giá thực tế.</small></div>
      <dl className={styles.details}>
        <div><dt>Xe</dt><dd>{vehicleName}</dd></div>
        <div><dt>Phiên bản model</dt><dd>{result.model_version}</dd></div>
        <div><dt>Thời gian</dt><dd>{formatDateTime(result.created_at)}</dd></div>
      </dl>
    </section>
  );
}