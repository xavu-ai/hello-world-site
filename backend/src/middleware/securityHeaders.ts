import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';

/**
 * Apply security headers to all responses
 */
export const securityHeaders = helmet();

/**
 * Apply caching headers based on file type
 */
export function cachingHeaders(req: Request, res: Response, next: NextFunction): void {
  const path = req.path;

  // No cache for HTML files
  if (path.endsWith('.html') || path === '/') {
    res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate');
    return next();
  }

  // Long cache for versioned/static assets
  const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', '.woff', '.woff2', '.ttf', '.eot', '.otf'];
  const ext = path.substring(path.lastIndexOf('.')).toLowerCase();

  if (staticExtensions.includes(ext)) {
    res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    return next();
  }

  // Default cache for other assets
  res.setHeader('Cache-Control', 'public, max-age=3600');
  next();
}

/**
 * Apply CORS headers (if needed in future)
 */
export function corsHeaders(_req: Request, res: Response, next: NextFunction): void {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  next();
}

/**
 * Remove x-powered-by header
 */
export function removePoweredBy(_req: Request, res: Response, next: NextFunction): void {
  res.removeHeader('X-Powered-By');
  next();
}

export default { securityHeaders, cachingHeaders, corsHeaders, removePoweredBy };
