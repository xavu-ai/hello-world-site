const { v4: uuidv4 } = require('uuid');

/**
 * Middleware to add correlation ID to each request
 * Generates UUID v4 and propagates via X-Request-ID header
 * @param {Object} options
 * @param {string} options.headerName - Name of the header for correlation ID
 * @returns {Function} Express middleware
 */
function createCorrelationIdMiddleware(options = {}) {
  const { headerName = 'X-Request-ID' } = options;

  return (req, res, next) => {
    // Use existing header value or generate new UUID v4
    const correlationId = req.get(headerName) || uuidv4();

    // Attach to request object for use in logging
    req.correlationId = correlationId;

    // Set header on response
    res.setHeader(headerName, correlationId);

    next();
  };
}

module.exports = {
  createCorrelationIdMiddleware
};
