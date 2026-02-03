'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

// Dashboard 아이콘 컴포넌트 (차트 아이콘)
function DashboardIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
      />
    </svg>
  );
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const isDashboardActive = pathname === '/dashboard';

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* 로고/홈 링크 */}
          <Link
            href="/"
            className="text-2xl font-bold text-indigo-600 hover:text-indigo-700 transition"
          >
            Module 5
          </Link>

          {/* 로그인 상태별 UI */}
          <div className="flex items-center space-x-4">
            {user ? (
              // 로그인 상태
              <>
                {/* 대시보드 링크 */}
                <Link
                  href="/dashboard"
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg font-medium transition ${
                    isDashboardActive
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-700 hover:text-indigo-600 hover:bg-gray-100'
                  }`}
                >
                  <DashboardIcon className="w-5 h-5" />
                  <span className="hidden sm:inline">대시보드</span>
                </Link>
                <span className="text-gray-700 font-medium hidden sm:inline">
                  {user.username}님
                </span>
                <button
                  onClick={logout}
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                >
                  로그아웃
                </button>
              </>
            ) : (
              // 비로그인 상태
              <>
                <Link
                  href="/login"
                  className="text-gray-700 hover:text-indigo-600 font-medium transition"
                >
                  로그인
                </Link>
                <Link
                  href="/register"
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
                >
                  회원가입
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
