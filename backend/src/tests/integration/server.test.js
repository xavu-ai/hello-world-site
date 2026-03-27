const request = require('supertest');
const { createApp, startServer } = require('../../server');

describe('Server Integration Tests', () => {
  let app;

  beforeAll(() => {
    app = createApp({ staticDir: 'public' });
  });

  describe('Health Endpoint', () => {
    test('GET /health should return 200', async () => {
      const response = await request(app).get('/health');
      expect(response.status).toBe(200);
    });

    test('GET /health should return status ok', async () => {
      const response = await request(app).get('/health');
      expect(response.body.status).toBe('ok');
    });

    test('GET /health should return ISO8601 timestamp', async () => {
      const response = await request(app).get('/health');
      expect(response.body.timestamp).toBeDefined();
      const timestamp = new Date(response.body.timestamp);
      expect(timestamp.toISOString()).toBe(response.body.timestamp);
    });

    test('GET /health should include X-Request-ID header', async () => {
      const response = await request(app).get('/health');
      expect(response.headers['x-request-id']).toBeDefined();
    });
  });

  describe('Static File Serving', () => {
    test('GET / should serve index.html', async () => {
      const response = await request(app).get('/');
      expect(response.status).toBe(200);
      expect(response.text).toContain('<!DOCTYPE html>');
    });

    test('GET /static/index.html should serve static file', async () => {
      const response = await request(app).get('/static/index.html');
      expect(response.status).toBe(200);
      expect(response.text).toContain('<!DOCTYPE html>');
    });
  });

  describe('404 Handling', () => {
    test('GET /nonexistent should return 404', async () => {
      const response = await request(app).get('/nonexistent');
      expect(response.status).toBe(404);
    });

    test('GET /nonexistent should return JSON error', async () => {
      const response = await request(app).get('/nonexistent');
      expect(response.body.error).toBeDefined();
      expect(response.body.error).toBe('Not found');
    });

    test('GET /api/* should return 404', async () => {
      const response = await request(app).get('/api/users');
      expect(response.status).toBe(404);
      expect(response.body.error).toContain('API routes not configured');
    });
  });

  describe('Security Headers', () => {
    test('responses should include X-Request-ID header', async () => {
      const response = await request(app).get('/health');
      expect(response.headers['x-request-id']).toBeDefined();
    });

    test('responses should have security headers', async () => {
      const response = await request(app).get('/health');
      // helmet adds various security headers
      expect(response.headers).toHaveProperty('x-content-type-options');
      expect(response.headers['x-content-type-options']).toBe('nosniff');
    });
  });

  describe('Server Startup/Shutdown', () => {
    test('createApp should return valid express app', () => {
      const testApp = createApp({ port: 3001 });
      expect(testApp).toBeDefined();
      expect(typeof testApp.listen).toBe('function');
    });
  });
});
