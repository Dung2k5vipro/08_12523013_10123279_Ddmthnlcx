const express = require('express');

const predictRoutes = require('./predict.routes');
const systemRoutes = require('./system.routes');

const router = express.Router();

router.use(predictRoutes);
router.use(systemRoutes);

module.exports = router;