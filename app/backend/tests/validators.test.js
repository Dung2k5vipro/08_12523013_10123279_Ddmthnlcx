const validatePredictBody = require('../src/validators/predict.validator');
const AppError = require('../src/utils/app-error');

const VALID_BODY = {
	model_year: 2020,
	make: 'Toyota',
	vehicle_class: 'SUV',
	engine_size: 2.0,
	cylinders: 4,
	transmission: 'Automatic',
	fuel_type: 'X'
};

describe('predict validator', () => {
	test('accepts a valid body', () => {
		expect(validatePredictBody(VALID_BODY)).toEqual(VALID_BODY);
	});

	test('rejects missing fields with all validation details', () => {
		expect.assertions(3);
		try {
			validatePredictBody({});
		} catch (error) {
			expect(error).toBeInstanceOf(AppError);
			expect(error.statusCode).toBe(422);
			expect(error.details.length).toBe(7);
		}
	});

	test('rejects invalid types', () => {
		expect(() => validatePredictBody({ ...VALID_BODY, make: 123 })).toThrow(AppError);
	});

	test.each([
		[1994, 'model_year'],
		[2024, 'model_year'],
		[0.7, 'engine_size'],
		[8.5, 'engine_size']
	])('rejects out-of-range %s for %s', (value, field) => {
		expect(() => validatePredictBody({ ...VALID_BODY, [field]: value })).toThrow(AppError);
	});

	test('rejects non-integer cylinders', () => {
		expect(() => validatePredictBody({ ...VALID_BODY, cylinders: 4.5 })).toThrow(AppError);
	});

	test('rejects unknown fields', () => {
		expect(() => validatePredictBody({ ...VALID_BODY, unknown_field: true })).toThrow(AppError);
	});

	test('converts numeric strings and trims strings', () => {
		const result = validatePredictBody({
			...VALID_BODY,
			model_year: '2020',
			engine_size: '2.5',
			cylinders: '6',
			make: ' Toyota '
		});

		expect(result.model_year).toBe(2020);
		expect(result.engine_size).toBe(2.5);
		expect(result.cylinders).toBe(6);
		expect(result.make).toBe('Toyota');
	});
});