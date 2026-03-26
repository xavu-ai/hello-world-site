import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import config from '../config/config.js';
import { NotFoundError } from '../middleware/errorHandler.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();
const publicPath = path.join(__dirname, '../../public');

router.use('/static', express.static(publicPath, {
  maxAge: config.staticAssets.maxAge.assets,
  etag: true,
  lastModified: true,
  setHeaders: (res, filePath) => {
    if (filePath.endsWith('.html')) {
      res.set('Cache-Control', 'public, max-age=0, must-revalidate');
    }
  }
}));

router.get('/', (req, res) => {
  const indexPath = path.join(publicPath, 'index.html');
  res.sendFile(indexPath, (err) => {
    if (err) {
      throw new NotFoundError('index.html not found');
    }
  });
});

router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

export default router;
