import express from 'express';
import compression from 'compression';
import helmet from 'helmet';
import morgan from 'morgan';
import { createServer } from 'http';
import { join, extname } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
import dotenv from 'dotenv';
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const NODE_ENV = process.env.NODE_ENV || 'development';
const PUBLIC_DIR = join(__dirname, 'public');

// Correlation ID generator
const generateCorrelationId = () => {
  return `corr-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
};

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));

// Compression middleware
app.use(compression());

// Request logging in development
if (NODE_ENV === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// Parse JSON and URL-encoded bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Static file serving with fallthrough for SPA routing
app.use(express.static(PUBLIC_DIR, {
  maxAge: NODE_ENV === 'production' ? '1d' : 0,
  etag: true,
  lastModified: true,
  setHeaders: (res, filePath) => {
    // Set appropriate headers
    const ext = extname(filePath).toLowerCase();
    const mimeTypes = {
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.svg': 'image/svg+xml',
      '.ico': 'image/x-icon',
      '.txt': 'text/plain',
      '.woff': 'font/woff',
      '.woff2': 'font/woff2',
    };
    if (mimeTypes[ext]) {
      res.setHeader('Content-Type', mimeTypes[ext]);
    }
  },
}));

// SPA fallback - serve index.html for any non-API routes
app.use((req, res, next) => {
  // Skip API routes and existing files
  if (req.path.startsWith('/api') || req.path.startsWith('/health')) {
    return next();
  }

  // Check if the request is for an existing file
  const requestedPath = join(PUBLIC_DIR, req.path);
  if (fs.existsSync(requestedPath) && fs.statSync(requestedPath).isFile()) {
    return next();
  }

  // Serve index.html for SPA routing
  res.sendFile(join(PUBLIC_DIR, 'index.html'));
});

// Path traversal protection middleware
app.use((req, res, next) => {
  const requestedPath = join(PUBLIC_DIR, req.path);
  if (!requestedPath.startsWith(PUBLIC_DIR)) {
    const correlationId = generateCorrelationId();
    console.error(`[${correlationId}] Path traversal attempt blocked: ${req.path}`);
    return res.status(400).json({
      error: 'ValidationError',
      message: 'Invalid request path',
      correlationId,
    });
  }
  next();
});

// Error handling middleware
app.use((err, req, res, next) => {
  const correlationId = generateCorrelationId();
  console.error(`[${correlationId}] Error:`, err);

  if (err.status === 404) {
    return res.status(404).json({
      error: 'NotFoundError',
      message: 'Resource not found',
      correlationId,
    });
  }

  res.status(err.status || 500).json({
    error: 'InternalServerError',
    message: NODE_ENV === 'production' ? 'An unexpected error occurred' : err.message,
    correlationId,
  });
});

// Only start the server if this file is run directly (not imported)
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  const server = createServer(app);

  // Graceful shutdown handlers
  const gracefulShutdown = (signal) => {
    console.log(`\n${signal} received. Starting graceful shutdown...`);
    
    server.close(() => {
      console.log('HTTP server closed. Exiting process.');
      process.exit(0);
    });

    // Force close after 10 seconds
    setTimeout(() => {
      console.error('Could not close connections in time, forcefully shutting down');
      process.exit(1);
    }, 10000);
  };

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));

  // Start server
  server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Environment: ${NODE_ENV}`);
    console.log(`Serving static files from: ${PUBLIC_DIR}`);
  });
}

export { app };
