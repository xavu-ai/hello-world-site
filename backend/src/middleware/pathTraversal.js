/**
 * Custom error class for path traversal attempts
 */
class PathTraversalError extends Error {
  constructor(message = 'Directory traversal attempt detected') {
    super(message);
    this.name = 'PathTraversalError';
    this.statusCode = 403;
  }
}

/**
 * Middleware to prevent path traversal attacks
 * Validates that the requested path does not escape the static directory
 * @param {Object} options
 * @param {string} options.staticDir - The base static directory path
 * @returns {Function} Express middleware
 */
function createPathTraversalMiddleware(options = {}) {
  const { staticDir = 'public' } = options;

  return (req, res, next) => {
    const requestedPath = req.path;

    // Check for path traversal patterns
    const traversalPatterns = [
      /\.\./g,
      /\.\.%2f/gi,
      /%2e%2e/gi,
      /%252e/gi,
    ];

    for (const pattern of traversalPatterns) {
      if (pattern.test(requestedPath)) {
        return next(new PathTraversalError('Invalid path: directory traversal not allowed'));
      }
    }

    // Normalize and validate the path
    const path = require('path');
    const fs = require('fs').promises;

    // Decode URI component to handle encoded traversal attempts
    let decodedPath;
    try {
      decodedPath = decodeURIComponent(requestedPath);
    } catch {
      return next(new PathTraversalError('Invalid path encoding'));
    }

    // Build the full path
    const fullPath = path.join(staticDir, decodedPath);

    // Resolve to absolute and check it's within staticDir
    const absoluteStaticDir = path.resolve(staticDir);
    const absoluteFullPath = path.resolve(fullPath);

    // Ensure the resolved path is within staticDir
    if (!absoluteFullPath.startsWith(absoluteStaticDir + path.sep) && absoluteFullPath !== absoluteStaticDir) {
      return next(new PathTraversalError('Access denied: path outside static directory'));
    }

    next();
  };
}

module.exports = {
  createPathTraversalMiddleware,
  PathTraversalError
};
