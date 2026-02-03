// 타입 정의 - Auth
interface RegisterData {
  username: string;
  email: string;
  password: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

// 타입 정의 - Activity
export interface Activity {
  id: number;
  user_id: number;
  action_type: string;
  description: string | null;
  extra_data: Record<string, any> | null;
  created_at: string; // ISO date string
}

export interface ActivityCreateData {
  action_type: string;
  description?: string;
  extra_data?: Record<string, any>;
}

export interface ActivityStats {
  total_count: number;
  by_type: Record<string, number>;
  by_date: Record<string, number>;
  most_common_action: string | null;
}

// API Base URLs
const API_BASE_URL = '/api/auth';
const DASHBOARD_API_URL = '/api/dashboard';

/**
 * 회원가입 API 호출
 */
export async function register(data: RegisterData): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return response.json();
}

/**
 * 로그인 API 호출
 */
export async function login(data: LoginData): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

/**
 * 현재 사용자 정보 조회 API 호출
 */
export async function getCurrentUser(token: string): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get user info');
  }

  return response.json();
}

// ============================================
// Activity API Functions
// ============================================

/**
 * 인증 토큰을 localStorage에서 가져오는 헬퍼 함수
 */
function getAuthToken(): string {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }
  return token;
}

/**
 * 인증된 요청에 대한 응답 처리 헬퍼 함수
 * 401 에러 시 로그인 페이지로 리다이렉트
 */
async function handleAuthenticatedResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    // 인증 실패 시 토큰 제거 및 로그인 페이지로 리다이렉트
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  // 204 No Content의 경우 빈 응답 반환
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * Activity 생성 API 호출
 * POST /api/dashboard/activities
 */
export async function createActivity(data: ActivityCreateData): Promise<Activity> {
  const token = getAuthToken();

  const response = await fetch(`${DASHBOARD_API_URL}/activities`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  return handleAuthenticatedResponse<Activity>(response);
}

/**
 * Activity 목록 조회 API 호출
 * GET /api/dashboard/activities?limit={limit}&offset={offset}
 */
export async function getActivities(limit: number = 50, offset: number = 0): Promise<Activity[]> {
  const token = getAuthToken();

  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });

  const response = await fetch(`${DASHBOARD_API_URL}/activities?${params}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  return handleAuthenticatedResponse<Activity[]>(response);
}

/**
 * 단일 Activity 조회 API 호출
 * GET /api/dashboard/activities/{id}
 */
export async function getActivity(id: number): Promise<Activity> {
  const token = getAuthToken();

  const response = await fetch(`${DASHBOARD_API_URL}/activities/${id}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  return handleAuthenticatedResponse<Activity>(response);
}

/**
 * Activity 통계 조회 API 호출
 * GET /api/dashboard/stats?start_date={startDate}&end_date={endDate}
 */
export async function getActivityStats(startDate?: string, endDate?: string): Promise<ActivityStats> {
  const token = getAuthToken();

  const params = new URLSearchParams();
  if (startDate) {
    params.append('start_date', startDate);
  }
  if (endDate) {
    params.append('end_date', endDate);
  }

  const queryString = params.toString();
  const url = queryString
    ? `${DASHBOARD_API_URL}/stats?${queryString}`
    : `${DASHBOARD_API_URL}/stats`;

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  return handleAuthenticatedResponse<ActivityStats>(response);
}

/**
 * Activity 삭제 API 호출
 * DELETE /api/dashboard/activities/{id}
 */
export async function deleteActivity(id: number): Promise<void> {
  const token = getAuthToken();

  const response = await fetch(`${DASHBOARD_API_URL}/activities/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  return handleAuthenticatedResponse<void>(response);
}
