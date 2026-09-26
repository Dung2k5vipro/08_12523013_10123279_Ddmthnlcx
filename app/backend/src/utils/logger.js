const config = require('../config/env');

const LOG_LEVELS = {
	error: 0,
	warn: 1,
	info: 2,
	debug: 3
};

const currentLevel = LOG_LEVELS[config.LOG_LEVEL] ?? LOG_LEVELS.info;

function writeLog(level, message, metadata = {}) {
	if (LOG_LEVELS[level] > currentLevel) {
		return;
	}

	const entry = {
		timestamp: new Date().toISOString(),
		level,
		message,
		...metadata
	};

	if (!metadata.request_id) {
		delete entry.request_id;
	}

	const output = JSON.stringify(entry);
	if (level === 'error') {
		console.error(output);
	} else if (level === 'warn') {
		console.warn(output);
	} else {
		console.log(output);
	}
}

module.exports = {
	error: (message, metadata) => writeLog('error', message, metadata),
	warn: (message, metadata) => writeLog('warn', message, metadata),
	info: (message, metadata) => writeLog('info', message, metadata),
	debug: (message, metadata) => writeLog('debug', message, metadata)
};