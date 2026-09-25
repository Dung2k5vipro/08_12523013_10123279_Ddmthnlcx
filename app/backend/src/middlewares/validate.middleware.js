const validateMiddleware = (schemaFn, source = 'body') => (req, res, next) => {
	try {
		req.validated = schemaFn(req[source]);
		next();
	} catch (error) {
		next(error);
	}
};

module.exports = validateMiddleware;