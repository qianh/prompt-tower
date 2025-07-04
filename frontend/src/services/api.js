import axios from 'axios';

const API_BASE_URL = 'http://localhost:8010/api/v1';

const AUTH_API_SLUG = '../../auth'; // Relative to API_BASE_URL to reach /auth

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // 60秒超时
});

// Add a request interceptor to include the token in headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const promptAPI = {
  list: async (params) => {
    const response = await api.get('/prompts', { params });
    return response.data;
  },

  get: async (title) => {
    const response = await api.get(`/prompts/${title}`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/prompts', data);
    return response.data;
  },

  update: async (title, data) => {
    const response = await api.put(`/prompts/${title}`, data);
    return response.data;
  },

  delete: async (title) => {
    const response = await api.delete(`/prompts/${title}`);
    return response.data;
  },

  search: async (query, searchIn = ['title', 'tags', 'content']) => {
    const response = await api.post('/prompts/search', {
      query,
      search_in: searchIn,
    });
    return response.data;
  },

  toggleStatus: async (title) => {
    const response = await api.post(`/prompts/${title}/toggle-status`);
    return response.data;
  },

  incrementUsageCount: async (title) => {
    const response = await api.post(`/prompts/${title}/increment-usage`);
    return response.data;
  },
  // Removed getAllTags from promptAPI as tagAPI.list() is now the unified source
};

export const llmAPI = {
  optimize: async (content, context = null, provider = 'gemini') => {
    const response = await api.post('/llm/optimize', {
      content,
      context,
      llm_provider: provider,
    });
    return response.data;
  },

  getProviders: async () => {
    const response = await api.get('/llm/providers');
    return response.data;
  },
};

export const authAPI = {
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post(`${AUTH_API_SLUG}/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
    }
    return response.data;
  },

  signup: async (username, password) => {
    const response = await api.post(`${AUTH_API_SLUG}/signup`, { username, password });
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('authToken');
  },

  getCurrentUser: async () => {
    const response = await api.get(`${AUTH_API_SLUG}/users/me`);
    return response.data;
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('authToken');
  },
};

export const tagAPI = {
  list: async () => {
    const response = await api.get('/tags'); 
    return response.data; // Expected to be List[str]
  },

  create: async (tagData) => { // tagData should be { name: "new_tag_name" }
    const response = await api.post('/tags', tagData); // Backend expects { "name": "..." }
    return response.data; // Expected to be List[str] (updated list of all tags)
  },
};

export const userAPI = {
  list: async () => {
    const response = await api.get('/users/');
    return response.data;
  },

  getByUsername: async (username) => {
    const response = await api.get(`/users/${username}/`);
    return response.data;
  },
};