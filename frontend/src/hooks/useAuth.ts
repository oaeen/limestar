import { useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

const AUTH_TOKEN_KEY = 'limestar_auth_token';

interface UseAuthResult {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (password: string) => Promise<{ success: boolean; message: string }>;
  logout: () => void;
}

export function useAuth(): UseAuthResult {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // 初始化时检查本地存储的 token
  useEffect(() => {
    const verifyStoredToken = async () => {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (token) {
        try {
          const { valid } = await authAPI.verify(token);
          setIsAuthenticated(valid);
          if (!valid) {
            localStorage.removeItem(AUTH_TOKEN_KEY);
          }
        } catch {
          localStorage.removeItem(AUTH_TOKEN_KEY);
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };
    verifyStoredToken();
  }, []);

  const login = useCallback(async (password: string) => {
    try {
      const response = await authAPI.login(password);
      if (response.success && response.token) {
        localStorage.setItem(AUTH_TOKEN_KEY, response.token);
        setIsAuthenticated(true);
        return { success: true, message: response.message };
      }
      return { success: false, message: response.message };
    } catch {
      return { success: false, message: '登录失败，请重试' };
    }
  }, []);

  const logout = useCallback(() => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      authAPI.logout(token).catch(() => {});
      localStorage.removeItem(AUTH_TOKEN_KEY);
    }
    setIsAuthenticated(false);
  }, []);

  return { isAuthenticated, isLoading, login, logout };
}
