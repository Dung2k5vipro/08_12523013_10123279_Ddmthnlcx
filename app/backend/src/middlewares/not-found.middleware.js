const AppError = require('../utils/app-error');

const notFoundMiddleware = (req, res, next) => {
	next(AppError.notFound('Route không tồn tại'));
};

module.exports = notFoundMiddleware;