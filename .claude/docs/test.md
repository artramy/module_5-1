# 테스트 체크리스트

이 문서는 프로젝트의 모든 테스트 항목을 FE/BE/DB로 분류하여 관리합니다.

## DB 테스트 (Database)

### User CRUD 테스트
- [x] 사용자 생성 테스트 (`test_create_user`)
- [x] 중복 email 제약 테스트 (`test_create_user_duplicate_email`)
- [x] 중복 username 제약 테스트 (`test_create_user_duplicate_username`)
- [x] email로 사용자 조회 - 존재하는 경우 (`test_get_user_by_email_exists`)
- [x] email로 사용자 조회 - 존재하지 않는 경우 (`test_get_user_by_email_not_exists`)
- [x] username으로 사용자 조회 - 존재하는 경우 (`test_get_user_by_username_exists`)
- [x] username으로 사용자 조회 - 존재하지 않는 경우 (`test_get_user_by_username_not_exists`)
- [x] ID로 사용자 조회 - 존재하는 경우 (`test_get_user_by_id_exists`)
- [x] ID로 사용자 조회 - 존재하지 않는 경우 (`test_get_user_by_id_not_exists`)

### User 모델 테스트 (test_user_model.py - 11개 테스트)
- [x] User 모델 필드 검증 테스트 (4개)
- [x] User 모델 타임스탬프 자동 생성 테스트 (3개)
- [x] User 모델 unique 제약 조건 테스트 (4개)

### DB 엣지 케이스 테스트 (test_db_edge_cases.py - 28개 테스트)
- [x] NULL 값 처리 테스트 (3개)
- [x] 빈 문자열 처리 테스트 (3개)
- [x] 매우 긴 문자열 처리 테스트 (5개)
- [x] 특수문자 포함 문자열 처리 테스트 (5개)
- [x] DB 트랜잭션 롤백 테스트 (3개)
- [x] 대량 데이터 생성 성능 테스트 (5개)
- [x] CRUD 함수 엣지 케이스 테스트 (4개)

---

## BE 테스트 (Backend API)

### FastAPI 앱 테스트 (test_main.py - 12개 테스트)
- [x] FastAPI 앱 초기화 테스트 (2개)
- [x] 앱 메타데이터 (title, version) 테스트 (2개)
- [x] CORS 미들웨어 설정 테스트 (4개)
- [x] 라우터 등록 확인 테스트 (4개)

### API 엔드포인트 테스트 (test_api.py - 21개 테스트)
- [x] Health check 엔드포인트 (`GET /api/health`) 테스트 (4개)
- [x] 존재하지 않는 엔드포인트 404 테스트 (2개)
- [x] Examples 라우터 CRUD 테스트 (9개)
- [x] CORS 헤더 검증 테스트 (3개)
- [x] Database connection 테스트 (3개)

---

## FE 테스트 (Frontend)

### 메인 페이지 테스트 (src/__tests__/page.test.tsx - 15개 테스트)
- [x] 메인 페이지 렌더링 테스트 (5개)
  - 제목, 부제목, 상태 섹션 렌더링
- [x] 로딩 상태 표시 테스트 (2개)
- [x] Health check API 호출 테스트 (2개)
- [x] 성공 상태 UI 테스트 (3개)
- [x] 실패 상태 UI 테스트 (3개)

---

## 테스트 실행 방법

### DB + BE 테스트
```bash
cd backend
pytest backend/tests/ -v
```

### 특정 테스트 파일만 실행
```bash
cd backend
pytest backend/tests/test_user_crud.py -v
pytest backend/tests/test_api.py -v
```

### FE 테스트
```bash
cd frontend
npm test
```

### 모든 테스트 실행 (전체 프로젝트)
```bash
# Backend
cd backend && pytest backend/tests/ -v

# Frontend
cd ../frontend && npm test
```

---

## 테스트 통계

### 현재 테스트 현황
- **DB 테스트**: 48개 (9 + 11 + 28) ✅ 모두 통과
- **BE 테스트**: 33개 (12 + 21) ✅ 모두 통과
- **FE 테스트**: 15개 ✅ 모두 통과
- **전체**: 96개 테스트 ✅ 모두 통과

### 테스트 파일 구조
```
backend/tests/
├── conftest.py              # 테스트 픽스처
├── test_user_crud.py        # User CRUD 테스트 (9개)
├── test_user_model.py       # User 모델 테스트 (11개)
├── test_db_edge_cases.py    # DB 엣지 케이스 테스트 (28개)
├── test_main.py             # FastAPI 앱 테스트 (12개)
└── test_api.py              # API 엔드포인트 테스트 (21개)

frontend/src/__tests__/
└── page.test.tsx            # 메인 페이지 테스트 (15개)
```

### 테스트 커버리지 목표
- **DB**: 90% 이상 (목표 달성 예상)
- **BE**: 80% 이상 (목표 달성 예상)
- **FE**: 70% 이상 (목표 달성 예상)
