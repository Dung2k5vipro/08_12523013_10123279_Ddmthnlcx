'use client';

import { FormEvent, useEffect, useState } from 'react';
import type { ApiErrorDetail, FieldsConfig, PredictionRequest } from '@/types';
import {
  FUEL_TYPE_SUGGESTIONS,
  MAKE_SUGGESTIONS,
  TRANSMISSION_SUGGESTIONS,
  VEHICLE_CLASS_SUGGESTIONS,
} from '@/utils/constants';
import Spinner from './Spinner';
import styles from './PredictionForm.module.css';

type FormKey = keyof PredictionRequest;
type FormValues = Record<FormKey, string>;
type FormErrors = Partial<Record<FormKey, string>>;

interface PredictionFormProps {
  fieldsConfig: FieldsConfig | null;
  loading?: boolean;
  serverErrors?: ApiErrorDetail[];
  onSubmit: (payload: PredictionRequest) => void | Promise<void>;
  onReset?: () => void;
}

const EMPTY_VALUES: FormValues = {
  model_year: '',
  make: '',
  vehicle_class: '',
  engine_size: '',
  cylinders: '',
  transmission: '',
  fuel_type: '',
};

const FIELD_LABELS: Record<FormKey, string> = {
  model_year: 'Năm sản xuất',
  make: 'Hãng xe',
  vehicle_class: 'Dòng xe',
  engine_size: 'Dung tích động cơ (L)',
  cylinders: 'Số xi-lanh',
  transmission: 'Hộp số',
  fuel_type: 'Loại nhiên liệu',
};

const DATALISTS = {
  make: 'make-suggestions',
  vehicle_class: 'vehicle-class-suggestions',
  transmission: 'transmission-suggestions',
  fuel_type: 'fuel-type-suggestions',
} as const;

function getInitialExample(fieldsConfig: FieldsConfig | null): FormValues {
  return {
    model_year: fieldsConfig ? String(fieldsConfig.limits.model_year.min) : '',
    make: 'Toyota',
    vehicle_class: 'SUV',
    engine_size: fieldsConfig ? String(fieldsConfig.limits.engine_size.min) : '',
    cylinders: fieldsConfig ? String(fieldsConfig.limits.cylinders.min) : '',
    transmission: 'AS6',
    fuel_type: 'X',
  };
}

export default function PredictionForm({
  fieldsConfig,
  loading = false,
  serverErrors = [],
  onSubmit,
  onReset,
}: PredictionFormProps) {
  const [values, setValues] = useState<FormValues>(EMPTY_VALUES);
  const [errors, setErrors] = useState<FormErrors>({});

  useEffect(() => {
    const nextErrors: FormErrors = {};
    serverErrors.forEach((detail) => {
      if (detail.field in EMPTY_VALUES) {
        nextErrors[detail.field as FormKey] = detail.message;
      }
    });
    setErrors(nextErrors);
  }, [serverErrors]);

  const updateValue = (field: FormKey, value: string) => {
    setValues((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
  };

  const validate = (): FormErrors => {
    const nextErrors: FormErrors = {};
    const numericFields: FormKey[] = ['model_year', 'engine_size', 'cylinders'];

    (Object.keys(values) as FormKey[]).forEach((field) => {
      if (!values[field].trim()) {
        nextErrors[field] = 'Trường này không được để trống.';
      }
    });

    numericFields.forEach((field) => {
      const numericValue = Number(values[field]);
      if (values[field].trim() && !Number.isFinite(numericValue)) {
        nextErrors[field] = 'Vui lòng nhập một số hợp lệ.';
      }
    });

    if (fieldsConfig) {
      const numericLimits: Record<'model_year' | 'engine_size' | 'cylinders', { min: number; max: number }> = fieldsConfig.limits;
      (Object.keys(numericLimits) as Array<'model_year' | 'engine_size' | 'cylinders'>).forEach((field) => {
        const value = Number(values[field]);
        const limits = numericLimits[field];
        if (values[field].trim() && Number.isFinite(value) && (value < limits.min || value > limits.max)) {
          nextErrors[field] = `Giá trị phải từ ${limits.min} đến ${limits.max}.`;
        }
      });
    }

    return nextErrors;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    await onSubmit({
      model_year: Number(values.model_year),
      make: values.make.trim(),
      vehicle_class: values.vehicle_class.trim(),
      engine_size: Number(values.engine_size),
      cylinders: Number(values.cylinders),
      transmission: values.transmission.trim(),
      fuel_type: values.fuel_type.trim(),
    });
  };

  const handleReset = () => {
    setValues(EMPTY_VALUES);
    setErrors({});
    onReset?.();
  };

  const fillExample = () => {
    setValues(getInitialExample(fieldsConfig));
    setErrors({});
  };

  const renderDatalist = (field: keyof typeof DATALISTS) => {
    const suggestions = field === 'make'
      ? MAKE_SUGGESTIONS.map((value) => ({ value, label: value }))
      : field === 'vehicle_class'
        ? VEHICLE_CLASS_SUGGESTIONS
        : field === 'transmission'
          ? TRANSMISSION_SUGGESTIONS
          : FUEL_TYPE_SUGGESTIONS;

    return (
      <datalist id={DATALISTS[field]}>
        {suggestions.map((suggestion) => <option key={suggestion.value} value={suggestion.value} label={suggestion.label} />)}
      </datalist>
    );
  };

  const renderField = (field: FormKey, type: 'text' | 'number', placeholder: string, step?: string) => {
    const errorId = `${field}-error`;
    const datalist = field in DATALISTS ? renderDatalist(field as keyof typeof DATALISTS) : null;
    return (
      <div className={styles.field} key={field}>
        <label htmlFor={field}>{FIELD_LABELS[field]}</label>
        <input
          id={field}
          name={field}
          type={type}
          value={values[field]}
          onChange={(event) => updateValue(field, event.target.value)}
          placeholder={placeholder}
          step={step}
          list={field in DATALISTS ? DATALISTS[field as keyof typeof DATALISTS] : undefined}
          aria-invalid={Boolean(errors[field])}
          aria-describedby={errors[field] ? errorId : undefined}
          disabled={loading}
        />
        {datalist}
        {errors[field] && <p className={styles.error} id={errorId}>{errors[field]}</p>}
      </div>
    );
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <div className={styles.grid}>
        {renderField('model_year', 'number', 'Ví dụ: 2020')}
        {renderField('make', 'text', 'Ví dụ: Toyota')}
        {renderField('vehicle_class', 'text', 'Ví dụ: SUV')}
        {renderField('engine_size', 'number', 'Ví dụ: 2.0', '0.1')}
        {renderField('cylinders', 'number', 'Ví dụ: 4', '1')}
        {renderField('transmission', 'text', 'Ví dụ: AS6')}
        <div className={styles.field}>
          <label htmlFor="fuel_type">Loại nhiên liệu <span className={styles.hint}>(X: xăng thường, Z: cao cấp)</span></label>
          <input
            id="fuel_type"
            name="fuel_type"
            type="text"
            value={values.fuel_type}
            onChange={(event) => updateValue('fuel_type', event.target.value)}
            placeholder="Ví dụ: X"
            list={DATALISTS.fuel_type}
            aria-invalid={Boolean(errors.fuel_type)}
            aria-describedby={errors.fuel_type ? 'fuel_type-error' : undefined}
            disabled={loading}
          />
          {renderDatalist('fuel_type')}
          {errors.fuel_type && <p className={styles.error} id="fuel_type-error">{errors.fuel_type}</p>}
        </div>
      </div>
      <div className={styles.actions}>
        <button className={styles.primaryButton} type="submit" disabled={loading || !fieldsConfig}>
          {loading && <Spinner label="Đang dự đoán" />}
          {loading ? 'Đang dự đoán...' : 'Dự đoán'}
        </button>
        <button className={styles.secondaryButton} type="button" onClick={handleReset} disabled={loading}>Nhập lại</button>
        <button className={styles.ghostButton} type="button" onClick={fillExample} disabled={loading}>Điền ví dụ mẫu</button>
      </div>
      {!fieldsConfig && <p className={styles.configNotice}>Đang tải giới hạn dữ liệu từ backend...</p>}
    </form>
  );
}