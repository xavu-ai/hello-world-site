const express = require('express');
const router = express.Router();

// Track server start time
const startTime = Date.now();

/**
 * GET /health
 * Health check endpoint
 * Returns status, timestamp, and uptime
 */
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: Math.floor((Date.now() - startTime) / 1000)
  });
});

module.exports = router;
