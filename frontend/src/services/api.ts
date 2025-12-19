// LimeStar API Service

import type { Link, LinkListResponse, TagWithCount, CategoryWithTags, LoginResponse, VerifyResponse } from '../types';

const API_BASE = '/api';

// Generic fetch wrapper
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

// Links API
export const linksAPI = {
  getAll: (params?: {
    page?: number;
    page_size?: number;
    tag?: string;
  }): Promise<LinkListResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.page_size) searchParams.set('page_size', String(params.page_size));
    if (params?.tag) searchParams.set('tag', params.tag);

    const query = searchParams.toString();
    return fetchAPI<LinkListResponse>(`/links${query ? `?${query}` : ''}`);
  },

  getOne: (id: number): Promise<Link> => {
    return fetchAPI<Link>(`/links/${id}`);
  },

  create: (data: { url: string; user_note?: string }): Promise<Link> => {
    return fetchAPI<Link>('/links', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: (
    id: number,
    data: { title?: string; description?: string; user_note?: string; tag_ids?: number[] }
  ): Promise<Link> => {
    return fetchAPI<Link>(`/links/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  delete: (id: number): Promise<void> => {
    return fetchAPI<void>(`/links/${id}`, { method: 'DELETE' });
  },
};

// Tags API
export const tagsAPI = {
  getAll: (): Promise<TagWithCount[]> => {
    return fetchAPI<TagWithCount[]>('/tags');
  },

  getCategories: (): Promise<CategoryWithTags[]> => {
    return fetchAPI<CategoryWithTags[]>('/tags/categories');
  },

  create: (data: { name: string; color?: string }): Promise<TagWithCount> => {
    return fetchAPI<TagWithCount>('/tags', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// Search API
export const searchAPI = {
  search: (params: {
    q?: string;
    tags?: string[];
    page?: number;
    page_size?: number;
  }): Promise<LinkListResponse> => {
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.set('q', params.q);
    if (params.tags?.length) {
      params.tags.forEach((tag) => searchParams.append('tags', tag));
    }
    if (params.page) searchParams.set('page', String(params.page));
    if (params.page_size) searchParams.set('page_size', String(params.page_size));

    return fetchAPI<LinkListResponse>(`/search?${searchParams.toString()}`);
  },
};

// Auth API
export const authAPI = {
  login: (password: string): Promise<LoginResponse> => {
    return fetchAPI<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ password }),
    });
  },

  verify: (token: string): Promise<VerifyResponse> => {
    return fetchAPI<VerifyResponse>('/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },

  logout: (token: string): Promise<{ success: boolean }> => {
    return fetchAPI<{ success: boolean }>('/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },
};
