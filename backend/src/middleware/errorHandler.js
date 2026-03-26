import config from '../config/config.js';
import logger from '../utils/logger.js';

export class NotFoundError extends Error {
  constructor(message = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = 404;
  }
}

export class InternalServerError extends Error {
  constructor(message = 'Internal server error') {
    super(message);
    this.name = 'InternalServerError';
    this.statusCode = 500;
  }
}

export function errorHandler(err, req, res, _next) {
  const statusCode = err.statusCode || 500;
  const errorName = err.name || 'Error';
  const message = err.message || 'An unexpected error occurred';

  logger.error({
    error: errorName,
    message,
    statusCode,
    path: req.path,
    method: req.method,
    stack: config.isProduction ? undefined : err.stack
  });

  if (statusCode === 404) {
    return res.status(404).json({
      error: 'NotFoundError',
      message
    });
  }

  res.status(statusCode).json({
    error: errorName,
    message: config.isProduction && statusCode === 500
      ? 'An unexpected error occurred'
      : message
  });
}

export function notFoundHandler(req, res) {
  res.status(404).json({
    error: 'NotFoundError',
    message: `Cannot ${req.method} ${req.path}`
  });
}
