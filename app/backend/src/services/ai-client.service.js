const axios = require('axios');

const config = require('../config/env');
const { FEATURE_FIELDS, REQUEST_ID_HEADER } = require('../config/constants');
const AppError = require('../utils/app-error');
const logger = require('../utils/logger');

const axiosInstance = axios.create({
	baseURL: config.AI_SERVICE_URL,
	timeout: config.AI_SERVICE_TIMEOUT_MS
});

function createServiceError(message, statusCode, code, requestId, details = []) {
	logger.error(message, { request_id: requestId, code, status_code: statusCode });
	return new AppError(message, statusCode, code, details);
}

function mapAxiosError(error, requestId) {
	if (error.response) {
		const { status, data } = error.response;

		if (status === 503) {
			return createServiceError('AI Service chưa sẵn sàng', 503, 'MODEL_NOT_READY', requestId);
		}

		if (status >= 400 && status < 500) {
			return createServiceError(
				'AI Service từ chối yêu cầu',
				422,
				'AI_VALIDATION_ERROR',
				requestId,
				data?.error?.details || data?.details || []
			);
		}

		if (status >= 500) {
			return createServiceError('AI Service gặp lỗi', 502, 'AI_SERVICE_ERROR', requestId);
		}
	}

	if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND' ||
		error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
		return createServiceError('Không thể kết nối AI Service', 502, 'AI_SERVICE_UNAVAILABLE', requestId);
	}

	return createServiceError('Lỗi giao tiếp với AI Service', 502, 'AI_SERVICE_ERROR', requestId);
}

async function request(method, path, requestId, data) {
	try {
		const response = await axiosInstance.request({
			method,
			url: path,
			data,
			headers: { [REQUEST_ID_HEADER]: requestId }
		});

		return response.data;
	} catch (error) {
		throw mapAxiosError(error, requestId);
	}
}

async function predict(features, requestId) {
	const payload = FEATURE_FIELDS.reduce((result, field) => {
		result[field] = features[field];
		return result;
	}, {});
	const data = await request('post', '/predict', requestId, payload);

	if (!Number.isFinite(data?.prediction) || !data?.model_version) {
		throw createServiceError('AI Service trả về dữ liệu dự đoán không hợp lệ', 502, 'AI_SERVICE_ERROR', requestId);
	}

	return {
		prediction: data.prediction,
		unit: data.unit,
		model_version: data.model_version
	};
}

async function getHealth(requestId) {
	return request('get', '/health', requestId);
}

async function getModelInfo(requestId) {
	return request('get', '/model-info', requestId);
}

module.exports = { predict, getHealth, getModelInfo };