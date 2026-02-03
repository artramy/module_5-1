'use client';

import { formatDistanceToNow, parseISO } from 'date-fns';
import { Activity } from '@/lib/api';

interface ActivityListProps {
  activities: Activity[];
  onDelete: (id: number) => void;
  onLoadMore: () => void;
  onSelect?: (activity: Activity) => void;
  hasMore: boolean;
  loading?: boolean;
}

// Badge colors for different action types
const ACTION_TYPE_COLORS: Record<string, string> = {
  login: 'bg-green-100 text-green-800',
  logout: 'bg-gray-100 text-gray-800',
  create: 'bg-blue-100 text-blue-800',
  update: 'bg-yellow-100 text-yellow-800',
  delete: 'bg-red-100 text-red-800',
  view: 'bg-purple-100 text-purple-800',
  default: 'bg-indigo-100 text-indigo-800',
};

function getActionTypeColor(actionType: string): string {
  const lowerType = actionType.toLowerCase();
  for (const key of Object.keys(ACTION_TYPE_COLORS)) {
    if (lowerType.includes(key)) {
      return ACTION_TYPE_COLORS[key];
    }
  }
  return ACTION_TYPE_COLORS.default;
}

function formatRelativeTime(dateString: string): string {
  try {
    const date = parseISO(dateString);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return dateString;
  }
}

export default function ActivityList({
  activities,
  onDelete,
  onLoadMore,
  onSelect,
  hasMore,
  loading = false,
}: ActivityListProps) {
  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="flex items-center p-4 bg-gray-50 rounded-lg">
          <div className="h-6 w-20 bg-gray-200 rounded mr-4"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/4"></div>
          </div>
          <div className="h-8 w-16 bg-gray-200 rounded"></div>
        </div>
      ))}
    </div>
  );

  // Empty state
  if (!loading && activities.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Recent Activities</h3>
        <div className="py-12 text-center">
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="mt-4 text-sm text-gray-500">No activities yet</p>
          <p className="text-sm text-gray-400">Your activities will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-700">Recent Activities</h3>
      </div>

      {/* Desktop view - Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Action Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {activities.map((activity) => (
              <tr
                key={activity.id}
                className="hover:bg-gray-50 transition-colors duration-150 cursor-pointer"
                onClick={() => onSelect?.(activity)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionTypeColor(activity.action_type)}`}
                  >
                    {activity.action_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-md truncate">
                    {activity.description || '-'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">
                    {formatRelativeTime(activity.created_at)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(activity.id);
                    }}
                    className="text-red-600 hover:text-red-900 transition-colors duration-150"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile view - Cards */}
      <div className="md:hidden divide-y divide-gray-200">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="p-4 hover:bg-gray-50 transition-colors duration-150 cursor-pointer"
            onClick={() => onSelect?.(activity)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionTypeColor(activity.action_type)}`}
                >
                  {activity.action_type}
                </span>
                <p className="mt-2 text-sm text-gray-900 truncate">
                  {activity.description || '-'}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  {formatRelativeTime(activity.created_at)}
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(activity.id);
                }}
                className="ml-4 text-red-600 hover:text-red-900 text-sm font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Loading indicator for infinite scroll */}
      {loading && (
        <div className="p-6">
          <LoadingSkeleton />
        </div>
      )}

      {/* Load More button */}
      {hasMore && !loading && (
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={onLoadMore}
            className="w-full py-2 px-4 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-150"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}
