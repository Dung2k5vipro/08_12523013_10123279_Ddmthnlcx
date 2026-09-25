const asyncHandler = require('../utils/async-handler');
const predictionService = require('../services/prediction.service');

const predict = asyncHandler(async (req, res) => {
	const result = await predictionService.createPrediction(req.validated, req.requestId);
	res.status(200).json(result);
});

const listPredictions = asyncHandler(async (req, res) => {
	const result = await predictionService.listPredictions(req.validated);
	res.status(200).json(result);
});

const getPrediction = asyncHandler(async (req, res) => {
	const result = await predictionService.getPredictionById(req.params.id);
	res.status(200).json(result);
});

const getStatistics = asyncHandler(async (req, res) => {
	const result = await predictionService.getStatistics();
	res.status(200).json(result);
});

module.exports = { predict, listPredictions, getPrediction, getStatistics };