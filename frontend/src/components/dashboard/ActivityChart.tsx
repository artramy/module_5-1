'use client';

import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { format, parseISO, isValid } from 'date-fns';

type ChartViewMode = 'byDate' | 'byType';

interface ActivityChartProps {
  data: Record<string, number>;
  viewMode: ChartViewMode;
  loading?: boolean;
}

interface ChartDataItem {
  name: string;
  value: number;
  fullDate?: string;
}

export default function ActivityChart({ data, viewMode, loading = false }: ActivityChartProps) {
  // Transform data for recharts
  const chartData = useMemo((): ChartDataItem[] => {
    if (!data || Object.keys(data).length === 0) return [];

    return Object.entries(data)
      .map(([key, value]) => {
        if (viewMode === 'byDate') {
          // Try to parse date and format it nicely
          try {
            const date = parseISO(key);
            if (isValid(date)) {
              return {
                name: format(date, 'MMM d'),
                value,
                fullDate: format(date, 'MMMM d, yyyy'),
              };
            }
          } catch {
            // If parsing fails, use the key as is
          }
        }
        return {
          name: key,
          value,
        };
      })
      .sort((a, b) => {
        // Sort by date for byDate view
        if (viewMode === 'byDate' && a.fullDate && b.fullDate) {
          return new Date(a.fullDate).getTime() - new Date(b.fullDate).getTime();
        }
        // Sort by value descending for byType view
        if (viewMode === 'byType') {
          return b.value - a.value;
        }
        return 0;
      });
  }, [data, viewMode]);

  // Loading state
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="h-4 bg-gray-200 rounded w-32 mb-4 animate-pulse"></div>
        <div className="h-64 bg-gray-100 rounded animate-pulse flex items-center justify-center">
          <div className="text-gray-400">Loading chart...</div>
        </div>
      </div>
    );
  }

  // Empty state
  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Activity {viewMode === 'byDate' ? 'Over Time' : 'by Type'}
        </h3>
        <div className="h-64 bg-gray-50 rounded flex items-center justify-center">
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <p className="mt-2 text-sm text-gray-500">No activity data available</p>
          </div>
        </div>
      </div>
    );
  }

  // Custom tooltip component
  const CustomTooltip = ({
    active,
    payload,
    label,
  }: {
    active?: boolean;
    payload?: Array<{ value: number; payload: ChartDataItem }>;
    label?: string;
  }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-medium text-gray-900">
            {item.fullDate || label}
          </p>
          <p className="text-sm text-blue-600">
            {payload[0].value} {payload[0].value === 1 ? 'activity' : 'activities'}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">
        Activity {viewMode === 'byDate' ? 'Over Time' : 'by Type'}
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          {viewMode === 'byDate' ? (
            <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={{ stroke: '#e5e7eb' }}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: '#2563eb' }}
              />
            </LineChart>
          ) : (
            <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="name"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#6b7280' }}
                tickLine={false}
                axisLine={{ stroke: '#e5e7eb' }}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey="value"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
                maxBarSize={60}
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
