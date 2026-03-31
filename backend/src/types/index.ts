// Custom error classes for the static file server

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly code: string;
  public readonly timestamp: string;

  constructor(message: string, statusCode: number, code: string) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.timestamp = new Date().toISOString();
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON(): object {
    return {
      error: this.message,
      code: this.code,
      timestamp: this.timestamp
    };
  }
}

export class FileNotFoundError extends AppError {
  constructor(message = 'File not found') {
    super(message, 404, 'FILE_NOT_FOUND');
  }
}

export class InvalidPathError extends AppError {
  constructor(message = 'Invalid path') {
    super(message, 400, 'INVALID_PATH');
  }
}

export class FileAccessError extends AppError {
  constructor(message = 'File access denied') {
    super(message, 403, 'FILE_ACCESS_DENIED');
  }
}

export class ServerError extends AppError {
  constructor(message = 'Internal server error') {
    super(message, 500, 'SERVER_ERROR');
  }
}

// Express route handler type for async routes
export type AsyncRequestHandler = (
  req: import('express').Request,
  res: import('express').Response,
  next: import('express').NextFunction
) => Promise<void>;
