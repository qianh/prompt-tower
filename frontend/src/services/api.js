import axios from 'axios';

const API_BASE_URL = 'http://localhost:8010/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,  // 60秒超时
});

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
