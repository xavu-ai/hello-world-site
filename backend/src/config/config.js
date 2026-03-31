import dotenv from 'dotenv';
dotenv.config();

const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  host: process.env.HOST || '0.0.0.0',
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development',
  forceHttps: process.env.FORCE_HTTPS === 'true' || process.env.NODE_ENV === 'production',
  logLevel: process.env.LOG_LEVEL || 'info',
  staticAssets: {
    root: process.env.STATIC_ASSETS_PATH || 'public',
    maxAge: {
      immutable: 31536000, // 1 year for CSS/JS with hash
      html: 0,              // no-cache for HTML
      assets: 31536000      // 1 year for images/fonts
    }
  }
};

export default config;
