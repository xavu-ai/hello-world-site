import { jest, describe, test, expect, beforeEach, afterAll } from '@jest/globals';

describe('Config', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
    jest.resetModules();
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  test('should have correct default values', async () => {
    delete process.env.NODE_ENV;
    delete process.env.PORT;
    delete process.env.HOST;
    const config = (await import('../../src/config/config.js')).default;
    expect(config.port).toBe(3000);
    expect(config.host).toBe('0.0.0.0');
    expect(config.env).toBe('development');
    expect(config.isProduction).toBe(false);
  });

  test('should load from environment variables', async () => {
    process.env.NODE_ENV = 'production';
    process.env.PORT = '8080';
    process.env.HOST = 'localhost';
    process.env.FORCE_HTTPS = 'true';
    const config = (await import('../../src/config/config.js')).default;
    expect(config.port).toBe(8080);
    expect(config.host).toBe('localhost');
    expect(config.isProduction).toBe(true);
    expect(config.forceHttps).toBe(true);
  });

  test('should set isDevelopment correctly', async () => {
    process.env.NODE_ENV = 'development';
    const config = (await import('../../src/config/config.js')).default;
    expect(config.isDevelopment).toBe(true);
    expect(config.isProduction).toBe(false);
  });

  test('should have correct static asset maxAge values', async () => {
    const config = (await import('../../src/config/config.js')).default;
    expect(config.staticAssets.maxAge.immutable).toBe(31536000);
    expect(config.staticAssets.maxAge.html).toBe(0);
    expect(config.staticAssets.maxAge.assets).toBe(31536000);
  });
});
