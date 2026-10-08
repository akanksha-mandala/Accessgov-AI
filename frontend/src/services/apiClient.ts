import axios from 'axios';

// Vite proxies /api to FastAPI in development. A relative base URL keeps
// browser requests same-origin and avoids localhost/127.0.0.1 CORS issues.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) || '/api/v1';

export const apiClient = axios.create({ baseURL: API_BASE_URL, timeout: 20000 });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessgov_token');
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessgov_token');
      localStorage.removeItem('accessgov_user');
    }
    return Promise.reject(error);
  }
);
