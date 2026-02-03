'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  ActivityCreateData,
  ActivityStats,
  getActivities,
  getActivityStats,
  createActivity as apiCreateActivity,
  deleteActivity as apiDeleteActivity,
} from '@/lib/api';

interface ActivitiesState {
  data: Activity[];
  loading: boolean;
  error: string | null;
}

interface StatsState {
  data: ActivityStats | null;
  loading: boolean;
  error: string | null;
}

interface PaginationState {
  limit: number;
  offset: number;
  hasMore: boolean;
}

interface UseDashboardReturn {
  // Activities state
  activities: Activity[];
  activitiesLoading: boolean;
  activitiesError: string | null;

  // Stats state
  stats: ActivityStats | null;
  statsLoading: boolean;
  statsError: string | null;

  // Pagination state
  pagination: PaginationState;
  hasMore: boolean;

  // CRUD operations
  fetchActivities: (limit?: number, offset?: number) => Promise<void>;
  fetchStats: (startDate?: string, endDate?: string) => Promise<void>;
  createActivity: (data: ActivityCreateData) => Promise<Activity | null>;
  deleteActivity: (id: number) => Promise<boolean>;
  refreshData: () => Promise<void>;
  loadMore: () => Promise<void>;

  // UI helpers
  isLoading: boolean;
}

const DEFAULT_LIMIT = 10;

export function useDashboard(): UseDashboardReturn {
  // Activities state
  const [activitiesState, setActivitiesState] = useState<ActivitiesState>({
    data: [],
    loading: true,
    error: null,
  });

  // Stats state
  const [statsState, setStatsState] = useState<StatsState>({
    data: null,
    loading: true,
    error: null,
  });

  // Pagination state
  const [pagination, setPagination] = useState<PaginationState>({
    limit: DEFAULT_LIMIT,
    offset: 0,
    hasMore: true,
  });

  // Fetch activities with pagination
  const fetchActivities = useCallback(async (limit: number = DEFAULT_LIMIT, offset: number = 0) => {
    setActivitiesState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await getActivities(limit, offset);

      setActivitiesState((prev) => ({
        data: offset === 0 ? data : [...prev.data, ...data],
        loading: false,
        error: null,
      }));

      setPagination({
        limit,
        offset,
        hasMore: data.length === limit,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch activities. Please try again.';
      setActivitiesState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  }, []);

  // Fetch stats with optional date range
  const fetchStats = useCallback(async (startDate?: string, endDate?: string) => {
    setStatsState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await getActivityStats(startDate, endDate);
      setStatsState({
        data,
        loading: false,
        error: null,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch statistics. Please try again.';
      setStatsState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  }, []);

  // Create a new activity
  const createActivity = useCallback(
    async (data: ActivityCreateData): Promise<Activity | null> => {
      try {
        const newActivity = await apiCreateActivity(data);
        // Add the new activity to the beginning of the list
        setActivitiesState((prev) => ({
          ...prev,
          data: [newActivity, ...prev.data],
        }));
        // Refresh stats to reflect the new activity
        fetchStats();
        return newActivity;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to create activity. Please try again.';
        setActivitiesState((prev) => ({
          ...prev,
          error: errorMessage,
        }));
        return null;
      }
    },
    [fetchStats]
  );

  // Delete an activity
  const deleteActivity = useCallback(
    async (id: number): Promise<boolean> => {
      try {
        await apiDeleteActivity(id);
        // Remove the activity from the list
        setActivitiesState((prev) => ({
          ...prev,
          data: prev.data.filter((activity) => activity.id !== id),
        }));
        // Refresh stats to reflect the deletion
        fetchStats();
        return true;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to delete activity. Please try again.';
        setActivitiesState((prev) => ({
          ...prev,
          error: errorMessage,
        }));
        return false;
      }
    },
    [fetchStats]
  );

  // Refresh both activities and stats
  const refreshData = useCallback(async () => {
    setPagination((prev) => ({ ...prev, offset: 0 }));
    await Promise.all([fetchActivities(pagination.limit, 0), fetchStats()]);
  }, [fetchActivities, fetchStats, pagination.limit]);

  // Load more activities (pagination)
  const loadMore = useCallback(async () => {
    if (!pagination.hasMore || activitiesState.loading) return;

    const newOffset = pagination.offset + pagination.limit;
    await fetchActivities(pagination.limit, newOffset);
  }, [fetchActivities, pagination, activitiesState.loading]);

  // Auto-fetch on mount
  useEffect(() => {
    fetchActivities();
    fetchStats();
  }, [fetchActivities, fetchStats]);

  // Combined loading state
  const isLoading = activitiesState.loading || statsState.loading;

  return {
    // Activities state
    activities: activitiesState.data,
    activitiesLoading: activitiesState.loading,
    activitiesError: activitiesState.error,

    // Stats state
    stats: statsState.data,
    statsLoading: statsState.loading,
    statsError: statsState.error,

    // Pagination state
    pagination,
    hasMore: pagination.hasMore,

    // CRUD operations
    fetchActivities,
    fetchStats,
    createActivity,
    deleteActivity,
    refreshData,
    loadMore,

    // UI helpers
    isLoading,
  };
}

export default useDashboard;
