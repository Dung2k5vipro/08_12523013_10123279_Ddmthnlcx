const mongoose = require('mongoose');

const { DEFAULT_UNIT } = require('../config/constants');

const predictionSchema = new mongoose.Schema({
	request_id: {
		type: String,
		required: true,
		unique: true,
		index: true
	},
	model_year: {
		type: Number,
		required: true
	},
	make: {
		type: String,
		required: true,
		trim: true
	},
	vehicle_class: {
		type: String,
		required: true,
		trim: true
	},
	engine_size: {
		type: Number,
		required: true
	},
	cylinders: {
		type: Number,
		required: true
	},
	transmission: {
		type: String,
		required: true,
		trim: true
	},
	fuel_type: {
		type: String,
		required: true,
		trim: true
	},
	prediction: {
		type: Number,
		required: true
	},
	unit: {
		type: String,
		default: DEFAULT_UNIT
	},
	model_version: {
		type: String,
		required: true
	},
	ai_latency_ms: {
		type: Number
	},
	created_at: {
		type: Date,
		default: Date.now,
		index: true
	}
}, {
		collection: 'predictions',
		timestamps: { createdAt: 'created_at', updatedAt: false },
		toJSON: {
			transform: (document, returnedObject) => {
				delete returnedObject.__v;
				if (returnedObject._id) {
					returnedObject.id = returnedObject._id.toString();
					delete returnedObject._id;
				}
				return returnedObject;
			}
		}
	});

predictionSchema.index({ make: 1, created_at: -1 });

module.exports = mongoose.model('Prediction', predictionSchema);