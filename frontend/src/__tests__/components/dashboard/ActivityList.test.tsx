import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ActivityList from '@/components/dashboard/ActivityList';
import { Activity } from '@/lib/api';

// Mock date-fns to return consistent values
jest.mock('date-fns', () => ({
  ...jest.requireActual('date-fns'),
  formatDistanceToNow: jest.fn(() => '2 hours ago'),
  parseISO: jest.fn((date) => new Date(date)),
}));

// Mock activities data
const mockActivities: Activity[] = [
  {
    id: 1,
    user_id: 1,
    action_type: 'login',
    description: 'User logged in from Chrome',
    extra_data: { ip: '192.168.1.1', browser: 'Chrome' },
    created_at: '2024-01-15T10:30:00Z',
  },
  {
    id: 2,
    user_id: 1,
    action_type: 'create',
    description: 'Created a new document',
    extra_data: { document_id: 123 },
    created_at: '2024-01-15T11:00:00Z',
  },
  {
    id: 3,
    user_id: 1,
    action_type: 'delete',
    description: 'Deleted old record',
    extra_data: null,
    created_at: '2024-01-15T12:00:00Z',
  },
];

describe('ActivityList component', () => {
  const defaultProps = {
    activities: mockActivities,
    onDelete: jest.fn(),
    onLoadMore: jest.fn(),
    onSelect: jest.fn(),
    hasMore: true,
    loading: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering activities', () => {
    it('renders list of activities', () => {
      render(<ActivityList {...defaultProps} />);

      expect(screen.getByText('Recent Activities')).toBeInTheDocument();
      // Use getAllByText since both desktop and mobile views render the same content
      expect(screen.getAllByText('User logged in from Chrome').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Created a new document').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Deleted old record').length).toBeGreaterThanOrEqual(1);
    });

    it('shows action type badges with correct text', () => {
      render(<ActivityList {...defaultProps} />);

      // Check for action type badges (may appear multiple times due to desktop/mobile views)
      expect(screen.getAllByText('login').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('create').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('delete').length).toBeGreaterThanOrEqual(1);
    });

    it('formats time correctly using relative format', () => {
      render(<ActivityList {...defaultProps} />);

      // formatDistanceToNow is mocked to return '2 hours ago'
      const timeElements = screen.getAllByText('2 hours ago');
      expect(timeElements.length).toBeGreaterThanOrEqual(1);
    });

    it('shows dash for null description', () => {
      const activitiesWithNullDesc: Activity[] = [
        {
          id: 1,
          user_id: 1,
          action_type: 'test',
          description: null,
          extra_data: null,
          created_at: '2024-01-15T10:30:00Z',
        },
      ];

      render(<ActivityList {...defaultProps} activities={activitiesWithNullDesc} />);

      // Description shows '-' when null
      expect(screen.getAllByText('-').length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('Delete functionality', () => {
    it('delete button calls onDelete callback with activity id', async () => {
      const user = userEvent.setup();
      const onDelete = jest.fn();

      render(<ActivityList {...defaultProps} onDelete={onDelete} />);

      // Find all delete buttons and click the first one
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      expect(onDelete).toHaveBeenCalledWith(1);
    });

    it('delete button click stops event propagation', async () => {
      const user = userEvent.setup();
      const onDelete = jest.fn();
      const onSelect = jest.fn();

      render(<ActivityList {...defaultProps} onDelete={onDelete} onSelect={onSelect} />);

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      await user.click(deleteButtons[0]);

      // onSelect should not be called when clicking delete
      expect(onDelete).toHaveBeenCalled();
      expect(onSelect).not.toHaveBeenCalled();
    });
  });

  describe('Load More functionality', () => {
    it('Load More button calls onLoadMore callback', async () => {
      const user = userEvent.setup();
      const onLoadMore = jest.fn();

      render(<ActivityList {...defaultProps} onLoadMore={onLoadMore} />);

      const loadMoreButton = screen.getByRole('button', { name: /load more/i });
      await user.click(loadMoreButton);

      expect(onLoadMore).toHaveBeenCalledTimes(1);
    });

    it('Load More button is visible when hasMore is true', () => {
      render(<ActivityList {...defaultProps} hasMore={true} />);

      expect(screen.getByRole('button', { name: /load more/i })).toBeInTheDocument();
    });

    it('Load More button is hidden when hasMore is false', () => {
      render(<ActivityList {...defaultProps} hasMore={false} />);

      expect(screen.queryByRole('button', { name: /load more/i })).not.toBeInTheDocument();
    });

    it('Load More button is hidden when loading', () => {
      render(<ActivityList {...defaultProps} hasMore={true} loading={true} />);

      expect(screen.queryByRole('button', { name: /load more/i })).not.toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty state when activities array is empty', () => {
      render(<ActivityList {...defaultProps} activities={[]} />);

      expect(screen.getByText('No activities yet')).toBeInTheDocument();
      expect(screen.getByText('Your activities will appear here')).toBeInTheDocument();
    });

    it('does not show empty state when loading', () => {
      render(<ActivityList {...defaultProps} activities={[]} loading={true} />);

      expect(screen.queryByText('No activities yet')).not.toBeInTheDocument();
    });
  });

  describe('Loading state', () => {
    it('shows loading skeleton when loading', () => {
      const { container } = render(<ActivityList {...defaultProps} loading={true} />);

      const skeleton = container.querySelector('.animate-pulse');
      expect(skeleton).toBeInTheDocument();
    });

    it('still shows existing activities while loading more', () => {
      render(<ActivityList {...defaultProps} loading={true} />);

      // Use getAllByText since both desktop and mobile views render
      expect(screen.getAllByText('User logged in from Chrome').length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('Selection functionality', () => {
    it('clicking activity row calls onSelect with activity', async () => {
      const user = userEvent.setup();
      const onSelect = jest.fn();

      render(<ActivityList {...defaultProps} onSelect={onSelect} />);

      // Find the table row containing the first activity (desktop view)
      const tableBody = screen.getByRole('table').querySelector('tbody');
      if (tableBody) {
        const firstRow = tableBody.querySelector('tr');
        if (firstRow) {
          await user.click(firstRow);
          expect(onSelect).toHaveBeenCalledWith(mockActivities[0]);
        }
      }
    });
  });

  describe('Action type badge colors', () => {
    it('applies green color for login action type', () => {
      const activities: Activity[] = [
        {
          id: 1,
          user_id: 1,
          action_type: 'login',
          description: 'Test',
          extra_data: null,
          created_at: '2024-01-15T10:30:00Z',
        },
      ];

      render(<ActivityList {...defaultProps} activities={activities} />);

      const badge = screen.getAllByText('login')[0];
      expect(badge).toHaveClass('bg-green-100', 'text-green-800');
    });

    it('applies blue color for create action type', () => {
      const activities: Activity[] = [
        {
          id: 1,
          user_id: 1,
          action_type: 'create',
          description: 'Test',
          extra_data: null,
          created_at: '2024-01-15T10:30:00Z',
        },
      ];

      render(<ActivityList {...defaultProps} activities={activities} />);

      const badge = screen.getAllByText('create')[0];
      expect(badge).toHaveClass('bg-blue-100', 'text-blue-800');
    });

    it('applies red color for delete action type', () => {
      const activities: Activity[] = [
        {
          id: 1,
          user_id: 1,
          action_type: 'delete',
          description: 'Test',
          extra_data: null,
          created_at: '2024-01-15T10:30:00Z',
        },
      ];

      render(<ActivityList {...defaultProps} activities={activities} />);

      const badge = screen.getAllByText('delete')[0];
      expect(badge).toHaveClass('bg-red-100', 'text-red-800');
    });

    it('applies yellow color for update action type', () => {
      const activities: Activity[] = [
        {
          id: 1,
          user_id: 1,
          action_type: 'update',
          description: 'Test',
          extra_data: null,
          created_at: '2024-01-15T10:30:00Z',
        },
      ];

      render(<ActivityList {...defaultProps} activities={activities} />);

      const badge = screen.getAllByText('update')[0];
      expect(badge).toHaveClass('bg-yellow-100', 'text-yellow-800');
    });

    it('applies default indigo color for unknown action type', () => {
      const activities: Activity[] = [
        {
          id: 1,
          user_id: 1,
          action_type: 'custom_action',
          description: 'Test',
          extra_data: null,
          created_at: '2024-01-15T10:30:00Z',
        },
      ];

      render(<ActivityList {...defaultProps} activities={activities} />);

      const badge = screen.getAllByText('custom_action')[0];
      expect(badge).toHaveClass('bg-indigo-100', 'text-indigo-800');
    });
  });

  describe('Desktop view (table)', () => {
    it('renders table with correct headers', () => {
      render(<ActivityList {...defaultProps} />);

      expect(screen.getByText('Action Type')).toBeInTheDocument();
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('Time')).toBeInTheDocument();
      expect(screen.getByText('Actions')).toBeInTheDocument();
    });

    it('renders table structure', () => {
      render(<ActivityList {...defaultProps} />);

      expect(screen.getByRole('table')).toBeInTheDocument();

      const rows = screen.getAllByRole('row');
      // 1 header row + 3 data rows
      expect(rows.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('Mobile view (cards)', () => {
    it('renders mobile card view alongside table view', () => {
      const { container } = render(<ActivityList {...defaultProps} />);

      // Both desktop (hidden md:block) and mobile (md:hidden) views exist in DOM
      const desktopView = container.querySelector('.hidden.md\\:block');
      const mobileView = container.querySelector('.md\\:hidden');

      expect(desktopView).toBeInTheDocument();
      expect(mobileView).toBeInTheDocument();
    });
  });
});
