const Joi = require('joi');

const AppError = require('../utils/app-error');
const {
	MIN_MODEL_YEAR,
	MAX_MODEL_YEAR,
	MIN_ENGINE_SIZE,
	MAX_ENGINE_SIZE,
	MIN_CYLINDERS,
	MAX_CYLINDERS
} = require('../config/constants');

const predictSchema = Joi.object({
	model_year: Joi.number().integer().min(MIN_MODEL_YEAR).max(MAX_MODEL_YEAR).required()
		.messages({
			'number.min': `{{#label}} phải nằm trong khoảng ${MIN_MODEL_YEAR} – ${MAX_MODEL_YEAR}`,
			'number.max': `{{#label}} phải nằm trong khoảng ${MIN_MODEL_YEAR} – ${MAX_MODEL_YEAR}`
		}),
	make: Joi.string().trim().min(1).max(50).required(),
	vehicle_class: Joi.string().trim().min(1).max(60).required(),
	engine_size: Joi.number().min(MIN_ENGINE_SIZE).max(MAX_ENGINE_SIZE).required()
		.messages({
			'number.min': `{{#label}} phải nằm trong khoảng ${MIN_ENGINE_SIZE} – ${MAX_ENGINE_SIZE}`,
			'number.max': `{{#label}} phải nằm trong khoảng ${MIN_ENGINE_SIZE} – ${MAX_ENGINE_SIZE}`
		}),
	cylinders: Joi.number().integer().min(MIN_CYLINDERS).max(MAX_CYLINDERS).required()
		.messages({
			'number.min': `{{#label}} phải nằm trong khoảng ${MIN_CYLINDERS} – ${MAX_CYLINDERS}`,
			'number.max': `{{#label}} phải nằm trong khoảng ${MIN_CYLINDERS} – ${MAX_CYLINDERS}`
		}),
	transmission: Joi.string().trim().min(1).max(20).required(),
	fuel_type: Joi.string().trim().min(1).max(20).required()
}).messages({
	'any.required': '{{#label}} là bắt buộc',
	'any.only': '{{#label}} không được phép',
	'number.base': '{{#label}} phải là số',
	'number.integer': '{{#label}} phải là số nguyên',
	'number.min': '{#label} phải lớn hơn hoặc bằng {#limit}',
	'number.max': '{#label} phải nhỏ hơn hoặc bằng {#limit}',
	'string.base': '{{#label}} phải là chuỗi',
	'string.empty': '{{#label}} không được để trống',
	'string.min': '{{#label}} phải có ít nhất {#limit} ký tự',
	'string.max': '{{#label}} không được vượt quá {#limit} ký tự',
	'object.unknown': '{{#label}} không được phép'
});

function validatePredictBody(body) {
	const { error, value } = predictSchema.validate(body, {
		abortEarly: false,
		allowUnknown: false,
		convert: true,
		stripUnknown: false
	});

	if (error) {
		const details = error.details.map((item) => ({
			field: item.path.join('.') || item.context?.key || 'body',
			message: item.message
		}));

		throw AppError.validationError('Dữ liệu dự đoán không hợp lệ', details);
	}

	return value;
}

module.exports = validatePredictBody;
module.exports.predictSchema = predictSchema;