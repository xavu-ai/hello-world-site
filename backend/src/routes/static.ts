import { Router, Request, Response } from 'express';
import path from 'node:path';
import config from '../config/server.js';
import { StaticFileService } from '../services/staticFileService.js';
import { FileNotFoundError } from '../types/index.js';
import logger from '../utils/logger.js';

// Initialize service with public directory
const publicDir = path.resolve(config.publicDir);
const staticFileService = new StaticFileService(publicDir);

const router = Router();

// Track server start time for uptime calculation
const serverStartTime = Date.now();

/**
 * GET /health
 * Health check endpoint
 */
router.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: Math.floor((Date.now() - serverStartTime) / 1000)
  });
});

/**
 * GET /
 * Serve index.html (SPA fallback)
 */
router.get('/', async (_req: Request, res: Response) => {
  try {
    const indexPath = '/index.html';
    const fileInfo = await staticFileService.getFileInfo(indexPath);

    res.setHeader('Content-Type', fileInfo.mimeType);
    res.setHeader('Content-Length', fileInfo.size);
    res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');

    const readStream = staticFileService.createReadStream(indexPath);
    readStream.pipe(res);

    readStream.on('error', (err) => {
      logger.error('Error streaming index.html', { error: err.message });
      if (!res.headersSent) {
        res.status(500).json({
          error: 'ServerError',
          message: 'Error serving file',
          code: 'SERVER_ERROR',
          timestamp: new Date().toISOString()
        });
      }
    });
  } catch (err) {
    if (err instanceof FileNotFoundError) {
      res.status(404).json({
        error: 'FileNotFoundError',
        message: 'index.html not found',
        code: 'FILE_NOT_FOUND',
        timestamp: new Date().toISOString()
      });
    } else {
      throw err;
    }
  }
});

/**
 * GET *
 * Serve static files (catch-all route)
 */
router.get('*', async (req: Request, res: Response, next) => {
  try {
    // Use req.params['0'] for wildcard captures (Express wildcard * captures in params['0'])
    const requestedPath = req.params['0'] || req.path;

    // Prevent path traversal by validating path
    if (requestedPath.includes('..') || requestedPath.includes('\\')) {
      res.status(400).json({
        error: 'InvalidPathError',
        message: 'Invalid path: directory traversal not allowed',
        code: 'INVALID_PATH',
        timestamp: new Date().toISOString()
      });
      return;
    }

    const fileInfo = await staticFileService.getFileInfo(requestedPath);

    // Set appropriate headers
    res.setHeader('Content-Type', fileInfo.mimeType);
    res.setHeader('Content-Length', fileInfo.size);
    res.setHeader('Last-Modified', fileInfo.lastModified.toUTCString());
    res.setHeader('ETag', `"${fileInfo.size}-${fileInfo.lastModified.getTime()}"`);

    // Set cache headers based on file type
    const ext = requestedPath.toLowerCase().substring(requestedPath.lastIndexOf('.'));
    if (['.css', '.js'].includes(ext)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    } else if (!['.html', '.htm'].includes(ext)) {
      res.setHeader('Cache-Control', `public, max-age=${config.cacheControlMaxAge}`);
    }

    // Stream the file
    const readStream = staticFileService.createReadStream(requestedPath);
    readStream.pipe(res);

    readStream.on('error', (err) => {
      logger.error('Error streaming file', { requestedPath, error: err.message });
      if (!res.headersSent) {
        res.status(500).json({
          error: 'ServerError',
          message: 'Error serving file',
          code: 'SERVER_ERROR',
          timestamp: new Date().toISOString()
        });
      }
    });
  } catch (err) {
    next(err);
  }
});

export default router;
