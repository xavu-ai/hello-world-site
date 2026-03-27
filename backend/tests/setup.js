// Jest setup file for backend tests

// Set test environment
process.env.NODE_ENV = 'test';
process.env.PORT = '3000';
process.env.STATIC_DIR = 'public';
process.env.INDEX_FILE = 'index.html';

// Increase timeout for integration tests
jest.setTimeout(30000);

// Global teardown if needed
afterAll(() => {
  // Clean up any open handles
});
