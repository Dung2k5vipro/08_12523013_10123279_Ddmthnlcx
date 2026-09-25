'use client';

import { useEffect, useState } from 'react';
import type { PaginatedPredictions } from '@/types';
import { DEFAULT_PAGE_SIZE } from '@/utils/constants';
import { formatConsumption, formatDateTime } from '@/utils/format';
import { ApiError, getErrorMessage } from '@/services/api-client';
import { getPredictions } from '@/services/prediction-service';
import Spinner from './Spinner';
import styles from './HistoryTable.module.css';

interface HistoryTableProps { refreshKey?: number; }

export default function HistoryTable({ refreshKey = 0 }: HistoryTableProps) {
  const [data, setData] = useState<PaginatedPredictions | null>(null);
  const [page, setPage] = useState(1);
  const [reloadKey, setReloadKey] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getPredictions({ page, limit: DEFAULT_PAGE_SIZE, sort: '-created_at' })
      .then((result) => { if (!cancelled) setData(result); })
      .catch((reason: unknown) => { if (!cancelled) setError(reason instanceof ApiError ? reason : new ApiError('Không thể tải lịch sử.', 0, 'NETWORK_ERROR')); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [page, refreshKey, reloadKey]);

  const totalPages = data?.total_pages ?? 0;
  return (
    <section className={styles.section} aria-labelledby="history-title">
      <div className={styles.heading}><div><p className={styles.eyebrow}>Theo dõi</p><h2 id="history-title">Lịch sử dự đoán</h2></div><button type="button" className={styles.refresh} onClick={() => setReloadKey((current) => current + 1)} disabled={loading}>{loading ? <Spinner label="Đang tải lịch sử" /> : 'Làm mới'}</button></div>
      {loading && <div className={styles.skeleton} aria-label="Đang tải lịch sử" aria-busy="true"><span /><span /><span /></div>}
      {!loading && error && <div className={styles.state}><strong>{getErrorMessage(error)}</strong><button type="button" onClick={() => setReloadKey((current) => current + 1)}>Thử lại</button></div>}
      {!loading && !error && data?.items.length === 0 && <p className={styles.state}>Chưa có bản ghi dự đoán nào.</p>}
      {!loading && !error && data && data.items.length > 0 && (
        <>
          <div className={styles.tableWrap}>
            <table><caption className={styles.srOnly}>Các kết quả dự đoán gần đây</caption><thead><tr><th>Thời gian</th><th>Hãng</th><th>Dòng xe</th><th>Năm</th><th>Động cơ</th><th>Hộp số</th><th>Nhiên liệu</th><th>Kết quả</th></tr></thead>
              <tbody>{data.items.map((item) => <tr key={item.id}><td data-label="Thời gian">{formatDateTime(item.created_at)}</td><td data-label="Hãng">{item.make}</td><td data-label="Dòng xe">{item.vehicle_class}</td><td data-label="Năm">{item.model_year}</td><td data-label="Động cơ">{item.engine_size}L / {item.cylinders}</td><td data-label="Hộp số">{item.transmission}</td><td data-label="Nhiên liệu">{item.fuel_type}</td><td data-label="Kết quả"><strong>{formatConsumption(item.prediction, item.unit)}</strong></td></tr>)}</tbody>
            </table>
          </div>
          <div className={styles.pagination}><button type="button" onClick={() => setPage((current) => current - 1)} disabled={page <= 1}>Trước</button><span>Trang {page} / {totalPages}</span><button type="button" onClick={() => setPage((current) => current + 1)} disabled={page >= totalPages}>Sau</button></div>
        </>
      )}
    </section>
  );
}