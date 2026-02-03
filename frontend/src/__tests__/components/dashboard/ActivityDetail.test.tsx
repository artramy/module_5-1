import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ActivityDetail from '@/components/dashboard/ActivityDetail';
import { Activity } from '@/lib/api';

// Mock date-fns
jest.mock('date-fns', () => ({
  ...jest.requireActual('date-fns'),
  format: jest.fn(() => 'January 15, 2024 at 10:30 AM'),
  parseISO: jest.fn((date) => new Date(date)),
}));

// Mock requestAnimationFrame for tests
const originalRAF = global.requestAnimationFrame;
beforeAll(() => {
  global.requestAnimationFrame = (callback: FrameRequestCallback) => {
    return setTimeout(() => callback(Date.now()), 0) as unknown as number;
  };
});

afterAll(() => {
  global.requestAnimationFrame = originalRAF;
});

// Mock activity data
const mockActivity: Activity = {
  id: 1,
  user_id: 1,
  action_type: 'login',
  description: 'User logged in from Chrome browser',
  extra_data: { ip: '192.168.1.1', browser: 'Chrome', os: 'Windows' },
  created_at: '2024-01-15T10:30:00Z',
};

const mockActivityWithNullData: Activity = {
  id: 2,
  user_id: 1,
  action_type: 'logout',
  description: null,
  extra_data: null,
  created_at: '2024-01-15T11:00:00Z',
};

describe('ActivityDetail component', () => {
  const defaultProps = {
    activity: mockActivity,
    onClose: jest.fn(),
    onDelete: jest.fn().mockResolvedValue(true),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset body overflow style
    document.body.style.overflow = 'unset';
  });

  describe('Rendering', () => {
    it('renders when activity is provided', () => {
      render(<ActivityDetail {...defaultProps} />);

      expect(screen.getByText('Activity Details')).toBeInTheDocument();
    });

    it('does not render when activity is null', () => {
      const { container } = render(
        <ActivityDetail {...defaultProps} activity={null} />
      );

      expect(container).toBeEmptyDOMElement();
    });

    it('displays all activity fields', () => {
      render(<ActivityDetail {...defaultProps} />);

      // Action Type
      expect(screen.getByText('Action Type')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();

      // Description
      expect(screen.getByText('Description')).toBeInTheDocument();
      expect(screen.getByText('User logged in from Chrome browser')).toBeInTheDocument();

      // Created At
      expect(screen.getByText('Created At')).toBeInTheDocument();
      expect(screen.getByText('January 15, 2024 at 10:30 AM')).toBeInTheDocument();

      // Activity ID
      expect(screen.getByText('Activity ID')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();

      // Extra Data
      expect(screen.getByText('Extra Data')).toBeInTheDocument();
    });

    it('formats extra_data as JSON', () => {
      render(<ActivityDetail {...defaultProps} />);

      // The extra data should be formatted as JSON with indentation
      const preElement = screen.getByText(/192\.168\.1\.1/);
      expect(preElement.tagName).toBe('PRE');
      expect(preElement.textContent).toContain('"ip"');
      expect(preElement.textContent).toContain('"browser"');
      expect(preElement.textContent).toContain('"os"');
    });

    it('shows "No additional data" for null extra_data', () => {
      render(<ActivityDetail {...defaultProps} activity={mockActivityWithNullData} />);

      expect(screen.getByText('No additional data')).toBeInTheDocument();
    });

    it('shows "-" for null description', () => {
      render(<ActivityDetail {...defaultProps} activity={mockActivityWithNullData} />);

      expect(screen.getByText('-')).toBeInTheDocument();
    });
  });

  describe('Close functionality', () => {
    it('Close button calls onClose callback', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();

      render(<ActivityDetail {...defaultProps} onClose={onClose} />);

      // Find the Close button in footer
      const closeButton = screen.getByRole('button', { name: 'Close' });
      await user.click(closeButton);

      // Wait for animation timeout
      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      }, { timeout: 500 });
    });

    it('X button in header calls onClose callback', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();

      render(<ActivityDetail {...defaultProps} onClose={onClose} />);

      // Find the X button in header (the one without text, just an SVG)
      const headerButtons = screen.getAllByRole('button');
      const xButton = headerButtons.find(btn => btn.querySelector('svg path[d*="M6 18L18 6"]'));

      if (xButton) {
        await user.click(xButton);

        await waitFor(() => {
          expect(onClose).toHaveBeenCalled();
        }, { timeout: 500 });
      }
    });

    it('Backdrop click calls onClose callback', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();

      render(<ActivityDetail {...defaultProps} onClose={onClose} />);

      // Find and click the backdrop
      const backdrop = document.querySelector('.bg-black.bg-opacity-50');
      if (backdrop) {
        await user.click(backdrop);

        await waitFor(() => {
          expect(onClose).toHaveBeenCalled();
        }, { timeout: 500 });
      }
    });

    it('ESC key calls onClose callback', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();

      render(<ActivityDetail {...defaultProps} onClose={onClose} />);

      await user.keyboard('{Escape}');

      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      }, { timeout: 500 });
    });
  });

  describe('Delete functionality', () => {
    it('Delete Activity button shows confirmation dialog', async () => {
      const user = userEvent.setup();

      render(<ActivityDetail {...defaultProps} />);

      const deleteButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteButton);

      expect(screen.getByText(/are you sure you want to delete/i)).toBeInTheDocument();
    });

    it('Delete confirmation shows Cancel and Delete buttons', async () => {
      const user = userEvent.setup();

      render(<ActivityDetail {...defaultProps} />);

      const deleteButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteButton);

      expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
    });

    it('Cancel button hides confirmation dialog', async () => {
      const user = userEvent.setup();

      render(<ActivityDetail {...defaultProps} />);

      // Show confirmation
      const deleteButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteButton);

      // Click cancel
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });
      await user.click(cancelButton);

      // Confirmation should be hidden
      expect(screen.queryByText(/are you sure you want to delete/i)).not.toBeInTheDocument();
    });

    it('Delete confirmation calls onDelete with activity id', async () => {
      const user = userEvent.setup();
      const onDelete = jest.fn().mockResolvedValue(true);

      render(<ActivityDetail {...defaultProps} onDelete={onDelete} />);

      // Show confirmation
      const deleteActivityButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteActivityButton);

      // Confirm delete
      const confirmDeleteButton = screen.getByRole('button', { name: 'Delete' });

      await act(async () => {
        await user.click(confirmDeleteButton);
      });

      await waitFor(() => {
        expect(onDelete).toHaveBeenCalledWith(mockActivity.id);
      });

      // Wait for any pending state updates
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 300));
      });
    });

    it('closes modal after successful delete', async () => {
      const user = userEvent.setup();
      const onDelete = jest.fn().mockResolvedValue(true);
      const onClose = jest.fn();

      render(<ActivityDetail {...defaultProps} onDelete={onDelete} onClose={onClose} />);

      // Show confirmation and delete
      const deleteActivityButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteActivityButton);

      const confirmDeleteButton = screen.getByRole('button', { name: 'Delete' });
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      }, { timeout: 500 });
    });

    it('does not close modal if delete fails', async () => {
      const user = userEvent.setup();
      const onDelete = jest.fn().mockResolvedValue(false);
      const onClose = jest.fn();

      render(<ActivityDetail {...defaultProps} onDelete={onDelete} onClose={onClose} />);

      // Show confirmation and delete
      const deleteActivityButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteActivityButton);

      const confirmDeleteButton = screen.getByRole('button', { name: 'Delete' });
      await user.click(confirmDeleteButton);

      await waitFor(() => {
        expect(onDelete).toHaveBeenCalled();
      });

      // Modal should still be visible (close not called immediately after failed delete)
      // Wait for any pending state updates
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });
      expect(onClose).not.toHaveBeenCalled();
    });

    it('shows loading spinner during delete', async () => {
      const user = userEvent.setup();
      let resolveDelete: (value: boolean) => void;
      const onDelete = jest.fn().mockImplementation(() => {
        return new Promise<boolean>((resolve) => {
          resolveDelete = resolve;
        });
      });

      render(<ActivityDetail {...defaultProps} onDelete={onDelete} />);

      // Show confirmation and start delete
      const deleteActivityButton = screen.getByRole('button', { name: /delete activity/i });
      await user.click(deleteActivityButton);

      const confirmDeleteButton = screen.getByRole('button', { name: 'Delete' });
      await user.click(confirmDeleteButton);

      // Should show loading spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();

      // Resolve to clean up and wait for state updates
      await act(async () => {
        resolveDelete!(true);
        await new Promise(resolve => setTimeout(resolve, 300));
      });
    });

    it('disables buttons during delete', async () => {
      const user = userEvent.setup();
      let resolveDelete: (value: boolean) => void;
      const onDelete = jest.fn().mockImplementation(() => {
        return new Promise<boolean>((resolve) => {
          resolveDelete = resolve;
        });
      });

      await act(async () => {
        render(<ActivityDetail {...defaultProps} onDelete={onDelete} />);
        // Wait for requestAnimationFrame
        await new Promise(resolve => setTimeout(resolve, 0));
      });

      // Show confirmation and start delete
      const deleteActivityButton = screen.getByRole('button', { name: /delete activity/i });
      await act(async () => {
        await user.click(deleteActivityButton);
      });

      const confirmDeleteButton = screen.getByRole('button', { name: 'Delete' });
      const cancelButton = screen.getByRole('button', { name: 'Cancel' });

      await act(async () => {
        await user.click(confirmDeleteButton);
      });

      // Buttons should be disabled
      expect(confirmDeleteButton).toBeDisabled();
      expect(cancelButton).toBeDisabled();

      // Resolve to clean up and wait for state updates
      await act(async () => {
        resolveDelete!(true);
        await new Promise(resolve => setTimeout(resolve, 300));
      });
    });
  });

  describe('Modal behavior', () => {
    it('prevents body scroll when modal is open', () => {
      render(<ActivityDetail {...defaultProps} />);

      expect(document.body.style.overflow).toBe('hidden');
    });

    it('restores body scroll when modal closes', () => {
      const { unmount } = render(<ActivityDetail {...defaultProps} />);

      unmount();

      expect(document.body.style.overflow).toBe('unset');
    });
  });

  describe('Styling', () => {
    it('renders modal with correct styling', () => {
      render(<ActivityDetail {...defaultProps} />);

      // Find the modal container (relative, bg-white)
      const modal = document.querySelector('.relative.bg-white.rounded-lg.shadow-xl');
      expect(modal).toBeInTheDocument();
    });

    it('renders action type badge with correct styling', () => {
      render(<ActivityDetail {...defaultProps} />);

      const badge = screen.getByText('login');
      expect(badge).toHaveClass('rounded-full');
      expect(badge).toHaveClass('bg-blue-100');
      expect(badge).toHaveClass('text-blue-800');
    });

    it('renders extra data in monospace font', () => {
      render(<ActivityDetail {...defaultProps} />);

      const preElement = screen.getByText(/192\.168\.1\.1/);
      expect(preElement).toHaveClass('font-mono');
    });

    it('renders activity ID in monospace font', () => {
      render(<ActivityDetail {...defaultProps} />);

      const idElement = screen.getByText('1');
      expect(idElement).toHaveClass('font-mono');
    });
  });

  describe('Animation', () => {
    it('applies animation classes', () => {
      const { container } = render(<ActivityDetail {...defaultProps} />);

      // The modal container should have transition classes
      const modalContainer = container.querySelector('.transition-opacity');
      expect(modalContainer).toBeInTheDocument();
    });
  });
});
