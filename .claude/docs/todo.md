# TODO List

## Feature: 로그인/회원가입 기능

### DB (Database)
- [x] User 모델 생성
  - [x] 테이블 필드 정의 (id, username, email, password_hash, created_at, updated_at)
  - [x] 인덱스 설정 (email, username unique)
- [x] User CRUD 함수 구현
  - [x] create_user: 사용자 생성
  - [x] get_user_by_email: 이메일로 사용자 조회
  - [x] get_user_by_username: 사용자명으로 조회
  - [x] get_user_by_id: ID로 사용자 조회
- [x] DB 테스트 작성
  - [x] User 모델 제약조건 테스트
  - [x] CRUD 함수 테스트

### BE (Backend)
- [x] 인증 관련 유틸리티 구현
  - [x] 비밀번호 해싱 함수 (bcrypt)
  - [x] 비밀번호 검증 함수
  - [x] JWT 토큰 생성 함수
  - [x] JWT 토큰 검증 함수
- [x] Pydantic 스키마 정의
  - [x] UserCreate: 회원가입 요청 스키마
  - [x] UserLogin: 로그인 요청 스키마
  - [x] UserResponse: 사용자 정보 응답 스키마
  - [x] Token: 토큰 응답 스키마
- [x] API 엔드포인트 구현
  - [x] POST /api/auth/register: 회원가입
  - [x] POST /api/auth/login: 로그인
  - [x] GET /api/auth/me: 현재 사용자 정보 조회
  - [ ] POST /api/auth/logout: 로그아웃 (옵션 - 클라이언트에서 토큰 삭제로 구현됨)
- [x] 미들웨어 구현
  - [x] 인증 의존성 함수 (get_current_user)
- [x] API 테스트 작성
  - [x] 회원가입 테스트
  - [x] 로그인 테스트
  - [x] 인증된 요청 테스트

### FE (Frontend)
- [x] 인증 관련 페이지 생성
  - [x] /login: 로그인 페이지
  - [x] /register: 회원가입 페이지
- [x] 컴포넌트 구현
  - [x] LoginForm: 로그인 폼 컴포넌트 (page.tsx에 통합)
  - [x] RegisterForm: 회원가입 폼 컴포넌트 (page.tsx에 통합)
  - [x] ProtectedRoute: 인증 보호 라우트 컴포넌트
  - [x] Navbar: 네비게이션 바 컴포넌트
- [x] API 연동
  - [x] 회원가입 API 호출 함수
  - [x] 로그인 API 호출 함수
  - [x] 사용자 정보 조회 API 함수
- [x] 상태 관리
  - [x] 토큰 저장/조회/삭제 (localStorage)
  - [x] 인증 상태 관리 (Context API)
  - [x] 로그인 상태에 따른 UI 변경
- [x] 라우팅 보호
  - [x] 비로그인 시 로그인 페이지 리다이렉트
  - [x] 로그인 시 메인 페이지 리다이렉트
- [x] 컴포넌트 테스트 작성
  - [x] 메인 페이지 테스트 (기존 test.md 참조)

---

## 작업 순서 (권장)
1. **DB 작업** (db-agent): User 모델 및 CRUD 함수 구현 ✅ **완료**
2. **BE 작업** (be-agent): 인증 유틸리티 및 API 엔드포인트 구현 ✅ **완료**
3. **FE 작업** (fe-agent): 로그인/회원가입 페이지 및 인증 상태 관리 구현 ✅ **완료**

---

## 🎉 로그인/인증 시스템 구현 완료!

### 구현된 기능
- ✅ 회원가입 (username, email, password)
- ✅ 로그인 (email, password)
- ✅ JWT 토큰 기반 인증
- ✅ 사용자 정보 조회 (/api/auth/me)
- ✅ 로그아웃 (클라이언트에서 토큰 삭제)
- ✅ 자동 로그인 (localStorage 토큰 유지)
- ✅ 인증 보호 라우트 (ProtectedRoute)
- ✅ 네비게이션 바 (로그인 상태별 UI)

### 테스트 커버리지
- ✅ DB 테스트: 48개 통과
- ✅ BE 테스트: 47개 통과 (33 + 14)
- ✅ FE 테스트: 15개 통과
- **총 110개 테스트 통과**

### 실행 방법
```bash
# Backend
cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### 접속 URL
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
