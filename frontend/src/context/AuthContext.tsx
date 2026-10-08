import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'citizen' | 'admin' | 'official';
  phone_number?: string;
  state?: string;
  district?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, pass: string) => Promise<void>;
  demoLogin: (role: 'citizen' | 'admin') => Promise<void>;
  googleLogin: (credential: string) => Promise<void>;
  register: (name: string, email: string, pass: string, role?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('accessgov_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('accessgov_token'));

  useEffect(() => {
    if (user) localStorage.setItem('accessgov_user', JSON.stringify(user));
    else localStorage.removeItem('accessgov_user');
  }, [user]);

  useEffect(() => {
    if (token) localStorage.setItem('accessgov_token', token);
    else localStorage.removeItem('accessgov_token');
  }, [token]);

  const applyAuth = (data: any) => {
    if (!data?.access_token || !data?.user) {
      throw new Error('Authentication response was incomplete. Please try again.');
    }
    setToken(data.access_token);
    setUser(data.user);
  };

  const login = async (email: string, pass: string) => {
    const res = await apiClient.post('/auth/login', { email, password: pass });
    applyAuth(res.data);
  };

  const demoLogin = async (role: 'citizen' | 'admin') => {
    const res = await apiClient.post('/auth/demo-login', { role });
    applyAuth(res.data);
  };

  const googleLogin = async (credential: string) => {
    const res = await apiClient.post('/auth/google', { credential });
    applyAuth(res.data);
  };

  const register = async (name: string, email: string, pass: string, _role = 'citizen') => {
    const res = await apiClient.post('/auth/register', {
      full_name: name,
      email,
      password: pass,
      role: 'citizen',
    });
    applyAuth(res.data);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('accessgov_token');
    localStorage.removeItem('accessgov_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user && !!token, login, demoLogin, googleLogin, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
