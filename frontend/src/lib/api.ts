import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// Environment configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  traceId?: string;
}

export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  xsrfCookieName: 'XSRF-TOKEN',
  xsrfHeaderName: 'X-XSRF-TOKEN',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds timeout for AI operations
});

// Auth Interceptor: No longer injects Authorization header from localStorage, relies on HttpOnly cookies
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response & Error Interceptor: Standardize error formats
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    let standardizedError: ApiResponse = {
      success: false,
      message: 'Network request failed',
      error: error.message,
    };

    if (error.response) {
      const responseData = error.response.data as { message?: string; detail?: any; error?: string; traceId?: string } | undefined;
      
      // If backend returned our standard exception response structure or FastAPI detail structure
      if (responseData && typeof responseData === 'object') {
        let errorMsg = responseData.message;
        if (!errorMsg && responseData.detail) {
          if (typeof responseData.detail === 'string') {
            errorMsg = responseData.detail;
          } else if (Array.isArray(responseData.detail)) {
            // Parse FastAPI validation errors list
            errorMsg = responseData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
          } else {
            errorMsg = JSON.stringify(responseData.detail);
          }
        }
        
        standardizedError = {
          success: false,
          message: errorMsg || 'An error occurred',
          error: responseData.error || error.message,
          traceId: responseData.traceId,
        };
      } else {
        standardizedError = {
          success: false,
          message: `Request failed with status ${error.response.status}`,
          error: error.response.statusText || error.message,
        };
      }
      
      // Global 401 Unauthorized handling
      if (error.response.status === 401 && typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        // Let component level handlers or router handle redirect if needed
      }
    } else if (error.request) {
      standardizedError = {
        success: false,
        message: 'No response received from the server. Check backend status.',
        error: error.message,
      };
    }

    return Promise.reject(standardizedError);
  }
);

// Typed API Helpers
export const apiService = {
  get: async <T>(url: string): Promise<T> => {
    const response = await api.get<T>(url);
    return response.data;
  },
  post: async <T>(url: string, data?: unknown): Promise<T> => {
    const response = await api.post<T>(url, data);
    return response.data;
  },
  put: async <T>(url: string, data?: unknown): Promise<T> => {
    const response = await api.put<T>(url, data);
    return response.data;
  },
  delete: async <T>(url: string): Promise<T> => {
    const response = await api.delete<T>(url);
    return response.data;
  },
};

// Health Check API
export interface HealthStatus {
  status: string;
  version: string;
}

export const checkBackendHealth = async (): Promise<HealthStatus> => {
  return apiService.get<HealthStatus>('/health');
};
