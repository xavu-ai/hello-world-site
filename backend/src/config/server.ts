import dotenv from 'dotenv';

dotenv.config();

interface ServerConfig {
  port: number;
  host: string;
  nodeEnv: string;
  publicDir: string;
  logLevel: string;
  enableCompression: boolean;
  cacheControlMaxAge: number;
  isProduction: boolean;
  isDevelopment: boolean;
}

const config: ServerConfig = {
  port: parseInt(process.env.PORT || '3000', 10),
  host: process.env.HOST || '0.0.0.0',
  nodeEnv: process.env.NODE_ENV || 'development',
  publicDir: process.env.PUBLIC_DIR || './public',
  logLevel: process.env.LOG_LEVEL || 'info',
  enableCompression: process.env.ENABLE_COMPRESSION !== 'false',
  cacheControlMaxAge: parseInt(process.env.CACHE_CONTROL_MAX_AGE || '3600', 10),
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development'
};

export default config;
