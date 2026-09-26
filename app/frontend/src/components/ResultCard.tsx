'use client';

import { useState } from 'react';
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

function getFuelTypeName(type: string): string {
  const map: Record<string, string> = {
    X: 'Xăng thường (Regular)',
    Z: 'Xăng cao cấp (Premium)',
    E: 'Ethanol E85',
    D: 'Dầu Diesel',
    N: 'Khí tự nhiên (CNG)',
  };
  return map[type.toUpperCase()] || type;
}

export default function ResultCard({ result, request }: ResultCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  const rating = result ? getRating(result.prediction) : null;
  const meterWidth = result
    ? Math.min(100, (result.prediction / (CONSUMPTION_THRESHOLDS.high * 1.5)) * 100)
    : 0;

  return (
    <section className={styles.mainCard} aria-live="polite">
      <p className={styles.eyebrow}>KẾT QUẢ ƯỚC TÍNH</p>

      {result ? (
        <>
          <div className={styles.valueRow}>
            <span className={styles.value}>{formatConsumption(result.prediction, result.unit)}</span>
          </div>

          {rating && (
            <div className={`${styles.ratingBadge} ${rating.className}`}>
              <div className={styles.ratingHeader}>
                <span className={styles.ratingLabel}>{rating.label}</span>
                <small className={styles.ratingSub}>Mức tiêu thụ năng lượng</small>
              </div>
              <div
                className={styles.meterTrack}
                role="meter"
                aria-label={`Mức tiêu hao ${rating.label}`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Math.round(meterWidth)}
              >
                <span className={styles.meterFill} style={{ width: `${meterWidth}%` }} />
              </div>
            </div>
          )}

          <dl className={styles.detailsGrid}>
            <div className={styles.detailItem}>
              <dt>Phiên bản mô hình</dt>
              <dd>{result.model_version}</dd>
            </div>
            <div className={styles.detailItem}>
              <dt>Thời gian thực hiện</dt>
              <dd>{formatDateTime(result.created_at)}</dd>
            </div>
          </dl>
        </>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>🏎️</div>
          <strong>Chưa có kết quả dự đoán</strong>
          <p>Vui lòng điền thông tin xe ở bên trái và bấm <span>Dự đoán</span>.</p>
        </div>
      )}

      {/* Dynamic Up/Down Arrow Toggle Button for Calculation Methodology */}
      <button
        type="button"
        className={styles.toggleButton}
        onClick={() => setShowDetails((prev) => !prev)}
        aria-expanded={showDetails}
        aria-controls="calculation-explanation"
      >
        <span className={styles.toggleText}>
          {showDetails ? 'Thu gọn cách tính' : 'Xem chi tiết cách tính'}
        </span>
        <div className={`${styles.arrowBadge} ${showDetails ? styles.arrowUp : styles.arrowDown}`}>
          <svg
            className={styles.chevronIcon}
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </button>

      {/* Expandable Calculation Breakdown Drawer Inside Main Card */}
      {showDetails && (
        <div id="calculation-explanation" className={styles.detailsDrawer}>
          <div className={styles.drawerHeader}>
            <h3>
              <span className={styles.drawerIcon}>📐</span> Cách thức mô hình tính toán kết quả
            </h3>
            <p>Mô hình Hồi quy (Machine Learning) phân tích thông số xe và tính toán mức tiêu hao nhiên liệu theo công thức trọng số đa biến:</p>
          </div>

          <div className={styles.formulaBox}>
            <code>
              Tiêu hao (L/100km) = Base + f(Động cơ) + f(Xi-lanh) + f(Nhiên liệu) + f(Hộp số & Dòng xe)
            </code>
          </div>

          <div className={styles.factorsList}>
            <div className={styles.factorCard}>
              <div className={styles.factorHeader}>
                <span className={styles.factorDot} />
                <strong>1. Dung tích động cơ (Engine Size)</strong>
                {request && <span className={styles.factorVal}>{request.engine_size} L</span>}
              </div>
              <p>Tỷ lệ thuận cao nhất với mức tiêu hao. Dung tích càng lớn đòi hỏi lượng hỗn hợp khí - nhiên liệu nạp vào buồng đốt càng nhiều.</p>
            </div>

            <div className={styles.factorCard}>
              <div className={styles.factorHeader}>
                <span className={styles.factorDot} />
                <strong>2. Số lượng Xi-lanh (Cylinders)</strong>
                {request && <span className={styles.factorVal}>{request.cylinders} xi-lanh</span>}
              </div>
              <p>Số buồng đốt hoạt động đồng thời làm tăng ma sát nội cơ khí và lượng nhiên liệu trung bình tiêu thụ.</p>
            </div>

            <div className={styles.factorCard}>
              <div className={styles.factorHeader}>
                <span className={styles.factorDot} />
                <strong>3. Loại nhiên liệu (Fuel Type)</strong>
                {request && <span className={styles.factorVal}>{getFuelTypeName(request.fuel_type)}</span>}
              </div>
              <p>
                Nhiên liệu Ethanol (E85) chứa mật độ năng lượng thấp hơn xăng thường (X/Z), dẫn đến tiêu hao nhiều thể tích hơn (~25-30%).
              </p>
            </div>

            <div className={styles.factorCard}>
              <div className={styles.factorHeader}>
                <span className={styles.factorDot} />
                <strong>4. Kiểu dòng xe & Hộp số</strong>
                {request && <span className={styles.factorVal}>{request.vehicle_class} / {request.transmission}</span>}
              </div>
              <p>Trọng lượng xe và hệ số cản khí động học. Hộp số quy định tỷ số truyền và vòng tua máy tối ưu.</p>
            </div>
          </div>

          {result && request && (
            <div className={styles.summaryBox}>
              <div className={styles.summaryTitle}>Tóm tắt kết quả tính cho xe của bạn:</div>
              <div className={styles.summaryDetails}>
                Xe <strong>{request.make} {request.vehicle_class}</strong> ({request.model_year}) trang bị động cơ <strong>{request.engine_size}L</strong>, <strong>{request.cylinders} xi-lanh</strong> dùng <strong>{request.fuel_type}</strong> đạt mức dự báo <strong>{result.prediction.toFixed(2)} L/100 km</strong>.
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}