import { Request, Response, NextFunction } from 'express';
import { AppError, FileNotFoundError, InvalidPathError, FileAccessError, ServerError } from '../types/index.js';
import logger from '../utils/logger.js';
import config from '../config/server.js';

/**
 * Global error handler middleware
 */
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  _next: NextFunction
): void {
  // Log the error
  logger.error({
    error: err.name,
    message: err.message,
    path: req.path,
    method: req.method,
    stack: config.isProduction ? undefined : err.stack
  });

  // Handle known app errors
  if (err instanceof AppError) {
    res.status(err.statusCode).json(err.toJSON());
    return;
  }

  // Handle Express built-in errors
  if (err.statusCode) {
    res.status(err.statusCode).json({
      error: err.name,
      message: err.message,
      code: 'EXPRESS_ERROR',
      timestamp: new Date().toISOString()
    });
    return;
  }

  // Handle unknown errors
  const statusCode = 500;
  const message = config.isProduction
    ? 'An unexpected error occurred'
    : err.message || 'An unexpected error occurred';

  res.status(statusCode).json({
    error: 'ServerError',
    message,
    code: 'SERVER_ERROR',
    timestamp: new Date().toISOString()
  });
}

/**
 * 404 Not Found handler for unmatched routes
 */
export function notFoundHandler(req: Request, res: Response): void {
  res.status(404).json({
    error: 'FileNotFoundError',
    message: `Cannot ${req.method} ${req.path}`,
    code: 'FILE_NOT_FOUND',
    timestamp: new Date().toISOString()
  });
}

export default errorHandler;
