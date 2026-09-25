'use client';

import type { ApiError } from '@/services/api-client';
import { getErrorMessage } from '@/services/api-client';
import styles from './ErrorAlert.module.css';

interface ErrorAlertProps { error: ApiError | null; onDismiss: () => void; }

export default function ErrorAlert({ error, onDismiss }: ErrorAlertProps) {
  if (!error) return null;
  return (
    <section className={styles.alert} role="alert">
      <div><strong>{getErrorMessage(error)}</strong>{error.details.length > 0 && <ul>{error.details.map((detail) => <li key={`${detail.field}-${detail.message}`}>{detail.field}: {detail.message}</li>)}</ul>}<small>Mã lỗi: {error.code}</small></div>
      <button type="button" onClick={onDismiss} aria-label="Đóng thông báo lỗi">Đóng</button>
    </section>
  );
}