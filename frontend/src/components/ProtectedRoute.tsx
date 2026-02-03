'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    // 로딩이 끝났고 사용자가 없으면 로그인 페이지로 리다이렉트
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // 로딩 중일 때 로딩 표시
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <span className="text-gray-700 font-medium">로딩 중...</span>
          </div>
        </div>
      </div>
    );
  }

  // 사용자가 없으면 null 반환 (리다이렉트 중)
  if (!user) {
    return null;
  }

  // 사용자가 있으면 children 렌더링
  return <>{children}</>;
}
