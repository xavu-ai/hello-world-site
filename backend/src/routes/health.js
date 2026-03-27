const express = require('express');
const router = express.Router();

/**
 * GET /health
 * Health check endpoint for container orchestration
 * Returns status and timestamp
 */
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
