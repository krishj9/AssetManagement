/**
 * API Client for Portfolio Platform Backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add correlation IDs
apiClient.interceptors.request.use(
  (config) => {
    // Generate request_id if not present
    if (!config.headers['X-Request-ID']) {
      config.headers['X-Request-ID'] = crypto.randomUUID();
    }
    
    // Add trace_id if available in session
    const traceId = sessionStorage.getItem('trace_id');
    if (traceId) {
      config.headers['X-Trace-ID'] = traceId;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => {
    // Store trace_id from response if present
    const traceId = response.headers['x-trace-id'];
    if (traceId) {
      sessionStorage.setItem('trace_id', traceId);
    }
    
    return response;
  },
  (error: AxiosError) => {
    // Handle structured errors from backend
    if (error.response?.data) {
      const errorData = error.response.data as {
        code?: string;
        message?: string;
        severity?: string;
        retryable?: boolean;
      };
      
      console.error('API Error:', {
        code: errorData.code,
        message: errorData.message,
        severity: errorData.severity,
        retryable: errorData.retryable,
      });
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;

// Helper function to handle API errors
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const errorData = error.response?.data as {
      message?: string;
      code?: string;
    };
    
    return errorData?.message || error.message || 'An unexpected error occurred';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};
