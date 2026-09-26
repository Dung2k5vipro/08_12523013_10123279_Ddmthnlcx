jest.mock('axios', () => ({
	create: jest.fn(() => ({ request: jest.fn() }))
}));

const request = require('supertest');
const axios = require('axios');
const app = require('../src/app');
const Prediction = require('../src/models/prediction.model');

const axiosRequest = axios.create.mock.results[0].value.request;

beforeEach(async () => {
	axiosRequest.mockResolvedValue({ data: {} });
	await Prediction.create([
		{ request_id: 'list-1', model_year: 2020, make: 'Toyota', vehicle_class: 'SUV', engine_size: 2, cylinders: 4, transmission: 'A', fuel_type: 'X', prediction: 7, model_version: 'v1', created_at: new Date('2024-01-01') },
		{ request_id: 'list-2', model_year: 2021, make: 'Honda', vehicle_class: 'Sedan', engine_size: 1.8, cylinders: 4, transmission: 'A', fuel_type: 'X', prediction: 6, model_version: 'v1', created_at: new Date('2024-01-02') },
		{ request_id: 'list-3', model_year: 2022, make: 'Toyota', vehicle_class: 'Truck', engine_size: 3, cylinders: 6, transmission: 'A', fuel_type: 'X', prediction: 9, model_version: 'v1', created_at: new Date('2024-01-03') }
	]);
});

describe('prediction collection endpoints', () => {
	test('supports pagination and descending sort', async () => {
		const response = await request(app).get('/api/predictions?page=1&limit=2&sort=-created_at');

		expect(response.status).toBe(200);
		expect(response.body.page).toBe(1);
		expect(response.body.limit).toBe(2);
		expect(response.body.total).toBe(3);
		expect(response.body.total_pages).toBe(2);
		expect(response.body.items.map((item) => item.request_id)).toEqual(['list-3', 'list-2']);
	});

	test('returns a prediction by ObjectId', async () => {
		const document = await Prediction.findOne({ request_id: 'list-1' });
		const response = await request(app).get(`/api/predictions/${document.id}`);

		expect(response.status).toBe(200);
		expect(response.body.request_id).toBe('list-1');
	});

	test('returns 404 when prediction does not exist', async () => {
		const response = await request(app).get('/api/predictions/507f1f77bcf86cd799439011');

		expect(response.status).toBe(404);
		expect(response.body.error.code).toBe('NOT_FOUND');
	});

	test('returns 400 for invalid ObjectId', async () => {
		const response = await request(app).get('/api/predictions/not-an-object-id');

		expect(response.status).toBe(400);
		expect(response.body.error.code).toBe('BAD_REQUEST');
	});

	test('returns statistics', async () => {
		const response = await request(app).get('/api/predictions/stats');

		expect(response.status).toBe(200);
		expect(response.body.total_predictions).toBe(3);
		expect(response.body.average_prediction).toBe(22 / 3);
		expect(response.body.min_prediction).toBe(6);
		expect(response.body.max_prediction).toBe(9);
		expect(response.body.predictions_by_make[0]).toEqual({ make: 'Toyota', count: 2 });
	});
});