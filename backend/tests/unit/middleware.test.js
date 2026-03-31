import { errorHandler, notFoundHandler, NotFoundError, InternalServerError } from '../../src/middleware/errorHandler.js';
import { applySecurityHeaders, applyCachingHeaders } from '../../src/middleware/securityHeaders.js';
import express from 'express';

const { jest } = await import('@jest/globals');

describe('Error Handler Middleware', () => {
  let mockReq;
  let mockRes;
  let mockNext;

  beforeEach(() => {
    mockReq = { path: '/test', method: 'GET' };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    mockNext = jest.fn();
  });

  test('NotFoundError should return 404', () => {
    const error = new NotFoundError('Page not found');
    errorHandler(error, mockReq, mockRes, mockNext);
    expect(mockRes.status).toHaveBeenCalledWith(404);
    expect(mockRes.json).toHaveBeenCalledWith({
      error: 'NotFoundError',
      message: 'Page not found'
    });
  });

  test('InternalServerError should return 500', () => {
    const error = new InternalServerError('Something went wrong');
    errorHandler(error, mockReq, mockRes, mockNext);
    expect(mockRes.status).toHaveBeenCalledWith(500);
    expect(mockRes.json).toHaveBeenCalledWith({
      error: 'InternalServerError',
      message: 'Something went wrong'
    });
  });

  test('notFoundHandler should return 404 with method and path', () => {
    notFoundHandler(mockReq, mockRes);
    expect(mockRes.status).toHaveBeenCalledWith(404);
    expect(mockRes.json).toHaveBeenCalledWith({
      error: 'NotFoundError',
      message: 'Cannot GET /test'
    });
  });
});

describe('Security Headers Middleware', () => {
  test('applySecurityHeaders should add helmet middleware', () => {
    const app = express();
    expect(() => applySecurityHeaders(app)).not.toThrow();
  });

  test('applyCachingHeaders should add caching middleware', () => {
    const app = express();
    expect(() => applyCachingHeaders(app)).not.toThrow();
  });
});
