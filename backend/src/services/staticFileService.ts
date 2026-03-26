import { stat, readFile, createReadStream } from 'node:fs';
import { promisify } from 'node:util';
import path from 'node:path';
import { FileNotFoundError, FileAccessError } from '../types/index.js';
import { validateAndResolvePath, isPathSafe } from '../utils/pathValidator.js';
import { getMimeType } from '../middleware/mimeTypes.js';

const statAsync = promisify(stat);
const readFileAsync = promisify(readFile);

export interface FileInfo {
  path: string;
  size: number;
  mimeType: string;
  lastModified: Date;
}

/**
 * Static file service for reading and serving static files
 */
export class StaticFileService {
  private publicDir: string;

  constructor(publicDir: string) {
    this.publicDir = path.resolve(publicDir);
  }

  /**
   * Get file information without reading content
   */
  async getFileInfo(requestedPath: string): Promise<FileInfo> {
    const filePath = validateAndResolvePath(requestedPath, this.publicDir);

    if (!isPathSafe(filePath)) {
      throw new FileAccessError('Invalid file path');
    }

    try {
      const stats = await statAsync(filePath);

      if (stats.isDirectory()) {
        throw new FileAccessError('Directory access not allowed');
      }

      return {
        path: filePath,
        size: stats.size,
        mimeType: getMimeType(filePath),
        lastModified: stats.mtime
      };
    } catch (err: unknown) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        throw new FileNotFoundError(`File not found: ${requestedPath}`);
      }
      if ((err as NodeJS.ErrnoException).code === 'EACCES') {
        throw new FileAccessError('Permission denied');
      }
      throw err;
    }
  }

  /**
   * Read file content as Buffer
   */
  async readFile(requestedPath: string): Promise<Buffer> {
    const filePath = validateAndResolvePath(requestedPath, this.publicDir);

    if (!isPathSafe(filePath)) {
      throw new FileAccessError('Invalid file path');
    }

    try {
      const stats = await statAsync(filePath);

      if (stats.isDirectory()) {
        throw new FileAccessError('Directory access not allowed');
      }

      return await readFileAsync(filePath);
    } catch (err: unknown) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') {
        throw new FileNotFoundError(`File not found: ${requestedPath}`);
      }
      if ((err as NodeJS.ErrnoException).code === 'EACCES') {
        throw new FileAccessError('Permission denied');
      }
      throw err;
    }
  }

  /**
   * Create a read stream for large files (memory efficient)
   */
  createReadStream(requestedPath: string): NodeJS.ReadableStream {
    const filePath = validateAndResolvePath(requestedPath, this.publicDir);

    if (!isPathSafe(filePath)) {
      throw new FileAccessError('Invalid file path');
    }

    return createReadStream(filePath);
  }

  /**
   * Check if index.html exists in the public directory
   */
  async hasIndex(): Promise<boolean> {
    try {
      const indexPath = path.join(this.publicDir, 'index.html');
      const stats = await statAsync(indexPath);
      return stats.isFile();
    } catch {
      return false;
    }
  }
}

export default StaticFileService;
