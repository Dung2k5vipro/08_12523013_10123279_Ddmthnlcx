import styles from './Spinner.module.css';

interface SpinnerProps {
  label?: string;
}

export default function Spinner({ label = 'Đang xử lý' }: SpinnerProps) {
  return <span className={styles.spinner} aria-label={label} role="status" />;
}