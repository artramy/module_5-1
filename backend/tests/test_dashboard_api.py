"""
Dashboard API 통합 테스트

Dashboard 기능 관련 API의 전체 플로우를 검증합니다.
- 활동 생성 (POST /api/dashboard/activities)
- 활동 목록 조회 (GET /api/dashboard/activities)
- 활동 상세 조회 (GET /api/dashboard/activities/{activity_id})
- 활동 통계 조회 (GET /api/dashboard/stats)
- 활동 삭제 (DELETE /api/dashboard/activities/{activity_id})
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
# 모델 임포트 - 테이블 생성을 위해 필요
from app.models import Example, User, Activity  # noqa: F401


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
USER1_DATA = {
    "username": "testuser1",
    "email": "user1@example.com",
    "password": "securepassword123"
}

USER2_DATA = {
    "username": "testuser2",
    "email": "user2@example.com",
    "password": "securepassword456"
}


@pytest.fixture
def auth_token(client):
    """인증된 사용자의 JWT 토큰을 반환하는 픽스처"""
    # 회원가입
    response = client.post("/api/auth/register", json=USER1_DATA)
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """인증 헤더를 반환하는 픽스처"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def second_user_auth_token(client):
    """두 번째 사용자의 JWT 토큰을 반환하는 픽스처"""
    response = client.post("/api/auth/register", json=USER2_DATA)
    return response.json()["access_token"]


@pytest.fixture
def second_user_auth_headers(second_user_auth_token):
    """두 번째 사용자의 인증 헤더를 반환하는 픽스처"""
    return {"Authorization": f"Bearer {second_user_auth_token}"}


# 테스트용 활동 데이터
VALID_ACTIVITY_DATA = {
    "action_type": "login",
    "description": "User logged in",
    "extra_data": {"ip": "127.0.0.1", "browser": "Chrome"}
}


class TestCreateActivityEndpoint:
    """POST /api/dashboard/activities 엔드포인트 테스트"""

    def test_create_activity_success(self, client, auth_headers):
        """
        활동 생성 성공 테스트

        POST /api/dashboard/activities
        - 유효한 action_type, description, extra_data 전송
        - 201 Created 상태 코드 확인
        - 생성된 활동 정보 반환 확인
        """
        response = client.post(
            "/api/dashboard/activities",
            json=VALID_ACTIVITY_DATA,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["action_type"] == VALID_ACTIVITY_DATA["action_type"]
        assert data["description"] == VALID_ACTIVITY_DATA["description"]
        assert data["extra_data"] == VALID_ACTIVITY_DATA["extra_data"]
        assert "user_id" in data
        assert "created_at" in data

    def test_create_activity_without_auth_failure(self, client):
        """
        인증 없이 활동 생성 실패 테스트

        - Authorization 헤더 없이 POST /api/dashboard/activities
        - 401 Unauthorized 또는 403 Forbidden 확인
        """
        response = client.post(
            "/api/dashboard/activities",
            json=VALID_ACTIVITY_DATA
        )

        # HTTPBearer는 Authorization 헤더가 없으면 403 Forbidden 반환
        assert response.status_code in [401, 403]

    def test_create_activity_missing_action_type_failure(self, client, auth_headers):
        """
        action_type 누락 시 활동 생성 실패 테스트

        - action_type 필드 없이 요청
        - 422 Unprocessable Entity 확인
        """
        invalid_data = {
            "description": "Missing action_type"
        }
        response = client.post(
            "/api/dashboard/activities",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_activity_extra_data_is_json(self, client, auth_headers):
        """
        extra_data가 JSON 형식인지 확인 테스트

        - extra_data에 딕셔너리 전송
        - 응답에서 extra_data가 딕셔너리로 반환되는지 확인
        """
        activity_data = {
            "action_type": "page_view",
            "extra_data": {"page": "/dashboard", "duration": 120, "scroll_depth": 0.8}
        }
        response = client.post(
            "/api/dashboard/activities",
            json=activity_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert isinstance(data["extra_data"], dict)
        assert data["extra_data"]["page"] == "/dashboard"
        assert data["extra_data"]["duration"] == 120
        assert data["extra_data"]["scroll_depth"] == 0.8

    def test_create_activity_without_optional_fields(self, client, auth_headers):
        """
        선택 필드 없이 활동 생성 테스트

        - description, extra_data 없이 action_type만 전송
        - 201 Created 확인
        """
        minimal_data = {"action_type": "click"}
        response = client.post(
            "/api/dashboard/activities",
            json=minimal_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["action_type"] == "click"
        assert data["description"] is None
        assert data["extra_data"] is None


class TestGetActivitiesEndpoint:
    """GET /api/dashboard/activities 엔드포인트 테스트"""

    def test_get_activities_success(self, client, auth_headers):
        """
        활동 목록 조회 성공 테스트

        GET /api/dashboard/activities
        - 200 OK 상태 코드 확인
        - 리스트 형태로 반환 확인
        """
        response = client.get(
            "/api/dashboard/activities",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_activities_pagination(self, client, auth_headers):
        """
        페이지네이션 동작 테스트 (limit, offset)

        - 여러 활동 생성 후 limit, offset으로 조회
        - 올바른 개수가 반환되는지 확인
        """
        # 10개 활동 생성
        for i in range(10):
            client.post(
                "/api/dashboard/activities",
                json={"action_type": f"action_{i}"},
                headers=auth_headers
            )

        # limit=5로 조회
        response = client.get(
            "/api/dashboard/activities?limit=5",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # offset=3, limit=5로 조회
        response = client.get(
            "/api/dashboard/activities?limit=5&offset=3",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # offset=8, limit=5로 조회 (남은 것 2개)
        response = client.get(
            "/api/dashboard/activities?limit=5&offset=8",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_activities_sorted_by_latest(self, client, auth_headers):
        """
        최신순 정렬 확인 테스트

        - 여러 활동 생성 후 조회
        - created_at 기준 내림차순 정렬 확인
        """
        # 활동 생성
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "first_action"},
            headers=auth_headers
        )
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "second_action"},
            headers=auth_headers
        )
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "third_action"},
            headers=auth_headers
        )

        response = client.get(
            "/api/dashboard/activities",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 최신순 정렬 확인 (third_action이 첫 번째)
        assert len(data) == 3
        assert data[0]["action_type"] == "third_action"
        assert data[1]["action_type"] == "second_action"
        assert data[2]["action_type"] == "first_action"

    def test_get_activities_without_auth_failure(self, client):
        """
        인증 없이 활동 목록 조회 실패 테스트

        - Authorization 헤더 없이 GET /api/dashboard/activities
        - 401 또는 403 확인
        """
        response = client.get("/api/dashboard/activities")
        assert response.status_code in [401, 403]

    def test_get_activities_does_not_show_other_users_activities(
        self, client, auth_headers, second_user_auth_headers
    ):
        """
        다른 사용자의 활동은 조회되지 않음 테스트

        - user1이 활동 생성
        - user2가 목록 조회 시 user1의 활동이 나타나지 않음
        """
        # user1이 활동 생성
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "user1_action"},
            headers=auth_headers
        )

        # user2가 목록 조회
        response = client.get(
            "/api/dashboard/activities",
            headers=second_user_auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        # user2는 활동이 없어야 함
        assert len(data) == 0


class TestGetActivityDetailEndpoint:
    """GET /api/dashboard/activities/{activity_id} 엔드포인트 테스트"""

    def test_get_activity_detail_success(self, client, auth_headers):
        """
        활동 상세 조회 성공 테스트

        GET /api/dashboard/activities/{activity_id}
        - 200 OK 상태 코드 확인
        - 올바른 활동 정보 반환 확인
        """
        # 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json=VALID_ACTIVITY_DATA,
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # 상세 조회
        response = client.get(
            f"/api/dashboard/activities/{activity_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == activity_id
        assert data["action_type"] == VALID_ACTIVITY_DATA["action_type"]
        assert data["description"] == VALID_ACTIVITY_DATA["description"]
        assert data["extra_data"] == VALID_ACTIVITY_DATA["extra_data"]

    def test_get_activity_detail_not_found(self, client, auth_headers):
        """
        존재하지 않는 activity_id로 조회 시 404 테스트

        - 존재하지 않는 ID로 GET /api/dashboard/activities/{id}
        - 404 Not Found 확인
        """
        response = client.get(
            "/api/dashboard/activities/99999",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_get_activity_detail_other_user_forbidden(
        self, client, auth_headers, second_user_auth_headers
    ):
        """
        다른 사용자의 활동 조회 시 403 Forbidden 테스트

        - user1이 활동 생성
        - user2가 user1의 활동 조회 시도
        - 403 Forbidden 확인
        """
        # user1이 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "user1_private_action"},
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # user2가 user1의 활동 조회 시도
        response = client.get(
            f"/api/dashboard/activities/{activity_id}",
            headers=second_user_auth_headers
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authorized to access this activity"

    def test_get_activity_detail_without_auth_failure(self, client, auth_headers):
        """
        인증 없이 활동 상세 조회 실패 테스트

        - Authorization 헤더 없이 GET /api/dashboard/activities/{id}
        - 401 또는 403 확인
        """
        # 먼저 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "test_action"},
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # 인증 없이 조회 시도
        response = client.get(f"/api/dashboard/activities/{activity_id}")

        assert response.status_code in [401, 403]


class TestGetActivityStatsEndpoint:
    """GET /api/dashboard/stats 엔드포인트 테스트"""

    def test_get_activity_stats_success(self, client, auth_headers):
        """
        활동 통계 조회 성공 테스트

        GET /api/dashboard/stats
        - 200 OK 상태 코드 확인
        - 필수 필드 확인 (by_type, by_date, total_count, most_common_action)
        """
        # 몇 개의 활동 생성
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "login"},
            headers=auth_headers
        )
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "login"},
            headers=auth_headers
        )
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "click"},
            headers=auth_headers
        )

        response = client.get(
            "/api/dashboard/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # 필수 필드 확인
        assert "total_count" in data
        assert "by_type" in data
        assert "by_date" in data
        assert "most_common_action" in data

        # 값 확인
        assert data["total_count"] == 3
        assert data["by_type"]["login"] == 2
        assert data["by_type"]["click"] == 1
        assert data["most_common_action"] == "login"

    def test_get_activity_stats_date_filtering(self, client, auth_headers):
        """
        start_date, end_date 필터링 동작 테스트

        - 날짜 범위를 지정하여 통계 조회
        - 올바르게 필터링되는지 확인
        """
        # 활동 생성
        client.post(
            "/api/dashboard/activities",
            json={"action_type": "test_action"},
            headers=auth_headers
        )

        # 현재 시간 기준으로 범위 설정
        now = datetime.utcnow()
        start_date = (now - timedelta(days=1)).isoformat()
        end_date = (now + timedelta(days=1)).isoformat()

        response = client.get(
            f"/api/dashboard/stats?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1

    def test_get_activity_stats_empty(self, client, auth_headers):
        """
        활동이 없을 때 통계 조회 테스트

        - 활동 없이 통계 조회
        - 빈 통계 반환 확인
        """
        response = client.get(
            "/api/dashboard/stats",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["by_type"] == {}
        assert data["by_date"] == {}
        assert data["most_common_action"] is None

    def test_get_activity_stats_without_auth_failure(self, client):
        """
        인증 없이 통계 조회 실패 테스트

        - Authorization 헤더 없이 GET /api/dashboard/stats
        - 401 또는 403 확인
        """
        response = client.get("/api/dashboard/stats")

        assert response.status_code in [401, 403]


class TestDeleteActivityEndpoint:
    """DELETE /api/dashboard/activities/{activity_id} 엔드포인트 테스트"""

    def test_delete_activity_success(self, client, auth_headers):
        """
        활동 삭제 성공 테스트

        DELETE /api/dashboard/activities/{activity_id}
        - 204 No Content 상태 코드 확인
        """
        # 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "to_be_deleted"},
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # 삭제
        response = client.delete(
            f"/api/dashboard/activities/{activity_id}",
            headers=auth_headers
        )

        assert response.status_code == 204

    def test_delete_activity_not_found(self, client, auth_headers):
        """
        존재하지 않는 activity_id로 삭제 시 404 테스트

        - 존재하지 않는 ID로 DELETE /api/dashboard/activities/{id}
        - 404 Not Found 확인
        """
        response = client.delete(
            "/api/dashboard/activities/99999",
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_delete_activity_other_user_forbidden(
        self, client, auth_headers, second_user_auth_headers
    ):
        """
        다른 사용자의 활동 삭제 시 403 Forbidden 테스트

        - user1이 활동 생성
        - user2가 user1의 활동 삭제 시도
        - 403 Forbidden 확인
        """
        # user1이 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "user1_protected_action"},
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # user2가 user1의 활동 삭제 시도
        response = client.delete(
            f"/api/dashboard/activities/{activity_id}",
            headers=second_user_auth_headers
        )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"] == "Not authorized to delete this activity"

    def test_delete_activity_without_auth_failure(self, client, auth_headers):
        """
        인증 없이 활동 삭제 실패 테스트

        - Authorization 헤더 없이 DELETE /api/dashboard/activities/{id}
        - 401 또는 403 확인
        """
        # 먼저 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "test_action"},
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # 인증 없이 삭제 시도
        response = client.delete(f"/api/dashboard/activities/{activity_id}")

        assert response.status_code in [401, 403]

    def test_delete_activity_then_get_returns_404(self, client, auth_headers):
        """
        삭제 후 조회 시 404 확인 테스트

        - 활동 생성, 삭제 후 조회
        - 404 Not Found 확인
        """
        # 활동 생성
        create_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "delete_test"},
            headers=auth_headers
        )
        activity_id = create_response.json()["id"]

        # 삭제
        delete_response = client.delete(
            f"/api/dashboard/activities/{activity_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

        # 삭제 후 조회
        get_response = client.get(
            f"/api/dashboard/activities/{activity_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestDashboardIntegrationFlow:
    """Dashboard API 통합 플로우 테스트"""

    def test_full_activity_flow(self, client, auth_headers):
        """
        활동 생성 -> 조회 -> 통계 확인 -> 삭제 플로우 테스트

        전체 CRUD 플로우가 정상 동작하는지 확인
        """
        # 1. 여러 활동 생성
        activities = [
            {"action_type": "login", "description": "User logged in"},
            {"action_type": "page_view", "description": "Viewed dashboard"},
            {"action_type": "click", "description": "Clicked button"},
            {"action_type": "login", "description": "User logged in again"},
            {"action_type": "logout", "description": "User logged out"},
        ]

        created_ids = []
        for activity_data in activities:
            response = client.post(
                "/api/dashboard/activities",
                json=activity_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # 2. 목록 조회 및 검증
        list_response = client.get(
            "/api/dashboard/activities",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        activities_list = list_response.json()
        assert len(activities_list) == 5

        # 3. 통계 확인
        stats_response = client.get(
            "/api/dashboard/stats",
            headers=auth_headers
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_count"] == 5
        assert stats["by_type"]["login"] == 2
        assert stats["by_type"]["page_view"] == 1
        assert stats["by_type"]["click"] == 1
        assert stats["by_type"]["logout"] == 1
        assert stats["most_common_action"] == "login"

        # 4. 하나 삭제
        delete_response = client.delete(
            f"/api/dashboard/activities/{created_ids[0]}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

        # 5. 삭제 후 목록에서 사라졌는지 확인
        list_response_after_delete = client.get(
            "/api/dashboard/activities",
            headers=auth_headers
        )
        assert list_response_after_delete.status_code == 200
        activities_after_delete = list_response_after_delete.json()
        assert len(activities_after_delete) == 4

        # 삭제된 활동 ID가 목록에 없는지 확인
        remaining_ids = [a["id"] for a in activities_after_delete]
        assert created_ids[0] not in remaining_ids

    def test_multi_user_activity_isolation(
        self, client, auth_headers, second_user_auth_headers
    ):
        """
        다른 사용자의 활동 접근 불가 테스트

        - user1, user2 생성
        - user1이 활동 생성
        - user2가 user1의 활동에 접근 불가 확인
        """
        # user1이 활동 생성
        user1_activities = [
            {"action_type": "user1_action1", "description": "User1 activity 1"},
            {"action_type": "user1_action2", "description": "User1 activity 2"},
        ]

        user1_activity_ids = []
        for activity_data in user1_activities:
            response = client.post(
                "/api/dashboard/activities",
                json=activity_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            user1_activity_ids.append(response.json()["id"])

        # user2가 자신의 활동 생성
        user2_response = client.post(
            "/api/dashboard/activities",
            json={"action_type": "user2_action", "description": "User2 activity"},
            headers=second_user_auth_headers
        )
        assert user2_response.status_code == 201

        # user2가 목록 조회 - user1의 활동이 나타나지 않아야 함
        user2_list_response = client.get(
            "/api/dashboard/activities",
            headers=second_user_auth_headers
        )
        assert user2_list_response.status_code == 200
        user2_activities = user2_list_response.json()
        assert len(user2_activities) == 1
        assert user2_activities[0]["action_type"] == "user2_action"

        # user2가 user1의 활동 상세 조회 시도 - 403 Forbidden
        for activity_id in user1_activity_ids:
            detail_response = client.get(
                f"/api/dashboard/activities/{activity_id}",
                headers=second_user_auth_headers
            )
            assert detail_response.status_code == 403
            assert detail_response.json()["detail"] == "Not authorized to access this activity"

        # user2가 user1의 활동 삭제 시도 - 403 Forbidden
        for activity_id in user1_activity_ids:
            delete_response = client.delete(
                f"/api/dashboard/activities/{activity_id}",
                headers=second_user_auth_headers
            )
            assert delete_response.status_code == 403
            assert delete_response.json()["detail"] == "Not authorized to delete this activity"

        # user1의 활동은 여전히 존재해야 함
        user1_list_response = client.get(
            "/api/dashboard/activities",
            headers=auth_headers
        )
        assert user1_list_response.status_code == 200
        assert len(user1_list_response.json()) == 2

    def test_stats_only_include_own_activities(
        self, client, auth_headers, second_user_auth_headers
    ):
        """
        통계가 본인의 활동만 포함하는지 테스트

        - user1, user2가 각각 활동 생성
        - 각 사용자의 통계에 본인 활동만 포함 확인
        """
        # user1이 활동 3개 생성
        for i in range(3):
            client.post(
                "/api/dashboard/activities",
                json={"action_type": "user1_type"},
                headers=auth_headers
            )

        # user2가 활동 2개 생성
        for i in range(2):
            client.post(
                "/api/dashboard/activities",
                json={"action_type": "user2_type"},
                headers=second_user_auth_headers
            )

        # user1의 통계 확인
        user1_stats = client.get(
            "/api/dashboard/stats",
            headers=auth_headers
        ).json()
        assert user1_stats["total_count"] == 3
        assert "user1_type" in user1_stats["by_type"]
        assert "user2_type" not in user1_stats["by_type"]

        # user2의 통계 확인
        user2_stats = client.get(
            "/api/dashboard/stats",
            headers=second_user_auth_headers
        ).json()
        assert user2_stats["total_count"] == 2
        assert "user2_type" in user2_stats["by_type"]
        assert "user1_type" not in user2_stats["by_type"]
