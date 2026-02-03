import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActivityChart from '@/components/dashboard/ActivityChart';

// Mock recharts to avoid rendering issues in tests
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container" style={{ width: 400, height: 300 }}>
        {children}
      </div>
    ),
    LineChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
      <div data-testid="line-chart" data-count={data?.length || 0}>
        {children}
      </div>
    ),
    BarChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
      <div data-testid="bar-chart" data-count={data?.length || 0}>
        {children}
      </div>
    ),
    Line: () => <div data-testid="line" />,
    Bar: () => <div data-testid="bar" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
  };
});

// Mock data
const mockByDateData: Record<string, number> = {
  '2024-01-15': 5,
  '2024-01-14': 8,
  '2024-01-13': 3,
  '2024-01-12': 10,
};

const mockByTypeData: Record<string, number> = {
  login: 15,
  create: 8,
  delete: 3,
  view: 12,
};

describe('ActivityChart component', () => {
  describe('By Date view (LineChart)', () => {
    it('renders with by_date data showing LineChart', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.getByTestId('line')).toBeInTheDocument();
    });

    it('displays correct title for byDate view', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByText('Activity Over Time')).toBeInTheDocument();
    });

    it('passes correct data count to LineChart', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      const lineChart = screen.getByTestId('line-chart');
      expect(lineChart).toHaveAttribute('data-count', '4');
    });

    it('does not render BarChart in byDate view', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();
    });
  });

  describe('By Type view (BarChart)', () => {
    it('renders with by_type data showing BarChart', () => {
      render(<ActivityChart data={mockByTypeData} viewMode="byType" />);

      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
      expect(screen.getByTestId('bar')).toBeInTheDocument();
    });

    it('displays correct title for byType view', () => {
      render(<ActivityChart data={mockByTypeData} viewMode="byType" />);

      expect(screen.getByText('Activity by Type')).toBeInTheDocument();
    });

    it('passes correct data count to BarChart', () => {
      render(<ActivityChart data={mockByTypeData} viewMode="byType" />);

      const barChart = screen.getByTestId('bar-chart');
      expect(barChart).toHaveAttribute('data-count', '4');
    });

    it('does not render LineChart in byType view', () => {
      render(<ActivityChart data={mockByTypeData} viewMode="byType" />);

      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
    });
  });

  describe('Empty state', () => {
    it('shows empty state when data is empty object', () => {
      render(<ActivityChart data={{}} viewMode="byDate" />);

      expect(screen.getByText('No activity data available')).toBeInTheDocument();
    });

    it('shows empty state when data is null/undefined', () => {
      render(<ActivityChart data={undefined as unknown as Record<string, number>} viewMode="byDate" />);

      expect(screen.getByText('No activity data available')).toBeInTheDocument();
    });

    it('does not render chart components in empty state', () => {
      render(<ActivityChart data={{}} viewMode="byDate" />);

      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
      expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();
    });

    it('shows correct empty state title for byDate view', () => {
      render(<ActivityChart data={{}} viewMode="byDate" />);

      expect(screen.getByText('Activity Over Time')).toBeInTheDocument();
    });

    it('shows correct empty state title for byType view', () => {
      render(<ActivityChart data={{}} viewMode="byType" />);

      expect(screen.getByText('Activity by Type')).toBeInTheDocument();
    });
  });

  describe('Loading state', () => {
    it('shows loading state when loading prop is true', () => {
      const { container } = render(
        <ActivityChart data={mockByDateData} viewMode="byDate" loading={true} />
      );

      const skeleton = container.querySelector('.animate-pulse');
      expect(skeleton).toBeInTheDocument();
    });

    it('shows "Loading chart..." text during loading', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" loading={true} />);

      expect(screen.getByText('Loading chart...')).toBeInTheDocument();
    });

    it('does not render chart during loading', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" loading={true} />);

      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
      expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();
    });

    it('shows skeleton placeholder during loading', () => {
      const { container } = render(
        <ActivityChart data={mockByDateData} viewMode="byDate" loading={true} />
      );

      const placeholders = container.querySelectorAll('.bg-gray-200, .bg-gray-100');
      expect(placeholders.length).toBeGreaterThan(0);
    });
  });

  describe('Chart components', () => {
    it('renders ResponsiveContainer', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    });

    it('renders XAxis component', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByTestId('x-axis')).toBeInTheDocument();
    });

    it('renders YAxis component', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByTestId('y-axis')).toBeInTheDocument();
    });

    it('renders CartesianGrid component', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByTestId('cartesian-grid')).toBeInTheDocument();
    });

    it('renders Tooltip component', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      expect(screen.getByTestId('tooltip')).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('renders with correct container styling', () => {
      const { container } = render(
        <ActivityChart data={mockByDateData} viewMode="byDate" />
      );

      const card = container.firstChild;
      expect(card).toHaveClass('bg-white');
      expect(card).toHaveClass('rounded-lg');
      expect(card).toHaveClass('shadow');
      expect(card).toHaveClass('p-6');
    });

    it('renders title with correct styling', () => {
      render(<ActivityChart data={mockByDateData} viewMode="byDate" />);

      const title = screen.getByText('Activity Over Time');
      expect(title).toHaveClass('text-lg');
      expect(title).toHaveClass('font-semibold');
      expect(title).toHaveClass('text-gray-700');
    });
  });

  describe('View mode switching', () => {
    it('changes from LineChart to BarChart when viewMode changes', () => {
      const { rerender } = render(
        <ActivityChart data={mockByDateData} viewMode="byDate" />
      );

      expect(screen.getByTestId('line-chart')).toBeInTheDocument();
      expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();

      rerender(<ActivityChart data={mockByTypeData} viewMode="byType" />);

      expect(screen.queryByTestId('line-chart')).not.toBeInTheDocument();
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });

    it('updates title when viewMode changes', () => {
      const { rerender } = render(
        <ActivityChart data={mockByDateData} viewMode="byDate" />
      );

      expect(screen.getByText('Activity Over Time')).toBeInTheDocument();

      rerender(<ActivityChart data={mockByTypeData} viewMode="byType" />);

      expect(screen.getByText('Activity by Type')).toBeInTheDocument();
    });
  });
});
