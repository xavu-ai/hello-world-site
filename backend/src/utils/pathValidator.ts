import path from 'node:path';
import { InvalidPathError } from '../types/index.js';

/**
 * Validates and resolves a requested path against the public directory
 * to prevent directory traversal attacks.
 *
 * @param requestedPath - The path requested by the client
 * @param publicDir - The public directory base path
 * @returns The resolved absolute path
 * @throws InvalidPathError if the path is invalid or traverses outside public dir
 */
export function validateAndResolvePath(requestedPath: string, publicDir: string): string {
  // Check for null bytes (null byte injection attack)
  if (requestedPath.includes('\0')) {
    throw new InvalidPathError('Invalid path: null bytes not allowed');
  }

  // Check for directory traversal attempts
  if (requestedPath.includes('..')) {
    throw new InvalidPathError('Invalid path: directory traversal not allowed');
  }

  // Ensure the path starts with a forward slash
  if (!requestedPath.startsWith('/')) {
    throw new InvalidPathError('Invalid path: must start with /');
  }

  // Remove double slashes
  const normalizedPath = requestedPath.replace(/\/+/g, '/');

  // Resolve the full path
  const fullPath = path.resolve(publicDir, normalizedPath.slice(1));

  // Verify the resolved path is within the public directory
  const resolvedPublicDir = path.resolve(publicDir);

  if (!fullPath.startsWith(resolvedPublicDir + path.sep) && fullPath !== resolvedPublicDir) {
    throw new InvalidPathError('Invalid path: access outside public directory not allowed');
  }

  return fullPath;
}

/**
 * Check if a path is safe for serving (not a directory, not a hidden file)
 * @param filePath - The file path to check
 * @returns True if the path is safe to serve
 */
export function isPathSafe(filePath: string): boolean {
  const basename = path.basename(filePath);

  // Reject hidden files (starting with .)
  if (basename.startsWith('.')) {
    return false;
  }

  // Reject paths with special characters that could be problematic
  if (/[<>:"|?*]/.test(basename)) {
    return false;
  }

  return true;
}

export default { validateAndResolvePath, isPathSafe };
