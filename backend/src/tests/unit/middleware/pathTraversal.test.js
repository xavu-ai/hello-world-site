const request = require('supertest');
const { createApp } = require('../../../server.js');

describe('Path Traversal Middleware', () => {
  let app;

  beforeEach(() => {
    app = createApp({ staticDir: 'public' });
  });

  describe('Blocking path traversal attempts', () => {
    it('should return 403 for /../etc/passwd', async () => {
      const response = await request(app)
        .get('/../etc/passwd')
        .expect(403);

      expect(response.body.error).toBeDefined();
      expect(response.body.correlationId).toBeDefined();
    });

    it('should return 403 for /../../etc/passwd', async () => {
      const response = await request(app)
        .get('/../../etc/passwd')
        .expect(403);

      expect(response.body.error).toContain('traversal');
    });

    it('should return 403 for encoded traversal /%2e%2e/%2e%2e/etc/passwd', async () => {
      const response = await request(app)
        .get('/%2e%2e/%2e%2e/etc/passwd')
        .expect(403);

      expect(response.body.error).toBeDefined();
    });

    it('should return 403 for double-encoded traversal /%252e%252e/%252e%252e/etc/passwd', async () => {
      const response = await request(app)
        .get('/%252e%252e/%252e%252e/etc/passwd')
        .expect(403);

      expect(response.body.error).toBeDefined();
    });

    it('should return 403 for /%2e%2e/etc/passwd', async () => {
      const response = await request(app)
        .get('/%2e%2e/etc/passwd')
        .expect(403);

      expect(response.body.error).toBeDefined();
    });
  });

  describe('Allowing valid paths', () => {
    it('should return 200 for /index.html', async () => {
      const response = await request(app)
        .get('/index.html')
        .expect(200);

      expect(response.text).toBeDefined();
    });

    it('should return 200 for /css/styles.css', async () => {
      const response = await request(app)
        .get('/css/styles.css')
        .expect(200);

      expect(response.text).toBeDefined();
    });

    it('should return 200 for /static/index.html', async () => {
      const response = await request(app)
        .get('/static/index.html')
        .expect(200);

      expect(response.text).toBeDefined();
    });
  });
});
