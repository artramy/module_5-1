'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface HealthStatus {
  status: string;
  message: string;
}

export default function Home() {
  const { user } = useAuth();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => {
        setHealth({ status: 'error', message: '백엔드 연결 실패' });
        setLoading(false);
      });
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4">
        {/* 로그인 상태별 환영 메시지 */}
        {user ? (
          <div className="mb-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <h2 className="text-xl font-bold text-indigo-800 mb-1">
              환영합니다! 🎉
            </h2>
            <p className="text-indigo-600">
              <span className="font-semibold">{user.username}</span>님, 로그인되었습니다.
            </p>
          </div>
        ) : (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-gray-600 text-center">
              로그인하여 더 많은 기능을 이용하세요
            </p>
          </div>
        )}

        <h1 className="text-3xl font-bold text-gray-800 text-center mb-6">
          Module 5
        </h1>
        <p className="text-gray-600 text-center mb-8">
          Next.js + FastAPI + SQLite
        </p>

        <div className="border-t pt-6">
          <h2 className="text-lg font-semibold text-gray-700 mb-3">
            백엔드 상태
          </h2>
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <div
              className={`p-4 rounded-lg ${
                health?.status === 'ok'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-700'
              }`}
            >
              <p className="font-medium">
                {health?.status === 'ok' ? '연결됨' : '연결 실패'}
              </p>
              <p className="text-sm mt-1">{health?.message}</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
