import { promises as fs } from 'fs';
import path from 'path';
import { STATIC_DIR } from '../config/index.js';

export async function spaFallback(req, res, next) {
  if (req.method !== 'GET') return next();
  
  const filePath = path.join(STATIC_DIR, req.path);
  try {
    const stats = await fs.stat(filePath);
    if (stats.isFile()) return next();
  } catch {
    // File doesn't exist, serve index.html for SPA routing
  }
  
  req.url = '/index.html';
  next();
}
