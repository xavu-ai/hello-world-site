import { config } from 'dotenv';
config();

export const PORT = parseInt(process.env.PORT || '3000', 10);
export const NODE_ENV = process.env.NODE_ENV || 'production';
export const STATIC_DIR = process.env.STATIC_DIR || './public';
export const CORS_ORIGINS = process.env.CORS_ORIGINS?.split(',') || ['*'];
export const COMPRESSION_LEVEL = parseInt(process.env.COMPRESSION_LEVEL || '6', 10);
