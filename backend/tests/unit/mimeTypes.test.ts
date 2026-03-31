import { describe, it } from 'node:test';
import assert from 'node:assert';
import { getMimeType, isTextBasedMimeType } from '../../src/middleware/mimeTypes.ts';

describe('mimeTypes', () => {
  describe('getMimeType', () => {
    it('should return correct MIME type for HTML', () => {
      assert.strictEqual(getMimeType('index.html'), 'text/html; charset=utf-8');
    });

    it('should return correct MIME type for CSS', () => {
      assert.strictEqual(getMimeType('styles.css'), 'text/css; charset=utf-8');
    });

    it('should return correct MIME type for JavaScript', () => {
      assert.strictEqual(getMimeType('script.ts'), 'application/javascript; charset=utf-8');
    });

    it('should return correct MIME type for JSON', () => {
      assert.strictEqual(getMimeType('data.json'), 'application/json');
    });

    it('should return correct MIME type for PNG images', () => {
      assert.strictEqual(getMimeType('image.png'), 'image/png');
    });

    it('should return correct MIME type for JPEG images', () => {
      assert.strictEqual(getMimeType('photo.jpg'), 'image/jpeg');
      assert.strictEqual(getMimeType('photo.jpeg'), 'image/jpeg');
    });

    it('should return correct MIME type for SVG', () => {
      assert.strictEqual(getMimeType('icon.svg'), 'image/svg+xml');
    });

    it('should return correct MIME type for fonts', () => {
      assert.strictEqual(getMimeType('font.woff'), 'font/woff');
      assert.strictEqual(getMimeType('font.woff2'), 'font/woff2');
    });

    it('should return correct MIME type for unknown extensions', () => {
      assert.strictEqual(getMimeType('file.unknown'), 'application/octet-stream');
      assert.strictEqual(getMimeType('file.noextension'), 'application/octet-stream');
    });

    it('should handle uppercase extensions', () => {
      assert.strictEqual(getMimeType('file.HTML'), 'text/html; charset=utf-8');
      assert.strictEqual(getMimeType('file.CSS'), 'text/css; charset=utf-8');
    });
  });

  describe('isTextBasedMimeType', () => {
    it('should return true for text-based MIME types', () => {
      assert.strictEqual(isTextBasedMimeType('text/html'), true);
      assert.strictEqual(isTextBasedMimeType('text/css'), true);
      assert.strictEqual(isTextBasedMimeType('text/plain'), true);
      assert.strictEqual(isTextBasedMimeType('application/javascript'), true);
      assert.strictEqual(isTextBasedMimeType('application/json'), true);
    });

    it('should return false for binary MIME types', () => {
      assert.strictEqual(isTextBasedMimeType('image/png'), false);
      assert.strictEqual(isTextBasedMimeType('image/jpeg'), false);
      assert.strictEqual(isTextBasedMimeType('application/pdf'), false);
      assert.strictEqual(isTextBasedMimeType('video/mp4'), false);
    });
  });
});
