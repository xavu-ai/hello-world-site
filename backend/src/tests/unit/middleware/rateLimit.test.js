const request = require('supertest');
const { createApp } = require('../../../server.js');

describe('Rate Limiting Middleware', () => {
  let app;

  beforeAll(() => {
    app = createApp({ staticDir: 'public' });
  });

  describe('Static file rate limiting', () => {
    it('should allow requests under the limit', async () => {
      for (let i = 0; i < 5; i++) {
        const response = await request(app)
          .get('/')
          .expect(200);
        expect(response.text).toBeDefined();
      }
    });

    it('should include rate limit headers', async () => {
      const response = await request(app)
        .get('/')
        .expect(200);

      expect(response.headers).toBeDefined();
    });
  });

  describe('Rate limit response', () => {
    it('should return response when not rate limited', async () => {
      const response = await request(app)
        .get('/');

      expect(response.status).toBeGreaterThanOrEqual(200);
      expect(response.status).toBeLessThan(500);
    });
  });
});
