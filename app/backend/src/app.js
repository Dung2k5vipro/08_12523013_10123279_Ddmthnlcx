const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const config = require('./config/env');
const { connectDatabase, disconnectDatabase } = require('./config/database');
const requestIdMiddleware = require('./middlewares/request-id.middleware');
const requestLoggerMiddleware = require('./middlewares/request-logger.middleware');
const routes = require('./routes');
const notFoundMiddleware = require('./middlewares/not-found.middleware');
const errorHandlerMiddleware = require('./middlewares/error-handler.middleware');

const app = express();

app.use(requestIdMiddleware);
app.use(requestLoggerMiddleware);
app.use(helmet());
app.use(cors({ origin: config.CORS_ORIGIN }));
app.use(express.json({ limit: '100kb' }));

app.use(routes);
app.use(notFoundMiddleware);
app.use(errorHandlerMiddleware);

if (require.main === module) {
	let server;

	const shutdown = async (signal) => {
		console.log(`Nhận ${signal}, đang đóng ứng dụng...`);

		if (server) {
			await new Promise((resolve) => server.close(resolve));
		}

		await disconnectDatabase();
		process.exit(0);
	};

	process.once('SIGINT', () => shutdown('SIGINT'));
	process.once('SIGTERM', () => shutdown('SIGTERM'));

	connectDatabase()
		.then(() => {
			server = app.listen(config.PORT, () => {
				console.log(`Backend đang lắng nghe tại cổng ${config.PORT}`);
			});
		})
		.catch((error) => {
			console.error(`Không thể khởi động ứng dụng: ${error.message}`);
			process.exitCode = 1;
		});
}

module.exports = app;
