const logger = require('../utils/logger');

const requestLoggerMiddleware = (req, res, next) => {
	const startedAt = process.hrtime.bigint();

	res.on('finish', () => {
		const durationMs = Number(process.hrtime.bigint() - startedAt) / 1000000;

		logger.info('HTTP request completed', {
			request_id: req.requestId,
			method: req.method,
			url: req.originalUrl,
			status: res.statusCode,
			duration_ms: Number(durationMs.toFixed(2))
		});
	});

	next();
};

module.exports = requestLoggerMiddleware;