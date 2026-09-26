class AppError extends Error {
	constructor(message, statusCode, code, details = []) {
		super(message);
		this.name = 'AppError';
		this.statusCode = statusCode;
		this.code = code;
		this.details = details;
		this.isOperational = true;
		Error.captureStackTrace(this, AppError);
	}

	static badRequest(message, details = []) {
		return new AppError(message, 400, 'BAD_REQUEST', details);
	}

	static notFound(message, details = []) {
		return new AppError(message, 404, 'NOT_FOUND', details);
	}

	static validationError(message, details = []) {
		return new AppError(message, 422, 'VALIDATION_ERROR', details);
	}

	static badGateway(message, details = []) {
		return new AppError(message, 502, 'BAD_GATEWAY', details);
	}

	static serviceUnavailable(message, details = []) {
		return new AppError(message, 503, 'SERVICE_UNAVAILABLE', details);
	}
}

module.exports = AppError;