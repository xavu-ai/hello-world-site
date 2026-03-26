import request from 'supertest';
import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { applySecurityHeaders, applyCachingHeaders } from '../../src/middleware/securityHeaders.js';
import { errorHandler, notFoundHandler } from '../../src/middleware/errorHandler.js';
import staticRoutes from '../../src/routes/staticRoutes.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe('Static File Serving Integration', () => {
  let securedApp;

  beforeAll(() => {
    securedApp = express();
    applySecurityHeaders(securedApp);
    applyCachingHeaders(securedApp);
    securedApp.use(staticRoutes);
    securedApp.use(notFoundHandler);
    securedApp.use(errorHandler);
  });

  test('GET / returns index.html with correct MIME type', async () => {
    const res = await request(securedApp).get('/');
    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toMatch(/text\/html/);
  });

  test('GET /css/style.css returns CSS with correct MIME type', async () => {
    const res = await request(securedApp).get('/css/style.css');
    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toMatch(/text\/css/);
    expect(res.headers['cache-control']).toBe('public, max-age=31536000, immutable');
  });

  test('GET /js/script.js returns JS with correct MIME type', async () => {
    const res = await request(securedApp).get('/js/script.js');
    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toMatch(/application\/javascript/);
    expect(res.headers['cache-control']).toBe('public, max-age=31536000, immutable');
  });

  test('GET /nonexistent returns 404', async () => {
    const res = await request(securedApp).get('/nonexistent');
    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('error', 'NotFoundError');
  });
});

describe('Security Headers Integration', () => {
  let securedApp;

  beforeAll(() => {
    securedApp = express();
    applySecurityHeaders(securedApp);
    applyCachingHeaders(securedApp);
    securedApp.use(staticRoutes);
    securedApp.use(notFoundHandler);
    securedApp.use(errorHandler);
  });

  test('should include X-Frame-Options header', async () => {
    const res = await request(securedApp).get('/');
    expect(res.headers['x-frame-options']).toBe('DENY');
  });

  test('should include X-Content-Type-Options header', async () => {
    const res = await request(securedApp).get('/');
    expect(res.headers['x-content-type-options']).toBe('nosniff');
  });

  test('should include Cache-Control for HTML', async () => {
    const res = await request(securedApp).get('/');
    expect(res.headers['cache-control']).toBeDefined();
  });
});
