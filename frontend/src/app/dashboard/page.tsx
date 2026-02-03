'use client';

import { useState, useMemo } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useDashboard } from '@/hooks/useDashboard';
import StatCard from '@/components/dashboard/StatCard';
import ActivityChart from '@/components/dashboard/ActivityChart';
import ActivityList from '@/components/dashboard/ActivityList';
import ActivityDetail from '@/components/dashboard/ActivityDetail';
import { Activity } from '@/lib/api';

// Icons for stat cards
const TotalActivitiesIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
    />
  </svg>
);

const TodayActivitiesIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
    />
  </svg>
);

const MostCommonIcon = () => (
  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
    />
  </svg>
);

type ChartView = 'byDate' | 'byType';

function DashboardContent() {
  const {
    activities,
    activitiesLoading,
    activitiesError,
    stats,
    statsLoading,
    statsError,
    hasMore,
    deleteActivity,
    refreshData,
    loadMore,
  } = useDashboard();

  const [chartView, setChartView] = useState<ChartView>('byDate');
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  // Calculate today's activities from stats
  const todayActivities = useMemo(() => {
    if (!stats?.by_date) return 0;
    const today = new Date().toISOString().split('T')[0];
    return stats.by_date[today] || 0;
  }, [stats]);

  // Handle delete from list (with confirmation)
  const handleDeleteFromList = (id: number) => {
    setDeleteConfirmId(id);
  };

  // Confirm delete
  const confirmDelete = async () => {
    if (deleteConfirmId !== null) {
      await deleteActivity(deleteConfirmId);
      setDeleteConfirmId(null);
    }
  };

  // Handle delete from detail modal
  const handleDeleteFromDetail = async (id: number): Promise<boolean> => {
    return await deleteActivity(id);
  };

  // Error display component
  const ErrorDisplay = ({ message, onRetry }: { message: string; onRetry: () => void }) => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center">
        <svg
          className="h-5 w-5 text-red-400 mr-2"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <span className="text-sm text-red-700">{message}</span>
      </div>
      <button
        onClick={onRetry}
        className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
      >
        Try again
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <button
              onClick={refreshData}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-150"
            >
              <svg
                className="h-4 w-4 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Error */}
        {statsError && (
          <div className="mb-6">
            <ErrorDisplay message={statsError} onRetry={refreshData} />
          </div>
        )}

        {/* Stat Cards Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Total Activities"
            value={stats?.total_count ?? 0}
            icon={<TotalActivitiesIcon />}
            loading={statsLoading}
          />
          <StatCard
            title="Today's Activities"
            value={todayActivities}
            icon={<TodayActivitiesIcon />}
            loading={statsLoading}
          />
          <StatCard
            title="Most Common Action"
            value={stats?.most_common_action ?? '-'}
            icon={<MostCommonIcon />}
            loading={statsLoading}
          />
        </div>

        {/* Chart Section */}
        <div className="mb-8">
          {/* Chart View Toggle */}
          <div className="flex items-center justify-end mb-4">
            <div className="inline-flex rounded-md shadow-sm" role="group">
              <button
                onClick={() => setChartView('byDate')}
                className={`px-4 py-2 text-sm font-medium rounded-l-md border ${
                  chartView === 'byDate'
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                } transition-colors duration-150`}
              >
                By Date
              </button>
              <button
                onClick={() => setChartView('byType')}
                className={`px-4 py-2 text-sm font-medium rounded-r-md border-t border-b border-r ${
                  chartView === 'byType'
                    ? 'bg-blue-500 text-white border-blue-500'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                } transition-colors duration-150`}
              >
                By Type
              </button>
            </div>
          </div>

          <ActivityChart
            data={chartView === 'byDate' ? stats?.by_date ?? {} : stats?.by_type ?? {}}
            viewMode={chartView}
            loading={statsLoading}
          />
        </div>

        {/* Activities Error */}
        {activitiesError && (
          <div className="mb-6">
            <ErrorDisplay message={activitiesError} onRetry={refreshData} />
          </div>
        )}

        {/* Activity List Section */}
        <ActivityList
          activities={activities}
          onDelete={handleDeleteFromList}
          onLoadMore={loadMore}
          onSelect={setSelectedActivity}
          hasMore={hasMore}
          loading={activitiesLoading}
        />
      </main>

      {/* Activity Detail Modal */}
      <ActivityDetail
        activity={selectedActivity}
        onClose={() => setSelectedActivity(null)}
        onDelete={handleDeleteFromDetail}
      />

      {/* Delete Confirmation Modal */}
      {deleteConfirmId !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={() => setDeleteConfirmId(null)}
          />
          <div className="relative bg-white rounded-lg shadow-xl max-w-sm w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Activity</h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to delete this activity? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors duration-150"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors duration-150"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
