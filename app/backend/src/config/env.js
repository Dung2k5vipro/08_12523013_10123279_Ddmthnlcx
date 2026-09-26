const dotenv = require('dotenv');

dotenv.config();

const REQUIRED_ENV_VARIABLES = ['PORT', 'MONGODB_URI', 'AI_SERVICE_URL'];
const missingVariables = REQUIRED_ENV_VARIABLES.filter((variableName) => !process.env[variableName]);

if (missingVariables.length > 0) {
  throw new Error(`Thiếu biến môi trường bắt buộc: ${missingVariables.join(', ')}`);
}

const port = Number(process.env.PORT);
const aiServiceTimeoutMs = Number(process.env.AI_SERVICE_TIMEOUT_MS || 10000);

if (!Number.isInteger(port) || port <= 0) {
  throw new Error('PORT phải là một số nguyên dương');
}

if (!Number.isInteger(aiServiceTimeoutMs) || aiServiceTimeoutMs <= 0) {
  throw new Error('AI_SERVICE_TIMEOUT_MS phải là một số nguyên dương');
}

module.exports = {
  PORT: port,
  NODE_ENV: process.env.NODE_ENV || 'development',
  MONGODB_URI: process.env.MONGODB_URI,
  AI_SERVICE_URL: process.env.AI_SERVICE_URL,
  AI_SERVICE_TIMEOUT_MS: aiServiceTimeoutMs,
  CORS_ORIGIN: process.env.CORS_ORIGIN || '*',
  LOG_LEVEL: process.env.LOG_LEVEL || 'info'
};