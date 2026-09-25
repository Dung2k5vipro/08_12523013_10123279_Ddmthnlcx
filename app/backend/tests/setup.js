const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');

jest.setTimeout(600000);

process.env.PORT = process.env.PORT || '8000';
process.env.NODE_ENV = process.env.NODE_ENV || 'test';
process.env.MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/fuel_consumption_test';
process.env.AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8001';
process.env.AI_SERVICE_TIMEOUT_MS = process.env.AI_SERVICE_TIMEOUT_MS || '1000';
process.env.CORS_ORIGIN = process.env.CORS_ORIGIN || 'http://127.0.0.1:3000';
process.env.LOG_LEVEL = process.env.LOG_LEVEL || 'error';

let mongoServer;

beforeAll(async () => {
	mongoServer = await MongoMemoryServer.create();
	process.env.MONGODB_URI = mongoServer.getUri();
	await mongoose.connect(process.env.MONGODB_URI);
});

afterEach(async () => {
	if (mongoose.connection.readyState !== 1) {
		return;
	}

	const collections = Object.values(mongoose.connection.collections);
	await Promise.all(collections.map((collection) => collection.deleteMany({})));
});

afterAll(async () => {
	await mongoose.disconnect();
	if (mongoServer) {
		await mongoServer.stop();
	}
});