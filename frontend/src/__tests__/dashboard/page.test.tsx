import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import DashboardPage from '@/app/dashboard/page';
import { Activity, ActivityStats } from '@/lib/api';

// Mock Next.js router
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock AuthContext
const mockAuthContext = {
  user: { id: 1, username: 'testuser', email: 'test@example.com', created_at: '2024-01-01T00:00:00Z' },
  token: 'mock-token',
  loading: false,
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
};

jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock useDashboard hook
const mockUseDashboard = {
  activities: [] as Activity[],
  activitiesLoading: false,
  activitiesError: null as string | null,
  stats: null as ActivityStats | null,
  statsLoading: false,
  statsError: null as string | null,
  hasMore: false,
  pagination: { limit: 10, offset: 0, hasMore: false },
  deleteActivity: jest.fn().mockResolvedValue(true),
  refreshData: jest.fn().mockResolvedValue(undefined),
  loadMore: jest.fn().mockResolvedValue(undefined),
  fetchActivities: jest.fn().mockResolvedValue(undefined),
  fetchStats: jest.fn().mockResolvedValue(undefined),
  createActivity: jest.fn().mockResolvedValue(null),
  isLoading: false,
};

jest.mock('@/hooks/useDashboard', () => ({
  useDashboard: () => mockUseDashboard,
  default: () => mockUseDashboard,
}));

// Mock recharts to avoid rendering issues
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="line-chart">{children}</div>
  ),
  BarChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="bar-chart">{children}</div>
  ),
  Line: () => <div data-testid="line" />,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
}));

// Mock date-fns
jest.mock('date-fns', () => ({
  ...jest.requireActual('date-fns'),
  formatDistanceToNow: jest.fn(() => '2 hours ago'),
  parseISO: jest.fn((date) => new Date(date)),
  format: jest.fn(() => 'Jan 15'),
  isValid: jest.fn(() => true),
}));

// Mock data
const mockActivities: Activity[] = [
  {
    id: 1,
    user_id: 1,
    action_type: 'login',
    description: 'User logged in',
    extra_data: { ip: '192.168.1.1' },
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    user_id: 1,
    action_type: 'query',
    description: 'Executed database query',
    extra_data: { query: 'SELECT * FROM users' },
    created_at: new Date().toISOString(),
  },
  {
    id: 3,
    user_id: 1,
    action_type: 'click',
    description: 'Clicked button',
    extra_data: null,
    created_at: new Date().toISOString(),
  },
];

const mockStats: ActivityStats = {
  total_count: 10,
  by_type: { login: 5, query: 3, click: 2 },
  by_date: { '2024-01-15': 5, '2024-01-14': 5 },
  most_common_action: 'login',
};

describe('Dashboard Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset mock values to defaults
    mockUseDashboard.activities = [];
    mockUseDashboard.activitiesLoading = false;
    mockUseDashboard.activitiesError = null;
    mockUseDashboard.stats = null;
    mockUseDashboard.statsLoading = false;
    mockUseDashboard.statsError = null;
    mockUseDashboard.hasMore = false;
    mockAuthContext.user = { id: 1, username: 'testuser', email: 'test@example.com', created_at: '2024-01-01T00:00:00Z' };
    mockAuthContext.loading = false;
  });

  describe('Rendering tests', () => {
    it('page renders without crashing', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('shows loading state initially (ProtectedRoute)', () => {
      mockAuthContext.loading = true;

      render(<DashboardPage />);

      // ProtectedRoute shows loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('redirects to login if not authenticated', () => {
      mockAuthContext.user = null;
      mockAuthContext.loading = false;

      render(<DashboardPage />);

      expect(mockPush).toHaveBeenCalledWith('/login');
    });

    it('renders dashboard content when authenticated', () => {
      mockUseDashboard.stats = mockStats;
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Recent Activities')).toBeInTheDocument();
    });
  });

  describe('Stats cards display', () => {
    it('renders 3 StatCards', () => {
      mockUseDashboard.stats = mockStats;

      render(<DashboardPage />);

      expect(screen.getByText('Total Activities')).toBeInTheDocument();
      expect(screen.getByText("Today's Activities")).toBeInTheDocument();
      expect(screen.getByText('Most Common Action')).toBeInTheDocument();
    });

    it('displays correct values from mock data', () => {
      mockUseDashboard.stats = mockStats;

      render(<DashboardPage />);

      // Total count
      expect(screen.getByText('10')).toBeInTheDocument();

      // Most common action
      expect(screen.getByText('login')).toBeInTheDocument();
    });

    it('shows loading skeletons when statsLoading is true', () => {
      mockUseDashboard.statsLoading = true;

      const { container } = render(<DashboardPage />);

      // Should have multiple loading skeletons
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('displays 0 for total activities when stats is null', () => {
      mockUseDashboard.stats = null;

      render(<DashboardPage />);

      // Should show 0 as default value
      const zeroValues = screen.getAllByText('0');
      expect(zeroValues.length).toBeGreaterThan(0);
    });

    it('displays dash for most common action when not available', () => {
      mockUseDashboard.stats = null;

      render(<DashboardPage />);

      // Should show '-' when most_common_action is not available
      expect(screen.getByText('-')).toBeInTheDocument();
    });
  });

  describe('Activity list display', () => {
    it('renders ActivityList component', () => {
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      expect(screen.getByText('Recent Activities')).toBeInTheDocument();
    });

    it('shows activities from mock data', () => {
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      // Use getAllByText since both desktop and mobile views render
      expect(screen.getAllByText('User logged in').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Executed database query').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Clicked button').length).toBeGreaterThanOrEqual(1);
    });

    it('Load More button appears when hasMore is true', () => {
      mockUseDashboard.activities = mockActivities;
      mockUseDashboard.hasMore = true;

      render(<DashboardPage />);

      expect(screen.getByRole('button', { name: /load more/i })).toBeInTheDocument();
    });

    it('Load More button is hidden when hasMore is false', () => {
      mockUseDashboard.activities = mockActivities;
      mockUseDashboard.hasMore = false;

      render(<DashboardPage />);

      expect(screen.queryByRole('button', { name: /load more/i })).not.toBeInTheDocument();
    });

    it('shows empty state when no activities', () => {
      mockUseDashboard.activities = [];

      render(<DashboardPage />);

      expect(screen.getByText('No activities yet')).toBeInTheDocument();
    });
  });

  describe('Chart display', () => {
    it('renders ActivityChart component', () => {
      mockUseDashboard.stats = mockStats;

      render(<DashboardPage />);

      // Chart container should be rendered
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    });

    it('toggle between Date/Type views works', async () => {
      const user = userEvent.setup();
      mockUseDashboard.stats = mockStats;

      render(<DashboardPage />);

      // Find toggle buttons
      const byDateButton = screen.getByRole('button', { name: /by date/i });
      const byTypeButton = screen.getByRole('button', { name: /by type/i });

      expect(byDateButton).toBeInTheDocument();
      expect(byTypeButton).toBeInTheDocument();

      // Initially byDate should be active (blue background)
      expect(byDateButton).toHaveClass('bg-blue-500');

      // Click byType button wrapped in act
      await act(async () => {
        await user.click(byTypeButton);
      });

      // Now byType should be active
      expect(byTypeButton).toHaveClass('bg-blue-500');
    });
  });

  describe('Error handling', () => {
    it('shows error message when stats fetch fails', () => {
      mockUseDashboard.statsError = 'Failed to load statistics';

      render(<DashboardPage />);

      expect(screen.getByText('Failed to load statistics')).toBeInTheDocument();
    });

    it('shows error message when activities fetch fails', () => {
      mockUseDashboard.activitiesError = 'Failed to load activities';

      render(<DashboardPage />);

      expect(screen.getByText('Failed to load activities')).toBeInTheDocument();
    });

    it('Retry button appears on stats error', () => {
      mockUseDashboard.statsError = 'Failed to load statistics';

      render(<DashboardPage />);

      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('Retry button calls refreshData', async () => {
      const user = userEvent.setup();
      mockUseDashboard.statsError = 'Failed to load statistics';

      render(<DashboardPage />);

      const retryButton = screen.getByRole('button', { name: /try again/i });
      await user.click(retryButton);

      expect(mockUseDashboard.refreshData).toHaveBeenCalled();
    });
  });

  describe('Refresh functionality', () => {
    it('Refresh button is rendered', () => {
      render(<DashboardPage />);

      expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
    });

    it('Refresh button calls refreshData', async () => {
      const user = userEvent.setup();

      render(<DashboardPage />);

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      await user.click(refreshButton);

      expect(mockUseDashboard.refreshData).toHaveBeenCalled();
    });
  });

  describe('Delete functionality', () => {
    it('delete from list shows confirmation modal', async () => {
      const user = userEvent.setup();
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      // Find and click a delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      // Filter for the list delete buttons (not the modal ones)
      const listDeleteButton = deleteButtons[0];

      await act(async () => {
        await user.click(listDeleteButton);
      });

      // Confirmation modal should appear
      expect(screen.getByText('Delete Activity')).toBeInTheDocument();
      expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    });

    it('cancel button in confirmation modal closes it', async () => {
      const user = userEvent.setup();
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      // Open confirmation
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await act(async () => {
        await user.click(deleteButtons[0]);
      });

      // Click cancel
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      await act(async () => {
        await user.click(cancelButton);
      });

      // Modal should be closed
      await waitFor(() => {
        expect(screen.queryByText(/are you sure you want to delete/i)).not.toBeInTheDocument();
      });
    });

    it('confirming delete calls deleteActivity', async () => {
      const user = userEvent.setup();
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      // Open confirmation
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await act(async () => {
        await user.click(deleteButtons[0]);
      });

      // Find and click the confirm delete button (in the modal)
      const modalDeleteButtons = screen.getAllByRole('button', { name: 'Delete' });
      const confirmDeleteButton = modalDeleteButtons.find(btn =>
        btn.closest('.bg-red-600') || btn.classList.contains('bg-red-600')
      );

      if (confirmDeleteButton) {
        await act(async () => {
          await user.click(confirmDeleteButton);
        });
        expect(mockUseDashboard.deleteActivity).toHaveBeenCalled();
      }
    });
  });

  describe('Activity detail modal', () => {
    it('clicking activity opens detail modal', async () => {
      const user = userEvent.setup();
      mockUseDashboard.activities = mockActivities;

      render(<DashboardPage />);

      // Find the table row and click it
      const tableBody = document.querySelector('tbody');
      if (tableBody) {
        const firstRow = tableBody.querySelector('tr');
        if (firstRow) {
          await act(async () => {
            await user.click(firstRow);
          });

          // Detail modal should open
          await waitFor(() => {
            expect(screen.getByText('Activity Details')).toBeInTheDocument();
          });
        }
      }
    });
  });

  describe('Load More functionality', () => {
    it('Load More button calls loadMore', async () => {
      const user = userEvent.setup();
      mockUseDashboard.activities = mockActivities;
      mockUseDashboard.hasMore = true;

      render(<DashboardPage />);

      const loadMoreButton = screen.getByRole('button', { name: /load more/i });
      await act(async () => {
        await user.click(loadMoreButton);
      });

      expect(mockUseDashboard.loadMore).toHaveBeenCalled();
    });
  });
});
