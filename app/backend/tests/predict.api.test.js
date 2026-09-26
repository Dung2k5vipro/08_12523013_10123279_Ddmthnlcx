jest.mock('axios', () => ({
	create: jest.fn(() => ({ request: jest.fn() }))
}));

const request = require('supertest');
const axios = require('axios');
const app = require('../src/app');
const Prediction = require('../src/models/prediction.model');

const VALID_BODY = {
	model_year: 2020,
	make: 'Toyota',
	vehicle_class: 'SUV',
	engine_size: 2.0,
	cylinders: 4,
	transmission: 'Automatic',
	fuel_type: 'X'
};

const axiosRequest = axios.create.mock.results[0].value.request;

beforeEach(() => {
	axiosRequest.mockResolvedValue({
		data: { prediction: 7.2, unit: 'L/100 km', model_version: 'model-v1' }
	});
});

describe('POST /api/predict', () => {
	test('returns prediction and stores the document', async () => {
		const response = await request(app)
			.post('/api/predict')
			.set('X-Request-ID', 'predict-request-1')
			.send(VALID_BODY);

		expect(response.status).toBe(200);
		expect(response.body).toEqual(expect.objectContaining({
			prediction: 7.2,
			unit: 'L/100 km',
			model_version: 'model-v1',
			request_id: 'predict-request-1'
		}));
		expect(response.body.created_at).toBeTruthy();
		expect(response.headers['x-request-id']).toBe('predict-request-1');
		expect(await Prediction.countDocuments({ request_id: 'predict-request-1' })).toBe(1);
	});

	test('preserves and forwards X-Request-ID to AI', async () => {
		await request(app).post('/api/predict').set('X-Request-ID', 'forwarded-request').send(VALID_BODY);

		expect(axiosRequest).toHaveBeenCalledWith(expect.objectContaining({
			headers: expect.objectContaining({ 'X-Request-ID': 'forwarded-request' }),
			data: { features: VALID_BODY }
		}));
	});

	test('generates a request ID when the header is absent', async () => {
		const response = await request(app).post('/api/predict').send(VALID_BODY);

		expect(response.headers['x-request-id']).toMatch(/^[0-9a-f-]{36}$/);
		expect(response.body.request_id).toBe(response.headers['x-request-id']);
	});

	test('returns 422 with details for invalid body', async () => {
		const response = await request(app).post('/api/predict').send({ model_year: 2020 });

		expect(response.status).toBe(422);
		expect(response.body.error.code).toBe('VALIDATION_ERROR');
		expect(response.body.error.details.length).toBeGreaterThan(0);
	});

	test('returns 400 for malformed JSON', async () => {
		const response = await request(app)
			.post('/api/predict')
			.set('Content-Type', 'application/json')
			.send('{"model_year":');

		expect(response.status).toBe(400);
		expect(response.body.error.code).toBe('INVALID_JSON');
	});

	test.each([
		['ECONNABORTED', 502],
		['ECONNREFUSED', 502]
	])('maps AI %s to 502', async (code, status) => {
		axiosRequest.mockRejectedValueOnce({ code });

		const response = await request(app).post('/api/predict').send(VALID_BODY);

		expect(response.status).toBe(status);
		expect(response.body.error.code).toBe('AI_SERVICE_UNAVAILABLE');
	});

	test('maps AI 503 to 503', async () => {
		axiosRequest.mockRejectedValueOnce({ response: { status: 503, data: {} } });

		const response = await request(app).post('/api/predict').send(VALID_BODY);

		expect(response.status).toBe(503);
		expect(response.body.error.code).toBe('MODEL_NOT_READY');
	});

	test('maps missing prediction from AI to 502', async () => {
		axiosRequest.mockResolvedValueOnce({ data: { unit: 'L/100 km', model_version: 'model-v1' } });

		const response = await request(app).post('/api/predict').send(VALID_BODY);

		expect(response.status).toBe(502);
		expect(response.body.error.code).toBe('AI_SERVICE_ERROR');
	});

	test('does not create a duplicate document for the same request ID', async () => {
		await request(app).post('/api/predict').set('X-Request-ID', 'idempotent-request').send(VALID_BODY);
		const secondResponse = await request(app).post('/api/predict').set('X-Request-ID', 'idempotent-request').send(VALID_BODY);

		expect(secondResponse.status).toBe(200);
		expect(await Prediction.countDocuments({ request_id: 'idempotent-request' })).toBe(1);
	});
});
