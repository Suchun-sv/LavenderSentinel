/**
 * Export all types
 */

export * from './paper';
export * from './search';
export * from './chat';

// Common types
export interface ApiError {
  error: string;
  details?: Record<string, unknown>;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
}

