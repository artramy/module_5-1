'use client';

import { useEffect, useState, useCallback } from 'react';
import { format, parseISO } from 'date-fns';
import { Activity } from '@/lib/api';

interface ActivityDetailProps {
  activity: Activity | null;
  onClose: () => void;
  onDelete: (id: number) => Promise<boolean>;
}

export default function ActivityDetail({ activity, onClose, onDelete }: ActivityDetailProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  const handleClose = useCallback(() => {
    setIsVisible(false);
    setShowDeleteConfirm(false);
    // Wait for animation to complete
    setTimeout(onClose, 200);
  }, [onClose]);

  // Handle animation
  useEffect(() => {
    if (activity) {
      // Trigger enter animation
      requestAnimationFrame(() => {
        setIsVisible(true);
      });
    } else {
      setIsVisible(false);
    }
  }, [activity]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    };

    if (activity) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [activity, handleClose]);

  const handleDelete = async () => {
    if (!activity) return;

    setIsDeleting(true);
    const success = await onDelete(activity.id);
    setIsDeleting(false);

    if (success) {
      handleClose();
    }
  };

  const formatDate = (dateString: string): string => {
    try {
      const date = parseISO(dateString);
      return format(date, 'MMMM d, yyyy at h:mm a');
    } catch {
      return dateString;
    }
  };

  const formatExtraData = (data: Record<string, unknown> | null): string => {
    if (!data || Object.keys(data).length === 0) {
      return 'No additional data';
    }
    return JSON.stringify(data, null, 2);
  };

  if (!activity) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-200 ${
        isVisible ? 'opacity-100' : 'opacity-0'
      }`}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div
        className={`relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 transform transition-all duration-200 ${
          isVisible ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Activity Details</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors duration-150"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Action Type */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Action Type</label>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {activity.action_type}
            </span>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Description</label>
            <p className="text-gray-900">{activity.description || '-'}</p>
          </div>

          {/* Created At */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Created At</label>
            <p className="text-gray-900">{formatDate(activity.created_at)}</p>
          </div>

          {/* Activity ID */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Activity ID</label>
            <p className="text-gray-900 font-mono text-sm">{activity.id}</p>
          </div>

          {/* Extra Data */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">Extra Data</label>
            <pre className="bg-gray-50 rounded-md p-3 text-sm text-gray-800 overflow-auto max-h-40 font-mono">
              {formatExtraData(activity.extra_data)}
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          {!showDeleteConfirm ? (
            <>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors duration-150"
              >
                Delete Activity
              </button>
              <button
                onClick={handleClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-150"
              >
                Close
              </button>
            </>
          ) : (
            <div className="flex items-center justify-between w-full">
              <p className="text-sm text-gray-600">Are you sure you want to delete this activity?</p>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isDeleting}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 transition-colors duration-150"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 flex items-center transition-colors duration-150"
                >
                  {isDeleting && (
                    <svg
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                  )}
                  Delete
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
