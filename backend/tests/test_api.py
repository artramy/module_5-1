"""
API 엔드포인트 테스트

Health check, Examples API 및 기타 API 엔드포인트를 테스트합니다.
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


class TestHealthCheckEndpoint:
    """Health check 엔드포인트 테스트"""

    def test_health_check_returns_200(self, client):
        """GET /api/health가 200 상태 코드를 반환하는지 확인"""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self, client):
        """GET /api/health 응답 구조 확인"""
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert "message" in data

    def test_health_check_status_ok(self, client):
        """GET /api/health의 status가 'ok'인지 확인"""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_message(self, client):
        """GET /api/health의 message가 올바른지 확인"""
        response = client.get("/api/health")
        data = response.json()
        assert "FastAPI" in data["message"]


class TestNotFoundEndpoint:
    """존재하지 않는 엔드포인트 테스트"""

    def test_nonexistent_endpoint_returns_404(self, client):
        """존재하지 않는 엔드포인트가 404를 반환하는지 확인"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_nonexistent_endpoint_error_detail(self, client):
        """404 응답에 detail이 포함되어 있는지 확인"""
        response = client.get("/api/nonexistent")
        data = response.json()
        assert "detail" in data


class TestExamplesAPI:
    """Examples API 엔드포인트 테스트"""

    def test_get_examples_empty_list(self, client):
        """GET /api/examples/가 빈 리스트를 반환하는지 확인"""
        response = client.get("/api/examples/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_example(self, client):
        """POST /api/examples/로 example 생성"""
        example_data = {
            "name": "Test Example",
            "description": "This is a test example"
        }
        response = client.post("/api/examples/", json=example_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Test Example"
        assert data["description"] == "This is a test example"
        assert "id" in data
        assert "created_at" in data

    def test_create_example_without_description(self, client):
        """description 없이 example 생성"""
        example_data = {"name": "No Description Example"}
        response = client.post("/api/examples/", json=example_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "No Description Example"
        assert data["description"] is None

    def test_get_example_by_id(self, client):
        """GET /api/examples/{id}로 특정 example 조회"""
        # 먼저 example 생성
        create_response = client.post(
            "/api/examples/",
            json={"name": "Get By ID Example", "description": "Test"}
        )
        example_id = create_response.json()["id"]

        # ID로 조회
        response = client.get(f"/api/examples/{example_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == example_id
        assert data["name"] == "Get By ID Example"

    def test_get_example_not_found(self, client):
        """존재하지 않는 example ID 조회 시 404 반환"""
        response = client.get("/api/examples/99999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Example not found"

    def test_delete_example(self, client):
        """DELETE /api/examples/{id}로 example 삭제"""
        # 먼저 example 생성
        create_response = client.post(
            "/api/examples/",
            json={"name": "To Be Deleted", "description": "Delete me"}
        )
        example_id = create_response.json()["id"]

        # 삭제
        delete_response = client.delete(f"/api/examples/{example_id}")
        assert delete_response.status_code == 200

        data = delete_response.json()
        assert "message" in data

        # 삭제 후 조회 시 404
        get_response = client.get(f"/api/examples/{example_id}")
        assert get_response.status_code == 404

    def test_delete_example_not_found(self, client):
        """존재하지 않는 example 삭제 시 404 반환"""
        response = client.delete("/api/examples/99999")
        assert response.status_code == 404

    def test_get_examples_after_create(self, client):
        """example 생성 후 목록 조회"""
        # 여러 example 생성
        client.post("/api/examples/", json={"name": "Example 1"})
        client.post("/api/examples/", json={"name": "Example 2"})
        client.post("/api/examples/", json={"name": "Example 3"})

        # 목록 조회
        response = client.get("/api/examples/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3

    def test_create_example_invalid_data(self, client):
        """잘못된 데이터로 example 생성 시 422 반환"""
        # name 필드 누락
        response = client.post("/api/examples/", json={"description": "No name"})
        assert response.status_code == 422


class TestCORSHeaders:
    """CORS 헤더 검증 테스트"""

    def test_cors_headers_on_get_request(self, client):
        """GET 요청에 CORS 헤더가 포함되는지 확인"""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_headers_on_post_request(self, client):
        """POST 요청에 CORS 헤더가 포함되는지 확인"""
        response = client.post(
            "/api/examples/",
            json={"name": "CORS Test"},
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_preflight_request(self, client):
        """OPTIONS preflight 요청 처리 확인"""
        response = client.options(
            "/api/examples/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert "POST" in response.headers.get("access-control-allow-methods", "")


class TestDatabaseConnection:
    """데이터베이스 연결 테스트"""

    def test_database_connection_works(self, client):
        """DB 연결이 정상 작동하는지 확인 (예: 데이터 생성/조회)"""
        # 데이터 생성
        create_response = client.post(
            "/api/examples/",
            json={"name": "DB Connection Test"}
        )
        assert create_response.status_code == 200
        example_id = create_response.json()["id"]

        # 데이터 조회
        get_response = client.get(f"/api/examples/{example_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "DB Connection Test"

    def test_database_persistence_within_test(self, client):
        """테스트 내에서 데이터가 유지되는지 확인"""
        # 여러 데이터 생성
        for i in range(5):
            client.post("/api/examples/", json={"name": f"Persistence Test {i}"})

        # 모든 데이터 조회
        response = client.get("/api/examples/")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_database_isolation_between_tests(self, client):
        """테스트 간 DB가 격리되는지 확인 (이 테스트는 비어있어야 함)"""
        response = client.get("/api/examples/")
        assert response.status_code == 200
        # setup_test_db 픽스처가 각 테스트 전에 DB를 초기화하므로 비어있어야 함
        assert response.json() == []
