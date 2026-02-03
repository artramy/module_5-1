# TODO List - AI 행동 추적 시스템

## Feature: 대시보드 (Dashboard)

사용자의 AI 활동을 추적하고 시각화하는 대시보드 기능

---

### DB (Database)

#### 1. Activity 모델 생성 ✅
- [x] 테이블 필드 정의
  - [x] id: 고유 식별자 (Integer, Primary Key)
  - [x] user_id: 사용자 ID (Integer, Foreign Key → User)
  - [x] action_type: 행동 유형 (String) - 예: "login", "query", "click" 등
  - [x] description: 행동 설명 (Text, nullable)
  - [x] extra_data: 추가 정보 (JSON, nullable) - 예: IP, 브라우저 정보 등 ⚠️ metadata → extra_data로 변경
  - [x] created_at: 생성 시간 (DateTime, default=now)
- [x] 인덱스 설정
  - [x] user_id 인덱스 (검색 성능 향상)
  - [x] created_at 인덱스 (시간별 조회)
  - [x] action_type 인덱스 (유형별 필터링)

#### 2. Activity CRUD 함수 구현 ✅
- [x] create_activity: 활동 기록 생성
  - [x] user_id, action_type, description, extra_data 파라미터
  - [x] Activity 객체 반환
- [x] get_activities_by_user: 사용자별 활동 조회
  - [x] user_id, limit, offset 파라미터
  - [x] 최신순 정렬
  - [x] 페이지네이션 지원
- [x] get_activity_by_id: 특정 활동 조회
  - [x] activity_id 파라미터
  - [x] Activity 객체 또는 None 반환
- [x] get_activities_by_type: 유형별 활동 조회
  - [x] user_id, action_type, limit, offset 파라미터
  - [x] 필터링된 활동 목록 반환
- [x] get_activity_stats: 사용자 활동 통계
  - [x] user_id, start_date, end_date 파라미터
  - [x] 유형별 카운트, 일별 카운트 등 통계 반환
- [x] delete_old_activities: 오래된 활동 삭제
  - [x] days 파라미터 (예: 90일 이전 데이터 삭제)
  - [x] 삭제된 개수 반환

#### 3. DB 테스트 작성 ✅
- [x] Activity 모델 테스트
  - [x] 필드 존재 여부 테스트
  - [x] Foreign Key 관계 테스트 (User)
  - [x] created_at 자동 생성 테스트
- [x] Activity CRUD 테스트
  - [x] create_activity 테스트
  - [x] get_activities_by_user 페이지네이션 테스트
  - [x] get_activities_by_type 필터링 테스트
  - [x] get_activity_stats 통계 계산 테스트
  - [x] delete_old_activities 테스트
- **총 33개 테스트 통과 ✅**

---

### BE (Backend)

#### 1. Pydantic 스키마 정의 ✅
- [x] ActivityCreate 스키마
  - [x] action_type: str (필수)
  - [x] description: str | None (선택)
  - [x] extra_data: dict | None (선택) ⚠️ metadata → extra_data로 변경
- [x] ActivityResponse 스키마
  - [x] id: int
  - [x] user_id: int
  - [x] action_type: str
  - [x] description: str | None
  - [x] extra_data: dict | None
  - [x] created_at: datetime
  - [x] from_attributes = True 설정
- [x] ActivityStats 스키마
  - [x] total_count: int
  - [x] by_type: dict[str, int] (유형별 카운트)
  - [x] by_date: dict[str, int] (날짜별 카운트)
  - [x] most_common_action: str (가장 많은 행동)

#### 2. Dashboard API 엔드포인트 구현 ✅
- [x] POST /api/dashboard/activities
  - [x] 활동 기록 생성
  - [x] 인증 필요 (get_current_user)
  - [x] ActivityCreate 요청 받기
  - [x] ActivityResponse 반환 (201 Created)
- [x] GET /api/dashboard/activities
  - [x] 현재 사용자의 활동 목록 조회
  - [x] 인증 필요
  - [x] Query params: limit (default=50), offset (default=0)
  - [x] List[ActivityResponse] 반환
- [x] GET /api/dashboard/activities/{activity_id}
  - [x] 특정 활동 상세 조회
  - [x] 인증 필요
  - [x] 본인 활동만 조회 가능 (권한 체크)
  - [x] ActivityResponse 반환 또는 404
- [x] GET /api/dashboard/stats
  - [x] 사용자 활동 통계 조회
  - [x] 인증 필요
  - [x] Query params: start_date, end_date (선택)
  - [x] ActivityStats 반환
- [x] DELETE /api/dashboard/activities/{activity_id}
  - [x] 특정 활동 삭제
  - [x] 인증 필요
  - [x] 본인 활동만 삭제 가능
  - [x] 204 No Content 반환

#### 3. Activity Logging 미들웨어/데코레이터 ✅
- [x] @log_activity 데코레이터 구현
  - [x] 자동으로 활동 기록
  - [x] action_type 자동 추출 (함수명 또는 명시)
  - [x] 비동기 지원
  - [x] include_args 옵션 (함수 인자 포함)
  - [x] 민감 정보 필터링 (password, db, current_user)
- [x] ActivityLogger 유틸리티 클래스
  - [x] log_login: 로그인 활동 기록
  - [x] log_api_call: API 호출 기록
  - [x] log_error: 에러 발생 기록

#### 4. BE 테스트 작성 ✅
- [x] Dashboard API 테스트
  - [x] POST /api/dashboard/activities 테스트 (5개)
  - [x] GET /api/dashboard/activities 페이지네이션 테스트 (5개)
  - [x] GET /api/dashboard/activities/{id} 권한 체크 테스트 (4개)
  - [x] GET /api/dashboard/stats 통계 계산 테스트 (4개)
  - [x] DELETE /api/dashboard/activities/{id} 권한 체크 테스트 (5개)
- [x] 통합 테스트 (3개)
  - [x] 활동 생성 → 조회 → 통계 확인 플로우
  - [x] 다른 사용자의 활동 접근 불가 테스트
  - [x] 통계에 자신의 활동만 포함되는지 테스트
- **총 26개 테스트 통과 ✅**

---

### FE (Frontend)

#### 1. API 연동 유틸리티 ✅
- [x] Activity API 함수 작성 (`frontend/src/lib/api.ts` 확장)
  - [x] createActivity(data): 활동 생성
  - [x] getActivities(limit, offset): 활동 목록 조회
  - [x] getActivity(id): 활동 상세 조회
  - [x] getActivityStats(startDate?, endDate?): 통계 조회
  - [x] deleteActivity(id): 활동 삭제
  - [x] TypeScript 타입 정의 (Activity, ActivityCreateData, ActivityStats)
  - [x] 인증 헤더 자동 포함
  - [x] 401 에러 시 자동 로그인 리다이렉트

#### 2. 대시보드 페이지 생성 ✅
- [x] /dashboard 페이지 생성 (`frontend/src/app/dashboard/page.tsx`)
  - [x] ProtectedRoute로 보호 (로그인 필요)
  - [x] 레이아웃 구성
    - [x] 상단: 통계 카드 (총 활동 수, 오늘 활동 수, 가장 많은 행동)
    - [x] 중간: 활동 차트 (Recharts 사용, Date/Type 토글)
    - [x] 하단: 최근 활동 목록 (테이블 + Load More)
  - [x] 새로고침 버튼
  - [x] 에러 처리 및 재시도
  - [x] 반응형 레이아웃 (모바일 대응)

#### 3. 대시보드 컴포넌트 구현 ✅
- [x] StatCard 컴포넌트 (`components/dashboard/StatCard.tsx`)
  - [x] Props: title, value, icon, trend (증감률)
  - [x] Tailwind CSS 스타일링
  - [x] 로딩 스켈레톤
  - [x] Trend 색상 코딩 (긍정/부정)
- [x] ActivityChart 컴포넌트 (`components/dashboard/ActivityChart.tsx`)
  - [x] Props: data (날짜별/유형별 활동 데이터)
  - [x] Recharts 연동 (LineChart, BarChart)
  - [x] 반응형 디자인
  - [x] 날짜 포맷팅 (date-fns)
  - [x] Empty state 처리
- [x] ActivityList 컴포넌트 (`components/dashboard/ActivityList.tsx`)
  - [x] Props: activities (활동 배열)
  - [x] 데스크톱: 테이블 형태
  - [x] 모바일: 카드 형태 (반응형)
  - [x] 컬럼: 행동 유형, 설명, 시간
  - [x] Load More 페이지네이션
  - [x] 삭제 버튼
  - [x] Empty/Loading states
- [x] ActivityDetail 모달 컴포넌트 (`components/dashboard/ActivityDetail.tsx`)
  - [x] Props: activity (상세 활동 정보), onClose
  - [x] extra_data JSON 포맷 표시
  - [x] 삭제 버튼 (확인 다이얼로그)
  - [x] 애니메이션 (enter/exit)
  - [x] ESC 키 및 backdrop 클릭으로 닫기

#### 4. 상태 관리 ✅
- [x] useDashboard 커스텀 훅 (`hooks/useDashboard.ts`)
  - [x] 활동 목록 상태 관리
  - [x] 통계 상태 관리
  - [x] 로딩/에러 상태 관리
  - [x] 페이지네이션 로직 (Load More)
  - [x] CRUD 작업 (fetch, create, delete)
  - [x] refreshData() 함수
  - [x] Auto-fetch on mount

#### 5. 자동 활동 추적 (Optional - 보류)
- [ ] useActivityTracker 훅 (`hooks/useActivityTracker.ts`)
  - [ ] 페이지 방문 자동 기록
  - [ ] 버튼 클릭 추적
  - [ ] API 호출 추적 (optional)
- [ ] ActivityTracker Provider
  - [ ] 전역에서 활동 추적 활성화
  - [ ] 설정 가능 (추적 활성/비활성)

#### 6. 네비게이션 업데이트 ✅
- [x] Navbar에 대시보드 링크 추가
  - [x] 로그인 상태에서만 표시
  - [x] 아이콘 (차트 SVG) + "대시보드" 텍스트
  - [x] Active state 하이라이팅
  - [x] 반응형 (모바일에서 텍스트 숨김)

#### 7. FE 테스트 작성
- [ ] 대시보드 페이지 테스트
  - [ ] 렌더링 테스트
  - [ ] 통계 카드 표시 테스트
  - [ ] 활동 목록 표시 테스트
- [ ] 컴포넌트 단위 테스트
  - [ ] StatCard 렌더링 테스트
  - [ ] ActivityList 페이지네이션 테스트
  - [ ] ActivityChart 데이터 표시 테스트

---

## 의존성 및 라이브러리

### Backend ✅
- [x] 추가 패키지 없음 (기존 FastAPI, SQLAlchemy 사용)

### Frontend ✅
- [x] 차트 라이브러리 선택 및 설치
  - [x] recharts (`npm install recharts`) ✅ 선택됨
- [x] 날짜 처리 라이브러리
  - [x] date-fns ✅ 설치됨

---

## 작업 순서 (권장)

### Phase 1: DB 기반 구축 ✅ **완료**
1. ✅ Activity 모델 생성
2. ✅ Activity CRUD 함수 구현
3. ✅ DB 테스트 작성 (33개 테스트 통과)

### Phase 2: BE API 구현 ✅ **완료**
1. ✅ Pydantic 스키마 정의
2. ✅ Dashboard API 엔드포인트 구현 (5개 API)
3. ✅ Activity Logging 유틸리티 구현 (optional)
4. ✅ BE 테스트 작성 (26개 테스트 통과)

### Phase 3: FE 화면 구현 🔄 **진행 중** (6/7 완료)
1. ✅ API 연동 함수 작성
2. ✅ 차트 라이브러리 설치 (recharts, date-fns)
3. ✅ 대시보드 페이지 생성
4. ✅ 컴포넌트 구현 (StatCard, ActivityChart, ActivityList, ActivityDetail)
5. ✅ 상태 관리 (useDashboard 훅)
6. ✅ 네비게이션 업데이트
7. ⏳ FE 테스트 작성

---

## 검증 방법

### Phase 1 검증
```bash
cd backend
pytest backend/tests/test_activity_crud.py -v
```

### Phase 2 검증
1. Swagger UI: http://localhost:8000/docs
2. POST /api/dashboard/activities로 활동 생성
3. GET /api/dashboard/activities로 목록 조회
4. GET /api/dashboard/stats로 통계 확인
5. 통합 테스트: `pytest backend/tests/test_dashboard_api.py -v`

### Phase 3 검증
1. Frontend 실행: `npm run dev`
2. http://localhost:3000/dashboard 접속
3. 통계 카드 표시 확인
4. 활동 차트 표시 확인
5. 활동 목록 표시 확인
6. 페이지네이션 동작 확인

---

## 추가 기능 아이디어 (Optional)

- [ ] 활동 필터링 (날짜 범위, 유형별)
- [ ] 활동 검색 기능
- [ ] 활동 데이터 CSV/JSON 내보내기
- [ ] 실시간 활동 알림 (WebSocket)
- [ ] 활동 히트맵 (시간대별 활동 시각화)
- [ ] 사용자별 활동 비교 (관리자용)
