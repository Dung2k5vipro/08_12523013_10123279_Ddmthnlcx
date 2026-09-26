jest.mock('axios', () => ({
	create: jest.fn(() => ({ request: jest.fn() }))
}));

const request = require('supertest');
const axios = require('axios');
const app = require('../src/app');
const healthService = require('../src/services/health.service');

const axiosRequest = axios.create.mock.results[0].value.request;

describe('system endpoints', () => {
	test('returns 200 when system overall_status is ok', async () => {
		healthService.getSystemHealth = jest.fn().mockResolvedValue({
			backend: { status: 'up' },
			mongodb: { status: 'up' },
			ai_service: { status: 'up' },
			overall_status: 'ok'
		});

		const response = await request(app).get('/api/health');

		expect(response.status).toBe(200);
		expect(response.body.overall_status).toBe('ok');
	});

	test('returns 503 when AI service is down', async () => {
		healthService.getSystemHealth = jest.fn().mockResolvedValue({
			backend: { status: 'up' },
			mongodb: { status: 'up' },
			ai_service: { status: 'down' },
			overall_status: 'down'
		});

		const response = await request(app).get('/api/health');

		expect(response.status).toBe(503);
		expect(response.body.ai_service.status).toBe('down');
	});

	test('proxies model info from AI service', async () => {
		axiosRequest.mockResolvedValueOnce({ data: { model_version: 'model-v1', model_name: 'regressor' } });

		const response = await request(app).get('/api/model-info');

		expect(response.status).toBe(200);
		expect(response.body).toEqual({ model_version: 'model-v1', model_name: 'regressor' });
	});

	test('returns standard fields and limits', async () => {
		const response = await request(app).get('/api/fields');

		expect(response.status).toBe(200);
		expect(response.body.fields).toHaveLength(7);
		expect(response.body.limits.engine_size).toEqual({ min: 0.8, max: 8.4 });
	});

	test('returns 404 for an unknown route', async () => {
		const response = await request(app).get('/api/unknown-route');

		expect(response.status).toBe(404);
		expect(response.body.error.code).toBe('NOT_FOUND');
	});
});