import { jest, describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import request from 'supertest';
import { app } from '../../server.js';
import { createServer } from 'http';

describe('Static File Server Integration Tests', () => {
  let server;

  beforeAll(() => {
    server = createServer(app);
  });

  afterAll((done) => {
    server.close(done);
  });

  describe('GET /', () => {
    it('should return index.html with correct content-type', async () => {
      const response = await request(server)
        .get('/')
        .expect('Content-Type', /text\/html/)
        .expect(200);

      expect(response.text).toContain('<!DOCTYPE html>');
      expect(response.text).toContain('Hello World');
    });
  });

  describe('GET /css/styles.css', () => {
    it('should return CSS with correct MIME type', async () => {
      const response = await request(server)
        .get('/css/styles.css')
        .expect('Content-Type', /text\/css/)
        .expect(200);

      expect(response.text).toBeDefined();
      expect(response.text.length).toBeGreaterThan(0);
    });
  });

  describe('GET /js/app.js', () => {
    it('should return JavaScript with correct MIME type', async () => {
      const response = await request(server)
        .get('/js/app.js')
        .expect('Content-Type', /application\/javascript/)
        .expect(200);

      expect(response.text).toBeDefined();
      expect(response.text.length).toBeGreaterThan(0);
    });
  });

  describe('GET /nonexistent', () => {
    it('should return fallback HTML for unknown routes (SPA behavior)', async () => {
      const response = await request(server)
        .get('/nonexistent')
        .expect(200);

      // Should serve index.html as fallback
      expect(response.text).toContain('Hello World');
    });
  });

  describe('Security Headers', () => {
    it('should include X-Content-Type-Options header', async () => {
      const response = await request(server)
        .get('/')
        .expect(200);

      expect(response.headers['x-content-type-options']).toBeDefined();
    });

    it('should include X-Frame-Options header', async () => {
      const response = await request(server)
        .get('/')
        .expect(200);

      expect(response.headers['x-frame-options']).toBeDefined();
    });

    it('should include X-XSS-Protection header', async () => {
      const response = await request(server)
        .get('/')
        .expect(200);

      expect(response.headers['x-xss-protection']).toBeDefined();
    });

    it('should include Content-Security-Policy header', async () => {
      const response = await request(server)
        .get('/')
        .expect(200);

      expect(response.headers['content-security-policy']).toBeDefined();
    });
  });

  describe('Compression', () => {
    it('should accept gzip encoding', async () => {
      const response = await request(server)
        .get('/')
        .set('Accept-Encoding', 'gzip')
        .expect(200);

      expect(response.body || response.text).toBeDefined();
    });

    it('should accept brotli encoding', async () => {
      const response = await request(server)
        .get('/')
        .set('Accept-Encoding', 'br')
        .expect(200);

      expect(response.body || response.text).toBeDefined();
    });
  });

  describe('Path Traversal Attack Prevention', () => {
    it('should block GET /../package.json with 400', async () => {
      const response = await request(server)
        .get('/../package.json')
        .expect(400);

      expect(response.body.error).toBe('ValidationError');
      expect(response.body.correlationId).toBeDefined();
    });
  });

  describe('Health Check Endpoint', () => {
    it('should return 200 OK with status', async () => {
      const response = await request(server)
        .get('/health')
        .expect('Content-Type', /application\/json/)
        .expect(200);

      expect(response.body.status).toBe('ok');
      expect(response.body.timestamp).toBeDefined();
    });
  });

  describe('Cache Control', () => {
    it('should set Cache-Control header', async () => {
      const response = await request(server)
        .get('/')
        .expect(200);

      expect(response.headers['cache-control']).toBeDefined();
    });
  });

  describe('Content Types', () => {
    it('should serve HTML files with text/html', async () => {
      const response = await request(server)
        .get('/')
        .expect('Content-Type', /text\/html/);

      expect(response.status).toBe(200);
    });

    it('should serve CSS files with text/css', async () => {
      const response = await request(server)
        .get('/css/styles.css')
        .expect('Content-Type', /text\/css/);

      expect(response.status).toBe(200);
    });

    it('should serve JS files with application/javascript', async () => {
      const response = await request(server)
        .get('/js/app.js')
        .expect('Content-Type', /application\/javascript/);

      expect(response.status).toBe(200);
    });
  });

  describe('SPA Fallback', () => {
    it('should serve index.html for unknown routes', async () => {
      const response = await request(server)
        .get('/some/unknown/path')
        .expect(200);

      expect(response.text).toContain('<!DOCTYPE html>');
      expect(response.text).toContain('Hello World');
    });

    it('should serve index.html for deep nested routes', async () => {
      const response = await request(server)
        .get('/a/b/c/d/e')
        .expect(200);

      expect(response.text).toContain('<!DOCTYPE html>');
    });
  });
});
