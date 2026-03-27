const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const { NotFoundError } = require('../middleware/errorHandler');

/**
 * Create static file serving routes with SPA fallback
 * @param {Object} options
 * @param {string} options.staticDir - Base directory for static files
 * @param {string} options.indexFile - Path to index.html for SPA fallback
 * @returns {Function} Express router
 */
function createStaticRouter(options = {}) {
  const {
    staticDir = 'public',
    indexFile = 'index.html'
  } = options;

  const router = express.Router();

  // Serve static files from /static/*
  router.get('/static/*', async (req, res, next) => {
    try {
      // Extract the file path from /static/
      const filePath = req.path.replace(/^\/static\//, '');
      const fullPath = path.join(staticDir, filePath);

      // Security check: ensure file exists and is within staticDir
      const absoluteStaticDir = path.resolve(staticDir);
      const absoluteFullPath = path.resolve(fullPath);

      if (!absoluteFullPath.startsWith(absoluteStaticDir + path.sep)) {
        throw new NotFoundError('File not found');
      }

      // Check if file exists
      await fs.access(fullPath);

      // Send the file with root option for relative paths
      res.sendFile(filePath, { root: staticDir });
    } catch (err) {
      if (err.code === 'ENOENT') {
        next(new NotFoundError('Static file not found'));
      } else {
        next(err);
      }
    }
  });

  // SPA fallback for root
  router.get('/', async (req, res, next) => {
    try {
      const indexPath = path.join(staticDir, indexFile);

      // Check if index exists
      await fs.access(indexPath);

      res.sendFile(indexFile, { root: staticDir });
    } catch (err) {
      if (err.code === 'ENOENT') {
        next(new NotFoundError('Index file not found'));
      } else {
        next(err);
      }
    }
  });

  // 404 for /api/* routes
  router.get('/api/*', (req, res, next) => {
    next(new NotFoundError('API routes not configured'));
  });

  return router;
}

module.exports = {
  createStaticRouter
};
