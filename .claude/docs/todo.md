# TODO List

## Feature: 로그인/회원가입 기능

### DB (Database)
- [ ] User 모델 생성
  - [ ] 테이블 필드 정의 (id, username, email, password_hash, created_at, updated_at)
  - [ ] 인덱스 설정 (email, username unique)
- [ ] User CRUD 함수 구현
  - [ ] create_user: 사용자 생성
  - [ ] get_user_by_email: 이메일로 사용자 조회
  - [ ] get_user_by_username: 사용자명으로 조회
  - [ ] get_user_by_id: ID로 사용자 조회
- [ ] DB 테스트 작성
  - [ ] User 모델 제약조건 테스트
  - [ ] CRUD 함수 테스트

### BE (Backend)
- [ ] 인증 관련 유틸리티 구현
  - [ ] 비밀번호 해싱 함수 (bcrypt)
  - [ ] 비밀번호 검증 함수
  - [ ] JWT 토큰 생성 함수
  - [ ] JWT 토큰 검증 함수
- [ ] Pydantic 스키마 정의
  - [ ] UserCreate: 회원가입 요청 스키마
  - [ ] UserLogin: 로그인 요청 스키마
  - [ ] UserResponse: 사용자 정보 응답 스키마
  - [ ] Token: 토큰 응답 스키마
- [ ] API 엔드포인트 구현
  - [ ] POST /api/auth/register: 회원가입
  - [ ] POST /api/auth/login: 로그인
  - [ ] GET /api/auth/me: 현재 사용자 정보 조회
  - [ ] POST /api/auth/logout: 로그아웃 (옵션)
- [ ] 미들웨어 구현
  - [ ] 인증 의존성 함수 (get_current_user)
- [ ] API 테스트 작성
  - [ ] 회원가입 테스트
  - [ ] 로그인 테스트
  - [ ] 인증된 요청 테스트

### FE (Frontend)
- [ ] 인증 관련 페이지 생성
  - [ ] /login: 로그인 페이지
  - [ ] /register: 회원가입 페이지
- [ ] 컴포넌트 구현
  - [ ] LoginForm: 로그인 폼 컴포넌트
  - [ ] RegisterForm: 회원가입 폼 컴포넌트
  - [ ] ProtectedRoute: 인증 보호 라우트 컴포넌트
- [ ] API 연동
  - [ ] 회원가입 API 호출 함수
  - [ ] 로그인 API 호출 함수
  - [ ] 사용자 정보 조회 API 함수
- [ ] 상태 관리
  - [ ] 토큰 저장/조회/삭제 (localStorage)
  - [ ] 인증 상태 관리 (Context API 또는 상태관리 라이브러리)
  - [ ] 로그인 상태에 따른 UI 변경
- [ ] 라우팅 보호
  - [ ] 비로그인 시 로그인 페이지 리다이렉트
  - [ ] 로그인 시 대시보드 리다이렉트
- [ ] 컴포넌트 테스트 작성
  - [ ] LoginForm 테스트
  - [ ] RegisterForm 테스트
  - [ ] 인증 상태 관리 테스트

---

## 작업 순서 (권장)
1. **DB 작업** (db-agent): User 모델 및 CRUD 함수 구현
2. **BE 작업** (be-agent): 인증 유틸리티 및 API 엔드포인트 구현
3. **FE 작업** (fe-agent): 로그인/회원가입 페이지 및 인증 상태 관리 구현
