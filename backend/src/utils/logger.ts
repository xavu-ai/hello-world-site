/**
 * Simple structured logger for the static file server
 * Uses console with timestamps and log levels
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  [key: string]: unknown;
}

class Logger {
  private level: LogLevel;
  private readonly levels = ['DEBUG', 'INFO', 'WARN', 'ERROR'] as const;

  constructor() {
    const envLevel = (process.env.LOG_LEVEL || 'info').toLowerCase();
    this.level = this.parseLevel(envLevel);
  }

  private parseLevel(level: string): LogLevel {
    switch (level) {
      case 'debug': return LogLevel.DEBUG;
      case 'info': return LogLevel.INFO;
      case 'warn': return LogLevel.WARN;
      case 'error': return LogLevel.ERROR;
      default: return LogLevel.INFO;
    }
  }

  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private log(level: LogLevel, message: string, meta?: object): void {
    if (level < this.level) return;

    const entry: LogEntry = {
      timestamp: this.formatTimestamp(),
      level: this.levels[level],
      message
    };

    if (meta) {
      Object.assign(entry, meta);
    }

    const output = JSON.stringify(entry);

    switch (level) {
      case LogLevel.DEBUG:
      case LogLevel.INFO:
        console.log(output);
        break;
      case LogLevel.WARN:
        console.warn(output);
        break;
      case LogLevel.ERROR:
        console.error(output);
        break;
    }
  }

  debug(message: string, meta?: object): void {
    this.log(LogLevel.DEBUG, message, meta);
  }

  info(message: string, meta?: object): void {
    this.log(LogLevel.INFO, message, meta);
  }

  warn(message: string, meta?: object): void {
    this.log(LogLevel.WARN, message, meta);
  }

  error(message: string, meta?: object): void {
    this.log(LogLevel.ERROR, message, meta);
  }

  // Convenience methods for HTTP logging
  http(message: string, meta?: object): void {
    this.info(`[HTTP] ${message}`, meta);
  }

  // Child logger with preset metadata
  child(meta: object): Logger {
    const childLogger = new Logger();
    childLogger.level = this.level;
    return {
      debug: (msg: string, m?: object) => this.debug(msg, { ...meta, ...m }),
      info: (msg: string, m?: object) => this.info(msg, { ...meta, ...m }),
      warn: (msg: string, m?: object) => this.warn(msg, { ...meta, ...m }),
      error: (msg: string, m?: object) => this.error(msg, { ...meta, ...m }),
      http: (msg: string, m?: object) => this.http(msg, { ...meta, ...m }),
      child: (_meta: object) => childLogger.child({ ...meta, ..._meta }),
      level: childLogger.level,
      setLevel: (l: string) => childLogger.setLevel(l)
    } as unknown as Logger;
  }

  setLevel(level: string): void {
    this.level = this.parseLevel(level);
  }
}

// Export a singleton instance
const logger = new Logger();
export default logger;
export { Logger };
