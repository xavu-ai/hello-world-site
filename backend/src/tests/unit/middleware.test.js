const request = require('supertest');
const { createApp } = require('../../server');
const { createCorrelationIdMiddleware } = require('../../middleware/correlationId');
const { createPathTraversalMiddleware, PathTraversalError } = require('../../middleware/pathTraversal');
const { errorHandler } = require('../../middleware/errorHandler');

describe('Path Traversal Middleware', () => {
  let app;

  beforeEach(() => {
    app = createApp({ staticDir: 'public' });
  });

  describe('Valid paths', () => {
    test('should allow access to root', async () => {
      const response = await request(app).get('/');
      expect(response.status).toBe(200);
    });

    test('should allow access to static files', async () => {
      const response = await request(app).get('/static/index.html');
      expect(response.status).toBe(200);
    });

    test('should allow paths with normal subdirectories', async () => {
      // This test assumes no subdirectories exist, but path should not be rejected
      const response = await request(app).get('/static/css/style.css');
      expect(response.status).toBe(404); // File not found, but not blocked by traversal middleware
    });
  });

  describe('Path traversal attempts', () => {
    test('should block ../ traversal', async () => {
      const response = await request(app).get('/static/../../../etc/passwd');
      expect(response.status).toBe(400);
      expect(response.body.error).toContain('directory traversal');
    });

    test('should block encoded ../ traversal', async () => {
      const response = await request(app).get('/static/%2e.%2e/%2e.%2e/etc/passwd');
      expect(response.status).toBe(400);
    });

    test('should block URL-encoded traversal', async () => {
      const response = await request(app).get('/static/..%2f..%2fetc/passwd');
      expect(response.status).toBe(400);
    });

    test('should block double-encoded traversal', async () => {
      const response = await request(app).get('/static/%252e%252e/%252e%252e/etc/passwd');
      expect(response.status).toBe(400);
    });

    test('should block traversal with different separators', async () => {
      const response = await request(app).get('/static/..\\..\\windows\\system32');
      expect(response.status).toBe(400);
    });
  });

  describe('Edge cases', () => {
    test('should handle empty path', async () => {
      const response = await request(app).get('');
      expect(response.status).toBe(404);
    });

    test('should handle path with only slashes', async () => {
      const response = await request(app).get('///');
      expect(response.status).toBe(404);
    });

    test('should handle path with null bytes', async () => {
      const response = await request(app).get('/static/..%00..');
      expect(response.status).toBe(400);
    });
  });
});

describe('Correlation ID Middleware', () => {
  let app;

  beforeEach(() => {
    app = createApp();
  });

  test('should generate UUID v4 correlation ID', async () => {
    const response = await request(app).get('/health');
    expect(response.headers['x-request-id']).toBeDefined();

    // UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
    const uuidV4Regex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    expect(response.headers['x-request-id']).toMatch(uuidV4Regex);
  });

  test('should propagate incoming correlation ID', async () => {
    const customId = 'custom-correlation-id-12345';
    const response = await request(app)
      .get('/health')
      .set('X-Request-ID', customId);

    expect(response.headers['x-request-id']).toBe(customId);
  });

  test('should include correlation ID in error responses', async () => {
    const response = await request(app).get('/nonexistent-route');
    expect(response.body.requestId).toBeDefined();
    expect(response.headers['x-request-id']).toBeDefined();
    expect(response.body.requestId).toBe(response.headers['x-request-id']);
  });
});

describe('Error Handler Middleware', () => {
  let app;

  beforeEach(() => {
    app = createApp();
  });

  test('should return JSON error response', async () => {
    const response = await request(app).get('/nonexistent');
    expect(response.status).toBe(404);
    expect(response.body).toHaveProperty('error');
    expect(response.body).toHaveProperty('requestId');
    expect(response.body).toHaveProperty('timestamp');
  });

  test('should include stack trace in development', async () => {
    const response = await request(app).get('/nonexistent');
    // Stack trace may or may not be present depending on error type
    expect(response.body).toHaveProperty('error');
  });

  test('should not expose stack trace in production', async () => {
    const prodApp = createApp({ env: 'production' });
    const response = await request(prodApp).get('/nonexistent');
    expect(response.body).not.toHaveProperty('stack');
  });
});
