import { describe, it, beforeEach, mock } from 'node:test';
import assert from 'node:assert';
import { validateAndResolvePath, isPathSafe } from '../../src/utils/pathValidator.js';
import { InvalidPathError } from '../../src/types/index.js';

describe('pathValidator', () => {
  const publicDir = '/var/www/public';

  describe('validateAndResolvePath', () => {
    it('should resolve a valid path within public directory', () => {
      const result = validateAndResolvePath('/index.html', publicDir);
      assert.strictEqual(result, '/var/www/public/index.html');
    });

    it('should resolve a nested valid path', () => {
      const result = validateAndResolvePath('/css/styles.css', publicDir);
      assert.strictEqual(result, '/var/www/public/css/styles.css');
    });

    it('should throw InvalidPathError for directory traversal with ..', () => {
      assert.throws(
        () => validateAndResolvePath('/../../../etc/passwd', publicDir),
        InvalidPathError
      );
    });

    it('should throw InvalidPathError for partial traversal', () => {
      assert.throws(
        () => validateAndResolvePath('/../secret.txt', publicDir),
        InvalidPathError
      );
    });

    it('should throw InvalidPathError for null bytes', () => {
      assert.throws(
        () => validateAndResolvePath('/file\0.txt', publicDir),
        InvalidPathError
      );
    });

    it('should throw InvalidPathError for paths not starting with /', () => {
      assert.throws(
        () => validateAndResolvePath('file.txt', publicDir),
        InvalidPathError
      );
    });

    it('should normalize double slashes', () => {
      const result = validateAndResolvePath('//file.txt', publicDir);
      assert.strictEqual(result, '/var/www/public/file.txt');
    });

    it('should throw InvalidPathError for paths outside public directory', () => {
      assert.throws(
        () => validateAndResolvePath('/../../etc/passwd', publicDir),
        InvalidPathError
      );
    });
  });

  describe('isPathSafe', () => {
    it('should return true for normal filenames', () => {
      assert.strictEqual(isPathSafe('file.txt'), true);
      assert.strictEqual(isPathSafe('styles.css'), true);
      assert.strictEqual(isPathSafe('script.js'), true);
      assert.strictEqual(isPathSafe('image.png'), true);
    });

    it('should return false for hidden files', () => {
      assert.strictEqual(isPathSafe('.htaccess'), false);
      assert.strictEqual(isPathSafe('.env'), false);
      assert.strictEqual(isPathSafe('..hidden'), false);
    });

    it('should return false for filenames with special characters', () => {
      assert.strictEqual(isPathSafe('file<.txt'), false);
      assert.strictEqual(isPathSafe('file>.txt'), false);
      assert.strictEqual(isPathSafe('file:.txt'), false);
      assert.strictEqual(isPathSafe('file|.txt'), false);
      assert.strictEqual(isPathSafe('file?.txt'), false);
      assert.strictEqual(isPathSafe('file*.txt'), false);
    });
  });
});
