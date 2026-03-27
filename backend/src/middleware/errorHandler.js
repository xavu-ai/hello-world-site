/**
 * Custom error classes for the application
 */
class NotFoundError extends Error {
  constructor(message = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = 404;
  }
}

class InternalServerError extends Error {
  constructor(message = 'Internal server error') {
    super(message);
    this.name = 'InternalServerError';
    this.statusCode = 500;
  }
}

class RateLimitError extends Error {
  constructor(message = 'Too many requests') {
    super(message);
    this.name = 'RateLimitError';
    this.statusCode = 429;
  }
}

/**
 * Global error handler middleware
 * Returns JSON error response with requestId and timestamp
 * @param {Error} err - Error object
 * @param {Object} req - Express request
 * @param {Object} res - Express response
 * @param {Function} next - Express next function
 */
function errorHandler(err, req, res, next) {
  // Default values
  let statusCode = err.statusCode || 500;
  let message = err.message || 'Internal server error';
  let errorName = err.name || 'Error';

  // Get request ID from correlation ID middleware
  const requestId = req.correlationId || 'unknown';

  // Get timestamp
  const timestamp = new Date().toISOString();

  // Prepare response
  const response = {
    error: message,
    requestId,
    timestamp
  };

  // Add stack trace in non-production environments
  if (process.env.NODE_ENV !== 'production' && err.stack) {
    response.stack = err.stack;
  }

  // Log error (using console for simplicity, would use logger in production)
  console.error(`[${timestamp}] ${errorName}: ${message}`, {
    requestId,
    statusCode,
    path: req.path,
    method: req.method,
    stack: process.env.NODE_ENV !== 'production' ? err.stack : undefined
  });

  res.status(statusCode).json(response);
}

/**
 * 404 handler for unmatched routes
 */
function notFoundHandler(req, res) {
  const requestId = req.correlationId || 'unknown';
  const timestamp = new Date().toISOString();

  res.status(404).json({
    error: 'Not found',
    requestId,
    timestamp
  });
}

module.exports = {
  errorHandler,
  notFoundHandler,
  NotFoundError,
  InternalServerError,
  RateLimitError
};
