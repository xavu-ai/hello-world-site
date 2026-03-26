import express, { Express } from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import compression from 'compression';
import config from './config/server.js';
import { securityHeaders, cachingHeaders, corsHeaders, removePoweredBy } from './middleware/securityHeaders.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';
import staticRoutes from './routes/static.js';
import logger from './utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create Express application
const app: Express = express();

// Trust proxy (for when behind nginx/load balancer)
app.set('trust proxy', 1);

// Remove X-Powered-By header
removePoweredBy(null as never, {} as never, () => {});

// Global middleware
app.use(compression());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Security and caching headers
app.use(securityHeaders);
app.use(cachingHeaders);
app.use(corsHeaders);

// Request logging
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.http(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`, {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration
    });
  });
  next();
});

// Static file routes
app.use(staticRoutes);

// 404 handler for unmatched routes
app.use(notFoundHandler);

// Global error handler
app.use(errorHandler);

// Start server if not in test mode
let server: ReturnType<Express['listen']> | undefined;

function startServer(): Promise<void> {
  return new Promise((resolve) => {
    server = app.listen(config.port, config.host, () => {
      logger.info(`Server running at http://${config.host}:${config.port}`);
      logger.info(`Environment: ${config.nodeEnv}`);
      logger.info(`Public directory: ${path.resolve(config.publicDir)}`);
      resolve();
    });
  });
}

function gracefulShutdown(signal: string): void {
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

// Register shutdown handlers
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start server if not being imported for testing
if (process.env.NODE_ENV !== 'test') {
  startServer().catch((err) => {
    logger.error('Failed to start server', { error: err.message });
    process.exit(1);
  });
}

export { app, startServer };
export default app;
