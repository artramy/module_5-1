import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from '../app/page';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Home 페이지', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(async () => {
    // Wait for any pending state updates to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });
  });

  it('페이지 제목이 올바르게 렌더링된다', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({ status: 'ok', message: 'Server is running' }),
    });

    await act(async () => {
      render(<Home />);
    });

    expect(screen.getByText('Module 5')).toBeInTheDocument();
  });

  it('기술 스택 설명이 표시된다', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({ status: 'ok', message: 'Server is running' }),
    });

    await act(async () => {
      render(<Home />);
    });

    expect(screen.getByText('Next.js + FastAPI + SQLite')).toBeInTheDocument();
  });

  it('로딩 중일 때 스피너가 표시된다', async () => {
    // Never resolve to keep loading state
    mockFetch.mockImplementationOnce(() => new Promise(() => {}));

    await act(async () => {
      render(<Home />);
    });

    // Check for loading spinner (animate-spin class is on the spinner div)
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('백엔드 상태 섹션 헤더가 표시된다', async () => {
    mockFetch.mockResolvedValueOnce({
      json: () => Promise.resolve({ status: 'ok', message: 'Server is running' }),
    });

    await act(async () => {
      render(<Home />);
    });

    expect(screen.getByText('백엔드 상태')).toBeInTheDocument();
  });

  describe('Health Check API 호출', () => {
    it('/api/health 엔드포인트를 호출한다', async () => {
      mockFetch.mockResolvedValueOnce({
        json: () => Promise.resolve({ status: 'ok', message: 'Server is running' }),
      });

      await act(async () => {
        render(<Home />);
      });

      expect(mockFetch).toHaveBeenCalledWith('/api/health');
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('백엔드 연결 성공 시', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValueOnce({
        json: () => Promise.resolve({ status: 'ok', message: 'Server is running' }),
      });
    });

    it('연결됨 상태가 표시된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText('연결됨')).toBeInTheDocument();
      });
    });

    it('성공 메시지가 표시된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText('Server is running')).toBeInTheDocument();
      });
    });

    it('성공 스타일(녹색 배경)이 적용된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        const statusDiv = screen.getByText('연결됨').closest('div');
        expect(statusDiv).toHaveClass('bg-green-50');
        expect(statusDiv).toHaveClass('text-green-700');
      });
    });

    it('로딩 스피너가 사라진다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        const spinner = document.querySelector('.animate-spin');
        expect(spinner).not.toBeInTheDocument();
      });
    });
  });

  describe('백엔드 연결 실패 시', () => {
    beforeEach(() => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
    });

    it('연결 실패 상태가 표시된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText('연결 실패')).toBeInTheDocument();
      });
    });

    it('에러 메시지가 표시된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText('백엔드 연결 실패')).toBeInTheDocument();
      });
    });

    it('실패 스타일(빨간 배경)이 적용된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        const statusDiv = screen.getByText('연결 실패').closest('div');
        expect(statusDiv).toHaveClass('bg-red-50');
        expect(statusDiv).toHaveClass('text-red-700');
      });
    });

    it('로딩 스피너가 사라진다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        const spinner = document.querySelector('.animate-spin');
        expect(spinner).not.toBeInTheDocument();
      });
    });
  });

  describe('API 응답이 에러 상태일 때', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValueOnce({
        json: () => Promise.resolve({ status: 'error', message: 'Database connection failed' }),
      });
    });

    it('연결 실패 상태가 표시된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText('연결 실패')).toBeInTheDocument();
      });
    });

    it('에러 메시지가 표시된다', async () => {
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText('Database connection failed')).toBeInTheDocument();
      });
    });
  });
});
