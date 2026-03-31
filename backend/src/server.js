import express from 'express';
import compression from 'compression';
import morgan from 'morgan';
import config from './config/config.js';
import { applySecurityHeaders, applyCachingHeaders, applyHttpsRedirect } from './middleware/securityHeaders.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';
import staticRoutes from './routes/staticRoutes.js';
import logger from './utils/logger.js';

const app = express();

app.use(compression());
app.use(morgan('combined', { stream: { write: (message) => logger.http(message.trim()) } }));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

applyHttpsRedirect(app);
applySecurityHeaders(app);
applyCachingHeaders(app);

app.use(staticRoutes);

app.use(notFoundHandler);
app.use(errorHandler);

let server;

function startServer() {
  return new Promise((resolve) => {
    server = app.listen(config.port, config.host, () => {
      logger.info(`Server running at http://${config.host}:${config.port}`);
      logger.info(`Environment: ${config.env}`);
      resolve();
    });
  });
}

function gracefulShutdown(signal) {
  logger.info(`${signal} received. Starting graceful shutdown...`);
  if (server) {
    server.close(() => {
      logger.info('HTTP server closed');
      process.exit(0);
    });
    setTimeout(() => {
      logger.error('Forced shutdown after timeout');
      process.exit(1);
    }, 10000);
  } else {
    process.exit(0);
  }
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

if (process.env.NODE_ENV !== 'test') {
  startServer();
}

export { app, startServer };
