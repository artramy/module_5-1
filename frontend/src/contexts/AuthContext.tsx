'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { register as apiRegister, login as apiLogin, getCurrentUser } from '@/lib/api';

// 타입 정의
interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider 컴포넌트
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // 초기화: localStorage에서 토큰 읽기
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      // 토큰으로 사용자 정보 조회
      getCurrentUser(storedToken)
        .then(setUser)
        .catch(() => {
          // 토큰이 유효하지 않으면 제거
          localStorage.removeItem('token');
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // 회원가입 함수
  const register = async (username: string, email: string, password: string) => {
    const response = await apiRegister({ username, email, password });
    const newToken = response.access_token;

    // 토큰 저장
    localStorage.setItem('token', newToken);
    setToken(newToken);

    // 사용자 정보 조회
    const userData = await getCurrentUser(newToken);
    setUser(userData);
  };

  // 로그인 함수
  const login = async (email: string, password: string) => {
    const response = await apiLogin({ email, password });
    const newToken = response.access_token;

    // 토큰 저장
    localStorage.setItem('token', newToken);
    setToken(newToken);

    // 사용자 정보 조회
    const userData = await getCurrentUser(newToken);
    setUser(userData);
  };

  // 로그아웃 함수
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// useAuth 커스텀 훅
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
