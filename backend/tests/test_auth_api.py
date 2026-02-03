"""
인증 API 통합 테스트

회원가입, 로그인, 사용자 정보 조회 등 인증 관련 API의 전체 플로우를 검증합니다.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
# 모델 임포트 - 테이블 생성을 위해 필요
from app.models import Example, User  # noqa: F401


# 테스트용 인메모리 SQLite DB 설정
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 인메모리 DB에서 동일한 연결 유지
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """테스트용 DB 세션 의존성 오버라이드"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """각 테스트 전후로 DB 테이블 생성/삭제 및 의존성 오버라이드"""
    # DB 의존성 오버라이드 설정
    app.dependency_overrides[get_db] = override_get_db
    # 테이블 생성
    Base.metadata.create_all(bind=test_engine)
    yield
    # 테이블 삭제
    Base.metadata.drop_all(bind=test_engine)
    # 의존성 오버라이드 해제
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """테스트용 HTTP 클라이언트 픽스처"""
    return TestClient(app)


# 테스트에 사용할 유효한 사용자 데이터
VALID_USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
}


class TestRegisterEndpoint:
    """회원가입 엔드포인트 테스트"""

    def test_register_success(self, client):
        """
        회원가입 성공 테스트

        POST /api/auth/register
        - 유효한 username, email, password 전송
        - 201 Created 상태 코드 확인
        - access_token, token_type 반환 확인
        """
        response = client.post("/api/auth/register", json=VALID_USER_DATA)

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_register_duplicate_email_failure(self, client):
        """
        중복 email 회원가입 실패 테스트

        - 사용자 1 생성
        - 동일한 email로 사용자 2 생성 시도
        - 400 Bad Request 확인
        - 에러 메시지: "Email already registered"
        """
        # 첫 번째 사용자 생성
        client.post("/api/auth/register", json=VALID_USER_DATA)

        # 동일한 email로 두 번째 사용자 생성 시도
        duplicate_email_user = {
            "username": "differentuser",
            "email": "test@example.com",  # 동일한 email
            "password": "anotherpassword123"
        }
        response = client.post("/api/auth/register", json=duplicate_email_user)

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Email already registered"

    def test_register_duplicate_username_failure(self, client):
        """
        중복 username 회원가입 실패 테스트

        - 사용자 1 생성
        - 동일한 username으로 사용자 2 생성 시도
        - 400 Bad Request 확인
        - 에러 메시지: "Username already taken"
        """
        # 첫 번째 사용자 생성
        client.post("/api/auth/register", json=VALID_USER_DATA)

        # 동일한 username으로 두 번째 사용자 생성 시도
        duplicate_username_user = {
            "username": "testuser",  # 동일한 username
            "email": "different@example.com",
            "password": "anotherpassword123"
        }
        response = client.post("/api/auth/register", json=duplicate_username_user)

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Username already taken"

    def test_register_invalid_email_failure(self, client):
        """
        유효하지 않은 email 회원가입 실패 테스트

        - 잘못된 형식의 email (예: "notanemail")
        - 422 Unprocessable Entity 확인
        """
        invalid_email_user = {
            "username": "testuser",
            "email": "notanemail",  # 유효하지 않은 email 형식
            "password": "securepassword123"
        }
        response = client.post("/api/auth/register", json=invalid_email_user)

        assert response.status_code == 422

    def test_register_short_password_failure(self, client):
        """
        짧은 비밀번호 회원가입 실패 테스트

        - password가 8자 미만 (예: "short")
        - 422 Unprocessable Entity 확인
        """
        short_password_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"  # 8자 미만 비밀번호
        }
        response = client.post("/api/auth/register", json=short_password_user)

        assert response.status_code == 422


class TestLoginEndpoint:
    """로그인 엔드포인트 테스트"""

    def test_login_success(self, client):
        """
        로그인 성공 테스트

        - 회원가입으로 사용자 생성
        - POST /api/auth/login
        - 올바른 email, password 전송
        - 200 OK 확인
        - access_token, token_type 반환 확인
        """
        # 먼저 회원가입
        client.post("/api/auth/register", json=VALID_USER_DATA)

        # 로그인
        login_data = {
            "email": VALID_USER_DATA["email"],
            "password": VALID_USER_DATA["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password_failure(self, client):
        """
        잘못된 비밀번호 로그인 실패 테스트

        - 사용자 생성
        - 틀린 비밀번호로 로그인 시도
        - 401 Unauthorized 확인
        - 에러 메시지: "Incorrect email or password"
        """
        # 먼저 회원가입
        client.post("/api/auth/register", json=VALID_USER_DATA)

        # 틀린 비밀번호로 로그인 시도
        wrong_password_login = {
            "email": VALID_USER_DATA["email"],
            "password": "wrongpassword123"
        }
        response = client.post("/api/auth/login", json=wrong_password_login)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_nonexistent_user_failure(self, client):
        """
        존재하지 않는 사용자 로그인 실패 테스트

        - 존재하지 않는 email로 로그인 시도
        - 401 Unauthorized 확인
        - 에러 메시지: "Incorrect email or password"
        """
        nonexistent_user_login = {
            "email": "nonexistent@example.com",
            "password": "somepassword123"
        }
        response = client.post("/api/auth/login", json=nonexistent_user_login)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"


class TestMeEndpoint:
    """사용자 정보 조회 엔드포인트 테스트"""

    def test_get_me_with_valid_token(self, client):
        """
        인증된 요청으로 /me 접근 테스트

        - 회원가입으로 사용자 생성 및 토큰 받기
        - GET /api/auth/me (Authorization: Bearer <token>)
        - 200 OK 확인
        - 사용자 정보 반환 확인 (id, username, email, created_at)
        """
        # 회원가입으로 토큰 받기
        register_response = client.post("/api/auth/register", json=VALID_USER_DATA)
        token = register_response.json()["access_token"]

        # /me 엔드포인트 호출
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == VALID_USER_DATA["username"]
        assert data["email"] == VALID_USER_DATA["email"]
        assert "created_at" in data

    def test_get_me_without_token_failure(self, client):
        """
        인증 없이 /me 접근 실패 테스트

        - Authorization 헤더 없이 GET /api/auth/me
        - 401 Unauthorized 또는 403 Forbidden 확인
        """
        response = client.get("/api/auth/me")

        # HTTPBearer는 Authorization 헤더가 없으면 403 Forbidden 반환
        assert response.status_code in [401, 403]

    def test_get_me_with_invalid_token_failure(self, client):
        """
        유효하지 않은 토큰으로 /me 접근 실패 테스트

        - 잘못된 토큰으로 GET /api/auth/me
        - 401 Unauthorized 확인
        """
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        assert response.status_code == 401


class TestAuthIntegrationFlow:
    """통합 시나리오 테스트"""

    def test_full_auth_flow(self, client):
        """
        전체 플로우 테스트 (회원가입 -> 로그인 -> /me)

        - 회원가입
        - 로그인으로 새 토큰 받기
        - /me로 사용자 정보 확인
        - 전체 플로우가 정상 동작하는지 확인
        """
        # 1. 회원가입
        register_response = client.post("/api/auth/register", json=VALID_USER_DATA)
        assert register_response.status_code == 201
        register_token = register_response.json()["access_token"]
        assert len(register_token) > 0

        # 2. 로그인으로 새 토큰 받기
        login_data = {
            "email": VALID_USER_DATA["email"],
            "password": VALID_USER_DATA["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]
        assert len(login_token) > 0

        # 3. 회원가입 토큰으로 /me 접근
        me_response_with_register_token = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {register_token}"}
        )
        assert me_response_with_register_token.status_code == 200
        user_data = me_response_with_register_token.json()
        assert user_data["username"] == VALID_USER_DATA["username"]
        assert user_data["email"] == VALID_USER_DATA["email"]

        # 4. 로그인 토큰으로 /me 접근 (동일한 사용자 정보 반환)
        me_response_with_login_token = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert me_response_with_login_token.status_code == 200
        user_data_login = me_response_with_login_token.json()

        # 동일한 사용자 정보여야 함
        assert user_data_login["id"] == user_data["id"]
        assert user_data_login["username"] == user_data["username"]
        assert user_data_login["email"] == user_data["email"]

    def test_multiple_users_registration(self, client):
        """
        여러 사용자 회원가입 테스트

        - 여러 사용자를 생성하고 각각 고유한 정보를 가지는지 확인
        """
        users = [
            {"username": "user1", "email": "user1@example.com", "password": "password123"},
            {"username": "user2", "email": "user2@example.com", "password": "password456"},
            {"username": "user3", "email": "user3@example.com", "password": "password789"},
        ]

        tokens = []
        for user_data in users:
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 201
            tokens.append(response.json()["access_token"])

        # 각 토큰으로 /me 접근하여 올바른 사용자 정보 반환 확인
        for i, token in enumerate(tokens):
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == users[i]["username"]
            assert data["email"] == users[i]["email"]

    def test_token_from_different_user_returns_different_data(self, client):
        """
        다른 사용자의 토큰으로 다른 사용자 정보가 반환되는지 확인
        """
        # 첫 번째 사용자 생성
        user1_data = {"username": "user1", "email": "user1@example.com", "password": "password123"}
        user1_response = client.post("/api/auth/register", json=user1_data)
        user1_token = user1_response.json()["access_token"]

        # 두 번째 사용자 생성
        user2_data = {"username": "user2", "email": "user2@example.com", "password": "password456"}
        user2_response = client.post("/api/auth/register", json=user2_data)
        user2_token = user2_response.json()["access_token"]

        # 각 토큰으로 /me 접근
        user1_me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user1_token}"}
        ).json()

        user2_me = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {user2_token}"}
        ).json()

        # 서로 다른 사용자 정보여야 함
        assert user1_me["id"] != user2_me["id"]
        assert user1_me["username"] != user2_me["username"]
        assert user1_me["email"] != user2_me["email"]
