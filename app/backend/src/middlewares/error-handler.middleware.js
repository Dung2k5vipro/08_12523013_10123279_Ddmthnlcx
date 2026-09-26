const AppError = require('../utils/app-error');

const errorHandlerMiddleware = (err, req, res, next) => {
	const isJsonParseError = err.type === 'entity.parse.failed';
	const isMongooseValidationError = err.name === 'ValidationError';
	let statusCode = 500;
	let code = 'INTERNAL_ERROR';
	let message = 'Đã xảy ra lỗi nội bộ';
	let details = [];

	if (err instanceof AppError) {
		statusCode = err.statusCode;
		code = err.code;
		message = err.message;
		details = err.details;
	} else if (isJsonParseError) {
		statusCode = 400;
		code = 'INVALID_JSON';
		message = 'JSON không hợp lệ';
	} else if (isMongooseValidationError) {
		statusCode = 422;
		code = 'VALIDATION_ERROR';
		message = err.message;
		details = Object.values(err.errors || {}).map((validationError) => ({
			field: validationError.path,
			message: validationError.message
		}));
	}

	res.status(statusCode).json({
		error: { code, message, details },
		request_id: req.requestId
	});
};

module.exports = errorHandlerMiddleware;