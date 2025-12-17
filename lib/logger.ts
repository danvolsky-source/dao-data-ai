import * as Sentry from '@sentry/nextjs';

// Log levels
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

// Log context interface
interface LogContext {
  [key: string]: any;
}

// Logger class
class Logger {
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
  }

  /**
   * Format log message with timestamp and level
   */
  private formatMessage(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` | Context: ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  /**
   * Log debug message (only in development)
   */
  debug(message: string, context?: LogContext): void {
    if (this.isDevelopment) {
      console.debug(this.formatMessage(LogLevel.DEBUG, message, context));
    }
  }

  /**
   * Log info message
   */
  info(message: string, context?: LogContext): void {
    const formattedMessage = this.formatMessage(LogLevel.INFO, message, context);
    console.info(formattedMessage);
    
    // Send to Sentry as breadcrumb
    Sentry.addBreadcrumb({
      message,
      level: 'info',
      data: context,
    });
  }

  /**
   * Log warning message
   */
  warn(message: string, context?: LogContext): void {
    const formattedMessage = this.formatMessage(LogLevel.WARN, message, context);
    console.warn(formattedMessage);
    
    // Send to Sentry as breadcrumb
    Sentry.addBreadcrumb({
      message,
      level: 'warning',
      data: context,
    });
  }

  /**
   * Log error message and send to Sentry
   */
  error(message: string, error?: Error, context?: LogContext): void {
    const formattedMessage = this.formatMessage(LogLevel.ERROR, message, context);
    console.error(formattedMessage, error);
    
    // Send to Sentry with full error tracking
    if (error) {
      Sentry.captureException(error, {
        contexts: {
          custom: context || {},
        },
        tags: {
          errorMessage: message,
        },
      });
    } else {
      Sentry.captureMessage(message, {
        level: 'error',
        contexts: {
          custom: context || {},
        },
      });
    }
  }

  /**
   * Log API request
   */
  logApiRequest(method: string, url: string, context?: LogContext): void {
    this.info(`API Request: ${method} ${url}`, {
      type: 'api_request',
      method,
      url,
      ...context,
    });
  }

  /**
   * Log API response
   */
  logApiResponse(method: string, url: string, status: number, duration: number, context?: LogContext): void {
    const level = status >= 400 ? LogLevel.ERROR : LogLevel.INFO;
    const message = `API Response: ${method} ${url} - ${status} (${duration}ms)`;
    
    if (level === LogLevel.ERROR) {
      this.error(message, undefined, {
        type: 'api_response',
        method,
        url,
        status,
        duration,
        ...context,
      });
    } else {
      this.info(message, {
        type: 'api_response',
        method,
        url,
        status,
        duration,
        ...context,
      });
    }
  }

  /**
   * Log user action
   */
  logUserAction(action: string, context?: LogContext): void {
    this.info(`User Action: ${action}`, {
      type: 'user_action',
      action,
      ...context,
    });
  }

  /**
   * Log performance metric
   */
  logPerformance(metric: string, value: number, unit: string = 'ms', context?: LogContext): void {
    this.info(`Performance: ${metric} = ${value}${unit}`, {
      type: 'performance',
      metric,
      value,
      unit,
      ...context,
    });
  }

  /**
   * Set user context for Sentry
   */
  setUser(userId: string, userEmail?: string, userName?: string): void {
    Sentry.setUser({
      id: userId,
      email: userEmail,
      username: userName,
    });
  }

  /**
   * Clear user context
   */
  clearUser(): void {
    Sentry.setUser(null);
  }

  /**
   * Add custom tags
   */
  setTag(key: string, value: string): void {
    Sentry.setTag(key, value);
  }

  /**
   * Add custom context
   */
  setContext(name: string, context: LogContext): void {
    Sentry.setContext(name, context);
  }
}

// Export singleton instance
export const logger = new Logger();

// Export convenience functions
export const logDebug = (message: string, context?: LogContext) => logger.debug(message, context);
export const logInfo = (message: string, context?: LogContext) => logger.info(message, context);
export const logWarn = (message: string, context?: LogContext) => logger.warn(message, context);
export const logError = (message: string, error?: Error, context?: LogContext) => logger.error(message, error, context);
export const logApiRequest = (method: string, url: string, context?: LogContext) => logger.logApiRequest(method, url, context);
export const logApiResponse = (method: string, url: string, status: number, duration: number, context?: LogContext) => logger.logApiResponse(method, url, status, duration, context);
export const logUserAction = (action: string, context?: LogContext) => logger.logUserAction(action, context);
export const logPerformance = (metric: string, value: number, unit?: string, context?: LogContext) => logger.logPerformance(metric, value, unit, context);
