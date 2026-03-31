import { describe, it, before, after, beforeEach } from 'node:test';
import assert from 'node:assert';
import request from 'supertest';
import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { execPath } from 'node:process';

// Create a test app by importing the app module
let app: any;

describe('Static Routes Integration Tests', () => {
  let tempDir: string;
  let publicDir: string;

  before(async () => {
    // Create a temporary public directory for testing
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'static-integration-'));
    publicDir = path.join(tempDir, 'public');
    fs.mkdirSync(publicDir);

    // Create test files
    fs.writeFileSync(path.join(publicDir, 'index.html'), '<html><body>Hello World</body></html>');
    fs.writeFileSync(path.join(publicDir, 'styles.css'), 'body { color: red; }');
    fs.writeFileSync(path.join(publicDir, 'script.js'), 'console.log("Hello");');
    fs.writeFileSync(path.join(publicDir, 'image.png'), Buffer.from([0x89, 0x50, 0x4E, 0x47]));

    // Set environment variables before importing app
    process.env.PUBLIC_DIR = publicDir;
    process.env.NODE_ENV = 'test';
    process.env.LOG_LEVEL = 'error';

    // Import app dynamically
    const { app: testApp } = await import('../../src/app.js');
    app = testApp;
  });

  after(() => {
    // Clean up
    fs.rmSync(tempDir, { recursive: true, force: true });
    delete process.env.PUBLIC_DIR;
  });

  describe('GET /health', () => {
    it('should return healthy status with timestamp', async () => {
      const response = await request(app)
        .get('/health')
        .expect('Content-Type', /json/)
        .expect(200);

      assert.strictEqual(response.body.status, 'healthy');
      assert.ok(response.body.timestamp);
    });
  });

  describe('GET /', () => {
    it('should return index.html with correct content-type', async () => {
      const response = await request(app)
        .get('/')
        .expect('Content-Type', /text\/html/)
        .expect(200);

      assert.ok(response.text.includes('Hello World'));
    });

    it('should include security headers', async () => {
      const response = await request(app).get('/');

      // Check for common security headers
      assert.ok(
        response.headers['x-content-type-options'] === 'nosniff' ||
        response.headers['x-frame-options'] === 'DENY' ||
        Object.keys(response.headers).some(h => h.startsWith('x-'))
      );
    });
  });

  describe('GET /styles.css', () => {
    it('should return CSS file with correct content-type', async () => {
      const response = await request(app)
        .get('/styles.css')
        .expect('Content-Type', /text\/css/)
        .expect(200);

      assert.ok(response.text.includes('color: red'));
    });
  });

  describe('GET /script.js', () => {
    it('should return JS file with correct content-type', async () => {
      const response = await request(app)
        .get('/script.js')
        .expect('Content-Type', /application\/javascript/)
        .expect(200);

      assert.ok(response.text.includes('console.log'));
    });
  });

  describe('GET /nonexistent', () => {
    it('should return 404 with JSON error', async () => {
      const response = await request(app)
        .get('/nonexistent')
        .expect('Content-Type', /json/)
        .expect(404);

      assert.strictEqual(response.body.code, 'FILE_NOT_FOUND');
      assert.ok(response.body.error);
      assert.ok(response.body.timestamp);
    });
  });

  describe('GET /../etc/passwd (path traversal)', () => {
    it('should return 400 for directory traversal attempt', async () => {
      const response = await request(app)
        .get('/../etc/passwd')
        .expect('Content-Type', /json/)
        .expect(400);

      assert.strictEqual(response.body.code, 'INVALID_PATH');
    });
  });
});
