const asyncHandler = require('../utils/async-handler');
const { FEATURE_FIELDS, MIN_MODEL_YEAR, MAX_MODEL_YEAR, MIN_ENGINE_SIZE, MAX_ENGINE_SIZE, MIN_CYLINDERS, MAX_CYLINDERS } = require('../config/constants');
const aiClient = require('../services/ai-client.service');
const healthService = require('../services/health.service');

const health = asyncHandler(async (req, res) => {
	const result = await healthService.getSystemHealth(req.requestId);
	const isReady = result.overall_status === 'ok';

	res.status(isReady ? 200 : 503).json(result);
});

const modelInfo = asyncHandler(async (req, res) => {
	const result = await aiClient.getModelInfo(req.requestId);
	res.status(200).json(result);
});

const fields = (req, res) => {
	res.status(200).json({
		fields: FEATURE_FIELDS,
		limits: {
			model_year: { min: MIN_MODEL_YEAR, max: MAX_MODEL_YEAR },
			engine_size: { min: MIN_ENGINE_SIZE, max: MAX_ENGINE_SIZE },
			cylinders: { min: MIN_CYLINDERS, max: MAX_CYLINDERS }
		}
	});
};

module.exports = { health, modelInfo, fields };