const express = require('express');

const predictController = require('../controllers/predict.controller');
const validateMiddleware = require('../middlewares/validate.middleware');
const validatePredictBody = require('../validators/predict.validator');
const validatePaginationQuery = require('../validators/pagination.validator');

const router = express.Router();

router.post('/api/predict', validateMiddleware(validatePredictBody), predictController.predict);
router.get('/api/predictions', validateMiddleware(validatePaginationQuery, 'query'), predictController.listPredictions);
router.get('/api/predictions/stats', predictController.getStatistics);
router.get('/api/predictions/:id', predictController.getPrediction);

module.exports = router;