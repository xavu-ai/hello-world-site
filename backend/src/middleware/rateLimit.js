const rateLimit = require('express-rate-limit');

/**
 * Rate limiting middleware for static file routes
 * Limits each IP to 1000 requests per 15 minutes
 */
const staticFileLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  message: { error: 'Too many requests' },
  standardHeaders: true, // Return rate limit info in headers
  legacyHeaders: false // Disable X-RateLimit-* headers
});

/**
 * General API rate limiter
 * More restrictive than static file limiter
 */
const apiLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minute
  max: 100, // limit each IP to 100 requests per minute
  message: { error: 'Too many requests, please try again later' },
  standardHeaders: true,
  legacyHeaders: false
});

module.exports = {
  staticFileLimiter,
  apiLimiter
};
