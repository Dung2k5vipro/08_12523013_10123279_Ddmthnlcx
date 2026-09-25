const mongoose = require('mongoose');

const aiClient = require('./ai-client.service');

async function getSystemHealth(requestId) {
	const mongodbUp = mongoose.connection.readyState === 1;
	let aiService;

	try {
		const health = await aiClient.getHealth(requestId);
		aiService = { status: 'up', ...health };
	} catch (error) {
		aiService = { status: 'down' };
	}

	const backend = { status: 'up' };
	const mongodb = { status: mongodbUp ? 'up' : 'down', ready_state: mongoose.connection.readyState };
	const overallStatus = backend.status === 'up' && mongodb.status === 'up' && aiService.status === 'up'
		? 'ok'
		: 'down';

	return {
		backend,
		mongodb,
		ai_service: aiService,
		overall_status: overallStatus
	};
}

module.exports = { getSystemHealth };