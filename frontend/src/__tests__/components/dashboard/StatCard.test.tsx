import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatCard from '@/components/dashboard/StatCard';

describe('StatCard component', () => {
  describe('Basic rendering', () => {
    it('renders with title and value', () => {
      render(<StatCard title="Total Activities" value={42} />);

      expect(screen.getByText('Total Activities')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
    });

    it('renders with string value', () => {
      render(<StatCard title="Most Common Action" value="login" />);

      expect(screen.getByText('Most Common Action')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
    });

    it('renders with zero value', () => {
      render(<StatCard title="Count" value={0} />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });
  });

  describe('With icon', () => {
    it('renders with optional icon', () => {
      const TestIcon = () => <svg data-testid="test-icon" />;

      render(<StatCard title="Test" value={10} icon={<TestIcon />} />);

      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });

    it('renders without icon when not provided', () => {
      const { container } = render(<StatCard title="Test" value={10} />);

      // Should not have the icon wrapper with bg-blue-50
      const iconWrapper = container.querySelector('.bg-blue-50');
      expect(iconWrapper).not.toBeInTheDocument();
    });
  });

  describe('With trend', () => {
    it('renders with positive trend in green color', () => {
      render(<StatCard title="Test" value={10} trend="+15%" />);

      const trendElement = screen.getByText('+15%');
      expect(trendElement).toBeInTheDocument();
      expect(trendElement).toHaveClass('text-green-600');
    });

    it('renders with negative trend in red color', () => {
      render(<StatCard title="Test" value={10} trend="-5%" />);

      const trendElement = screen.getByText('-5%');
      expect(trendElement).toBeInTheDocument();
      expect(trendElement).toHaveClass('text-red-600');
    });

    it('renders neutral trend in gray color', () => {
      render(<StatCard title="Test" value={10} trend="0%" />);

      const trendElement = screen.getByText('0%');
      expect(trendElement).toBeInTheDocument();
      expect(trendElement).toHaveClass('text-gray-600');
    });

    it('renders "from last period" text with trend', () => {
      render(<StatCard title="Test" value={10} trend="+10%" />);

      expect(screen.getByText('from last period')).toBeInTheDocument();
    });

    it('does not render trend section when trend is not provided', () => {
      render(<StatCard title="Test" value={10} />);

      expect(screen.queryByText('from last period')).not.toBeInTheDocument();
    });
  });

  describe('Loading state', () => {
    it('shows loading skeleton when loading prop is true', () => {
      const { container } = render(<StatCard title="Test" value={10} loading={true} />);

      // Should have animate-pulse class for loading skeleton
      const skeleton = container.querySelector('.animate-pulse');
      expect(skeleton).toBeInTheDocument();
    });

    it('shows placeholder elements during loading', () => {
      const { container } = render(<StatCard title="Test" value={10} loading={true} />);

      // Should have skeleton placeholder divs with bg-gray-200
      const placeholders = container.querySelectorAll('.bg-gray-200');
      expect(placeholders.length).toBeGreaterThan(0);
    });

    it('does not show actual title and value during loading', () => {
      render(<StatCard title="Test Title" value={999} loading={true} />);

      expect(screen.queryByText('Test Title')).not.toBeInTheDocument();
      expect(screen.queryByText('999')).not.toBeInTheDocument();
    });

    it('shows icon placeholder when loading with icon', () => {
      const TestIcon = () => <svg data-testid="test-icon" />;
      const { container } = render(
        <StatCard title="Test" value={10} icon={<TestIcon />} loading={true} />
      );

      // Icon should not be rendered, but placeholder should exist
      expect(screen.queryByTestId('test-icon')).not.toBeInTheDocument();
      const iconPlaceholder = container.querySelector('.rounded-full.bg-gray-200');
      expect(iconPlaceholder).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('applies correct styling to the card', () => {
      const { container } = render(<StatCard title="Test" value={10} />);

      const card = container.firstChild;
      expect(card).toHaveClass('bg-white');
      expect(card).toHaveClass('rounded-lg');
      expect(card).toHaveClass('shadow');
      expect(card).toHaveClass('p-6');
    });

    it('applies hover shadow transition', () => {
      const { container } = render(<StatCard title="Test" value={10} />);

      const card = container.firstChild;
      expect(card).toHaveClass('hover:shadow-lg');
      expect(card).toHaveClass('transition-all');
    });

    it('applies uppercase tracking to title', () => {
      render(<StatCard title="Test Title" value={10} />);

      const title = screen.getByText('Test Title');
      expect(title).toHaveClass('uppercase');
      expect(title).toHaveClass('tracking-wide');
    });

    it('applies bold styling to value', () => {
      render(<StatCard title="Test" value={42} />);

      const value = screen.getByText('42');
      expect(value).toHaveClass('font-bold');
      expect(value).toHaveClass('text-3xl');
    });
  });
});
