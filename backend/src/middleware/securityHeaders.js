import { securityHeaders } from '../config/helmet.config.js';
import config from '../config/config.js';

export function applySecurityHeaders(app) {
  app.use(securityHeaders);
  app.disable('x-powered-by');
  app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    next();
  });
}

export function applyCachingHeaders(app) {
  app.use((req, res, next) => {
    const reqPath = req.path;

    if (reqPath === '/' || reqPath.endsWith('.html')) {
      res.set('Cache-Control', 'public, max-age=0, must-revalidate');
    } else if (reqPath.startsWith('/css/') || reqPath.startsWith('/js/')) {
      res.set('Cache-Control', 'public, max-age=31536000, immutable');
    } else if (reqPath.startsWith('/assets/') || isAssetFile(reqPath)) {
      res.set('Cache-Control', 'public, max-age=31536000');
    }

    next();
  });
}

function isAssetFile(path) {
  const assetExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.webp'];
  return assetExtensions.some(ext => path.endsWith(ext));
}

export function applyHttpsRedirect(app) {
  if (!config.forceHttps) return;

  app.use((req, res, next) => {
    if (req.protocol === 'https') {
      return next();
    }
    res.redirect(301, `https://${req.hostname}${req.originalUrl}`);
  });
}
