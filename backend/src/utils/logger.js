const morgan = require('morgan');

/**
 * Create configured Morgan logger
 * Uses combined format for production logging
 * @param {Object} options
 * @param {string} options.format - Morgan format string
 * @param {Object} options.options - Morgan stream options
 * @returns {Function} Morgan middleware
 */
function createLogger(options = {}) {
  const {
    format = 'combined',
    options: streamOptions = {}
  } = options;

  // Custom token for correlation ID
  morgan.token('request-id', (req) => req.correlationId || '-');

  // Use combined format with correlation ID
  const logFormat = format === 'combined'
    ? ':request-id - :remote-addr - :method :url :status :res[content-length] - :response-time ms'
    : format;

  return morgan(logFormat, {
    ...streamOptions,
    // Skip health check logging if desired
    skip: (req) => {
      return false; // Log all requests
    }
  });
}

module.exports = {
  createLogger
};
