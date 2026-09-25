const Joi = require('joi');

const AppError = require('../utils/app-error');
const {
	DEFAULT_PAGE,
	DEFAULT_LIMIT,
	MIN_PAGE,
	MIN_LIMIT,
	MAX_LIMIT,
	DEFAULT_SORT
} = require('../config/constants');

const paginationSchema = Joi.object({
	page: Joi.number().integer().min(MIN_PAGE).default(DEFAULT_PAGE),
	limit: Joi.number().integer().min(MIN_LIMIT).max(MAX_LIMIT).default(DEFAULT_LIMIT),
	sort: Joi.string().valid('created_at', DEFAULT_SORT).default(DEFAULT_SORT)
}).messages({
	'number.base': '{{#label}} phải là số',
	'number.integer': '{{#label}} phải là số nguyên',
	'number.min': '{{#label}} phải lớn hơn hoặc bằng {#limit}',
	'number.max': '{{#label}} phải nhỏ hơn hoặc bằng {#limit}',
	'string.base': '{{#label}} phải là chuỗi',
	'any.only': '{{#label}} chỉ được là created_at hoặc -created_at',
	'object.unknown': '{{#label}} không được phép'
});

function validatePaginationQuery(query) {
	const { error, value } = paginationSchema.validate(query, {
		abortEarly: false,
		allowUnknown: false,
		convert: true,
		stripUnknown: false
	});

	if (error) {
		const details = error.details.map((item) => ({
			field: item.path.join('.') || item.context?.key || 'query',
			message: item.message
		}));

		throw AppError.validationError('Tham số phân trang không hợp lệ', details);
	}

	return value;
}

module.exports = validatePaginationQuery;
module.exports.paginationSchema = paginationSchema;