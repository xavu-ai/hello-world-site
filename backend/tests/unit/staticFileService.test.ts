import { describe, it, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert';
import { StaticFileService } from '../../src/services/staticFileService.ts';
import { FileNotFoundError, FileAccessError } from '../../src/types/index.ts';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

describe('staticFileService', () => {
  let tempDir: string;
  let service: StaticFileService;

  beforeEach(() => {
    // Create a temporary directory for testing
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'static-test-'));
    service = new StaticFileService(tempDir);
  });

  afterEach(() => {
    // Clean up temp directory
    fs.rmSync(tempDir, { recursive: true, force: true });
  });

  describe('getFileInfo', () => {
    it('should return file info for existing file', async () => {
      const testFile = path.join(tempDir, 'test.txt');
      fs.writeFileSync(testFile, 'Hello World');
      const stat = fs.statSync(testFile);

      const info = await service.getFileInfo('/test.txt');

      assert.strictEqual(info.path, testFile);
      assert.strictEqual(info.size, 11);
      assert.strictEqual(info.mimeType, 'text/plain; charset=utf-8');
    });

    it('should throw FileNotFoundError for non-existent file', async () => {
      await assert.rejects(
        () => service.getFileInfo('/nonexistent.txt'),
        FileNotFoundError
      );
    });

    it('should throw FileAccessError when trying to access directory', async () => {
      const subDir = path.join(tempDir, 'subdir');
      fs.mkdirSync(subDir);

      await assert.rejects(
        () => service.getFileInfo('/subdir'),
        FileAccessError
      );
    });

    it('should throw FileAccessError for path traversal attempt', async () => {
      await assert.rejects(
        () => service.getFileInfo('/../etc/passwd'),
        FileAccessError
      );
    });

    it('should reject hidden files', async () => {
      const hiddenFile = path.join(tempDir, '.hidden');
      fs.writeFileSync(hiddenFile, 'hidden content');

      await assert.rejects(
        () => service.getFileInfo('/.hidden'),
        FileAccessError
      );
    });
  });

  describe('readFile', () => {
    it('should read file content as buffer', async () => {
      const testFile = path.join(tempDir, 'test.txt');
      fs.writeFileSync(testFile, 'Hello World');

      const content = await service.readFile('/test.txt');

      assert.strictEqual(content.toString(), 'Hello World');
    });

    it('should throw FileNotFoundError for non-existent file', async () => {
      await assert.rejects(
        () => service.readFile('/nonexistent.txt'),
        FileNotFoundError
      );
    });
  });

  describe('createReadStream', () => {
    it('should create a readable stream for existing file', () => {
      const testFile = path.join(tempDir, 'test.txt');
      fs.writeFileSync(testFile, 'Hello World');

      const stream = service.createReadStream('/test.txt');

      assert.strictEqual(stream.readable, true);
    });

    it('should throw FileNotFoundError for non-existent file', () => {
      assert.throws(
        () => service.createReadStream('/nonexistent.txt'),
        FileNotFoundError
      );
    });
  });

  describe('hasIndex', () => {
    it('should return true when index.html exists', async () => {
      const indexFile = path.join(tempDir, 'index.html');
      fs.writeFileSync(indexFile, '<html></html>');

      const hasIndex = await service.hasIndex();

      assert.strictEqual(hasIndex, true);
    });

    it('should return false when index.html does not exist', async () => {
      const hasIndex = await service.hasIndex();

      assert.strictEqual(hasIndex, false);
    });
  });
});
