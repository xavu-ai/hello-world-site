const express = require('express');
const helmet = require('helmet');
const compression = require('compression');

const { createCorrelationIdMiddleware } = require('./middleware/correlationId');
const { createPathTraversalMiddleware } = require('./middleware/pathTraversal');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');
const { staticFileLimiter } = require('./middleware/rateLimit');
const { createLogger } = require('./utils/logger');
const healthRoutes = require('./routes/health');
const { createStaticRouter } = require('./routes/static');

/**
 * Create and configure Express application
 * @param {Object} config - Application configuration
 * @param {string} config.staticDir - Directory for static files
 * @param {string} config.indexFile - Index file name for SPA fallback
 * @param {string} config.port - Server port
 * @param {string} config.env - Environment (development, production)
 * @returns {Object} Express app instance
 */
function createApp(config = {}) {
  const {
    staticDir = 'public',
    indexFile = 'index.html',
    port = process.env.PORT || 3000,
    env = process.env.NODE_ENV || 'development'
  } = config;

  const app = express();

  // Trust proxy for accurate IP logging
  app.set('trust proxy', 1);

  // Middleware registration ORDER:
  // 1. Correlation ID (must be first to include in all logs)
  app.use(createCorrelationIdMiddleware());

  // 2. Path traversal protection
  app.use(createPathTraversalMiddleware({ staticDir }));

  // 3. Security headers
  app.use(helmet());

  // 4. Compression
  app.use(compression());

  // 5. Body parsing (for future API routes)
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // 6. Request logging
  app.use(createLogger({ format: 'combined' }));

  // 7. Health check routes (no rate limiting needed)
  app.use(healthRoutes);

  // 8. Rate limiting for static files
  app.use('/static', staticFileLimiter);

  // 9. Static file serving with SPA fallback
  app.use(createStaticRouter({ staticDir, indexFile }));

  // 10. 404 handler for unmatched routes
  app.use(notFoundHandler);

  // 11. Global error handler (must be last)
  app.use(errorHandler);

  return app;
}

// Create default app instance for testing
const app = createApp({
  staticDir: process.env.STATIC_DIR || 'public',
  indexFile: process.env.INDEX_FILE || 'index.html',
  port: process.env.PORT || 3000,
  env: process.env.NODE_ENV || 'development'
});

/**
 * Start the server with graceful shutdown
 * @param {Object} config - Application configuration
 * @returns {Object} Server instance
 */
function startServer(config = {}) {
  const app = createApp(config);
  const port = config.port || process.env.PORT || 3000;

  const server = app.listen(port, () => {
    console.log(`[${new Date().toISOString()}] Server started`);
    console.log(`Environment: ${config.env || process.env.NODE_ENV || 'development'}`);
    console.log(`Listening on port: ${port}`);
    console.log(`Static directory: ${config.staticDir || 'public'}`);
  });

  // Graceful shutdown handlers
  const shutdown = (signal) => {
    console.log(`\n[${new Date().toISOString()}] Received ${signal}. Starting graceful shutdown...`);

    server.close((err) => {
      if (err) {
        console.error(`[${new Date().toISOString()}] Error during shutdown:`, err);
        process.exit(1);
      }
      console.log(`[${new Date().toISOString()}] Server closed gracefully`);
      process.exit(0);
    });

    // Force shutdown after 30 seconds
    setTimeout(() => {
      console.error(`[${new Date().toISOString()}] Forced shutdown after timeout`);
      process.exit(1);
    }, 30000);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  return server;
}

// Start server if run directly
if (require.main === module) {
  startServer({
    staticDir: process.env.STATIC_DIR || 'public',
    indexFile: process.env.INDEX_FILE || 'index.html',
    port: process.env.PORT || 3000,
    env: process.env.NODE_ENV || 'development'
  });
}

module.exports = {
  app,
  createApp,
  startServer
};
