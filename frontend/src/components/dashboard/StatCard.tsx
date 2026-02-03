'use client';

import { ReactNode } from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  trend?: string;
  loading?: boolean;
}

export default function StatCard({ title, value, icon, trend, loading = false }: StatCardProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-24 mb-3"></div>
            <div className="h-8 bg-gray-200 rounded w-16"></div>
          </div>
          {icon && <div className="h-12 w-12 bg-gray-200 rounded-full"></div>}
        </div>
        {trend && <div className="h-4 bg-gray-200 rounded w-12 mt-3"></div>}
      </div>
    );
  }

  // Determine trend color
  const getTrendColor = (trend: string): string => {
    if (trend.startsWith('+')) return 'text-green-600';
    if (trend.startsWith('-')) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-all duration-200">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        {icon && (
          <div className="flex-shrink-0 p-3 bg-blue-50 rounded-full text-blue-600">{icon}</div>
        )}
      </div>
      {trend && (
        <div className="mt-3">
          <span className={`text-sm font-medium ${getTrendColor(trend)}`}>{trend}</span>
          <span className="text-sm text-gray-500 ml-1">from last period</span>
        </div>
      )}
    </div>
  );
}
