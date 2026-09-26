const { v4: uuidv4 } = require('uuid');

const { REQUEST_ID_HEADER } = require('../config/constants');

const requestIdMiddleware = (req, res, next) => {
	const incomingRequestId = req.get(REQUEST_ID_HEADER);
	const requestId = incomingRequestId && incomingRequestId.trim() ? incomingRequestId : uuidv4();

	req.requestId = requestId;
	res.setHeader(REQUEST_ID_HEADER, requestId);
	next();
};

module.exports = requestIdMiddleware;