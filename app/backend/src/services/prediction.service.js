const mongoose = require('mongoose');

const Prediction = require('../models/prediction.model');
const { DEFAULT_UNIT } = require('../config/constants');
const AppError = require('../utils/app-error');
const logger = require('../utils/logger');
const aiClient = require('./ai-client.service');

function getPredictionResponse(document) {
	return {
		prediction: document.prediction,
		unit: document.unit,
		model_version: document.model_version,
		request_id: document.request_id,
		created_at: document.created_at
	};
}

async function createPrediction(features, requestId) {
	const startedAt = process.hrtime.bigint();
	const aiResult = await aiClient.predict(features, requestId);
	const aiLatencyMs = Number(process.hrtime.bigint() - startedAt) / 1000000;

	try {
		const document = await Prediction.create({
			...features,
			prediction: aiResult.prediction,
			unit: aiResult.unit || DEFAULT_UNIT,
			model_version: aiResult.model_version,
			request_id: requestId,
			ai_latency_ms: Number(aiLatencyMs.toFixed(2))
		});

		return getPredictionResponse(document);
	} catch (error) {
		if (error.code === 11000) {
			const existingDocument = await Prediction.findOne({ request_id: requestId });
			if (existingDocument) {
				return getPredictionResponse(existingDocument);
			}
		}

		logger.error('Không thể lưu kết quả dự đoán vào MongoDB', {
			request_id: requestId,
			error_name: error.name,
			error_code: error.code
		});
		throw new AppError('Không thể lưu kết quả dự đoán', 500, 'INTERNAL_ERROR');
	}
}

async function listPredictions({ page, limit, sort }) {
	const sortDirection = sort === '-created_at' ? -1 : 1;
	const [items, total] = await Promise.all([
		Prediction.find().sort({ created_at: sortDirection }).skip((page - 1) * limit).limit(limit),
		Prediction.countDocuments()
	]);

	return {
		items: items.map((item) => item.toJSON()),
		page,
		limit,
		total,
		total_pages: Math.ceil(total / limit)
	};
}

async function getPredictionById(id) {
	if (!mongoose.Types.ObjectId.isValid(id)) {
		throw AppError.badRequest('id không hợp lệ');
	}

	const document = await Prediction.findById(id);
	if (!document) {
		throw AppError.notFound('Không tìm thấy dự đoán');
	}

	return document.toJSON();
}

async function getStatistics() {
	const [statistics] = await Prediction.aggregate([
		{
			$facet: {
				summary: [{
					$group: {
						_id: null,
						total_predictions: { $sum: 1 },
						average_prediction: { $avg: '$prediction' },
						min_prediction: { $min: '$prediction' },
						max_prediction: { $max: '$prediction' }
					}
				}],
				by_make: [
					{ $group: { _id: '$make', count: { $sum: 1 } } },
					{ $sort: { count: -1, _id: 1 } },
					{ $limit: 10 },
					{ $project: { _id: 0, make: '$_id', count: 1 } }
				]
			}
		},
		{
			$project: {
				summary: { $ifNull: [{ $arrayElemAt: ['$summary', 0] }, {}] },
				by_make: 1
			}
		}
	]);

	return {
		total_predictions: statistics.summary.total_predictions || 0,
		average_prediction: statistics.summary.average_prediction ?? null,
		min_prediction: statistics.summary.min_prediction ?? null,
		max_prediction: statistics.summary.max_prediction ?? null,
		predictions_by_make: statistics.by_make
	};
}

module.exports = {
	createPrediction,
	listPredictions,
	getPredictionById,
	getStatistics
};