const express = require('express');

const systemController = require('../controllers/system.controller');

const router = express.Router();

router.get('/api/health', systemController.health);
router.get('/api/model-info', systemController.modelInfo);
router.get('/api/fields', systemController.fields);

module.exports = router;