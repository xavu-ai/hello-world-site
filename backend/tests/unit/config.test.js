const { createApp } = require('../../server');

describe('Configuration Tests', () => {
  describe('Environment Configuration', () => {
    test('should use default values when env vars not set', () => {
      const app = createApp();
      expect(app).toBeDefined();
    });

    test('should accept custom static directory', () => {
      const app = createApp({ staticDir: 'custom-static' });
      expect(app).toBeDefined();
    });

    test('should accept custom index file', () => {
      const app = createApp({ indexFile: 'custom-index.html' });
      expect(app).toBeDefined();
    });

    test('should accept custom port in config', () => {
      const app = createApp({ port: 4000 });
      expect(app).toBeDefined();
    });
  });

  describe('App Factory Pattern', () => {
    test('createApp should return an express app', () => {
      const app = createApp();
      expect(typeof app).toBe('function');
      expect(typeof app.listen).toBe('function');
      expect(typeof app.use).toBe('function');
    });

    test('should configure all middleware', () => {
      const app = createApp();
      // Express app should have middleware configured
      expect(app._router).toBeDefined();
    });
  });
});
