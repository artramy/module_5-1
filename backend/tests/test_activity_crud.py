"""
Activity 모델 및 CRUD 함수 테스트

테스트 항목:
- Activity 모델 필드 존재 여부
- Foreign Key 관계 테스트
- created_at 자동 생성
- CRUD 함수 동작 검증
- 페이지네이션 및 필터링
- 통계 함수 테스트
- 오래된 활동 삭제
- Cascade 삭제 테스트
"""

import pytest
from datetime import datetime, timedelta

from app.models.activity import Activity
from app.models.user import User
from app.crud.user import create_user
from app.crud.activity import (
    create_activity,
    get_activities_by_user,
    get_activity_by_id,
    get_activities_by_type,
    get_activity_stats,
    delete_old_activities,
)


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_user(db, username="testuser", email="test@example.com"):
    """테스트용 사용자 생성 헬퍼"""
    return create_user(
        db=db,
        username=username,
        email=email,
        password_hash="hashed_password_123",
    )


# ============================================================================
# Activity Model Tests
# ============================================================================

class TestActivityModelFields:
    """Activity 모델 필드 존재 여부 테스트"""

    def test_activity_model_has_required_fields(self, db):
        """Activity 모델에 필수 필드가 존재하는지 확인"""
        # 사용자 생성
        user = create_test_user(db)

        # Activity 생성
        activity = Activity(
            user_id=user.id,
            action_type="login",
            description="User logged in",
            extra_data={"ip": "127.0.0.1"},
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        # 필드 존재 확인
        assert hasattr(activity, 'id')
        assert hasattr(activity, 'user_id')
        assert hasattr(activity, 'action_type')
        assert hasattr(activity, 'description')
        assert hasattr(activity, 'extra_data')
        assert hasattr(activity, 'created_at')

    def test_activity_field_values(self, db):
        """Activity 필드 값이 올바르게 저장되는지 확인"""
        user = create_test_user(db)

        activity = Activity(
            user_id=user.id,
            action_type="click",
            description="Button clicked",
            extra_data={"button_id": "submit"},
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        assert activity.id is not None
        assert activity.user_id == user.id
        assert activity.action_type == "click"
        assert activity.description == "Button clicked"
        assert activity.extra_data == {"button_id": "submit"}


class TestActivityForeignKeyRelation:
    """Foreign Key 관계 테스트"""

    def test_activity_user_relation(self, db):
        """Activity.user로 User에 접근 가능한지 확인"""
        user = create_test_user(db, username="reluser", email="rel@example.com")

        activity = create_activity(
            db=db,
            user_id=user.id,
            action_type="login",
            description="Test login",
        )

        # Activity에서 User 접근
        assert activity.user is not None
        assert activity.user.id == user.id
        assert activity.user.username == "reluser"

    def test_user_activities_relation(self, db):
        """User.activities로 Activity 목록에 접근 가능한지 확인"""
        user = create_test_user(db, username="actuser", email="act@example.com")

        # 여러 Activity 생성
        create_activity(db, user.id, "login", "Login 1")
        create_activity(db, user.id, "query", "Query 1")
        create_activity(db, user.id, "click", "Click 1")

        # User에서 activities 접근
        db.refresh(user)
        assert user.activities is not None
        assert len(user.activities) == 3


class TestActivityCreatedAtAutoGeneration:
    """created_at 자동 생성 테스트"""

    def test_created_at_auto_set(self, db):
        """Activity 생성 시 created_at이 자동으로 설정되는지 확인"""
        user = create_test_user(db, username="timeuser", email="time@example.com")

        before_creation = datetime.utcnow()

        activity = create_activity(
            db=db,
            user_id=user.id,
            action_type="login",
        )

        after_creation = datetime.utcnow()

        assert activity.created_at is not None
        # created_at이 생성 시간 범위 내에 있는지 확인
        assert before_creation <= activity.created_at <= after_creation


# ============================================================================
# Activity CRUD Tests
# ============================================================================

class TestCreateActivity:
    """create_activity 함수 테스트"""

    def test_create_activity_success(self, db):
        """정상적으로 활동 생성"""
        user = create_test_user(db, username="createuser", email="create@example.com")

        activity = create_activity(
            db=db,
            user_id=user.id,
            action_type="login",
            description="User logged in successfully",
            extra_data={"ip": "192.168.1.1", "browser": "Chrome"},
        )

        assert activity.id is not None
        assert activity.user_id == user.id
        assert activity.action_type == "login"
        assert activity.description == "User logged in successfully"
        assert activity.extra_data == {"ip": "192.168.1.1", "browser": "Chrome"}
        assert activity.created_at is not None

    def test_create_activity_with_none_description(self, db):
        """description=None도 허용되는지 확인"""
        user = create_test_user(db, username="nodescuser", email="nodesc@example.com")

        activity = create_activity(
            db=db,
            user_id=user.id,
            action_type="click",
            description=None,
            extra_data={"button": "submit"},
        )

        assert activity.id is not None
        assert activity.description is None

    def test_create_activity_with_none_extra_data(self, db):
        """extra_data=None도 허용되는지 확인"""
        user = create_test_user(db, username="nometauser", email="nometa@example.com")

        activity = create_activity(
            db=db,
            user_id=user.id,
            action_type="query",
            description="Search query",
            extra_data=None,
        )

        assert activity.id is not None
        assert activity.extra_data is None

    def test_create_activity_minimal(self, db):
        """필수 필드만으로 Activity 생성"""
        user = create_test_user(db, username="minuser", email="min@example.com")

        activity = create_activity(
            db=db,
            user_id=user.id,
            action_type="view",
        )

        assert activity.id is not None
        assert activity.user_id == user.id
        assert activity.action_type == "view"
        assert activity.description is None
        assert activity.extra_data is None


class TestGetActivitiesByUser:
    """get_activities_by_user 함수 테스트"""

    def test_get_activities_by_user_basic(self, db):
        """특정 사용자의 활동 목록 조회"""
        user = create_test_user(db, username="getuser", email="get@example.com")

        # 활동 생성
        create_activity(db, user.id, "login", "Login")
        create_activity(db, user.id, "query", "Query")
        create_activity(db, user.id, "click", "Click")

        activities = get_activities_by_user(db, user.id)

        assert len(activities) == 3

    def test_get_activities_by_user_descending_order(self, db):
        """최신순 정렬 확인 - created_at 기준 내림차순"""
        user = create_test_user(db, username="orderuser", email="order@example.com")

        # 명시적으로 다른 시간에 생성된 활동들
        # 오래된 활동
        old_activity = Activity(
            user_id=user.id,
            action_type="old",
            description="Old action",
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        db.add(old_activity)

        # 중간 활동
        mid_activity = Activity(
            user_id=user.id,
            action_type="mid",
            description="Mid action",
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        db.add(mid_activity)

        # 최신 활동
        new_activity = Activity(
            user_id=user.id,
            action_type="new",
            description="New action",
            created_at=datetime.utcnow(),
        )
        db.add(new_activity)
        db.commit()

        activities = get_activities_by_user(db, user.id)

        # 최신순(DESC)으로 정렬 - created_at 기준
        assert len(activities) == 3
        assert activities[0].action_type == "new"
        assert activities[1].action_type == "mid"
        assert activities[2].action_type == "old"

    def test_get_activities_by_user_pagination_limit(self, db):
        """페이지네이션 - limit 동작 확인"""
        user = create_test_user(db, username="limituser", email="limit@example.com")

        # 5개 활동 생성
        for i in range(5):
            create_activity(db, user.id, f"action_{i}", f"Action {i}")

        # limit=3으로 조회
        activities = get_activities_by_user(db, user.id, limit=3)

        assert len(activities) == 3

    def test_get_activities_by_user_pagination_offset(self, db):
        """페이지네이션 - offset 동작 확인"""
        user = create_test_user(db, username="offsetuser", email="offset@example.com")

        # 5개 활동 생성 - ID 저장
        created_activities = []
        for i in range(5):
            act = create_activity(db, user.id, f"action_{i}", f"Action {i}")
            created_activities.append(act)

        # offset=2로 조회 (처음 2개 건너뜀)
        activities = get_activities_by_user(db, user.id, offset=2)

        assert len(activities) == 3
        # offset 이후의 활동들이 조회되는지 확인
        # 전체 활동 수 - offset = 반환되는 활동 수
        all_activities = get_activities_by_user(db, user.id)
        assert activities == all_activities[2:]

    def test_get_activities_by_user_pagination_combined(self, db):
        """페이지네이션 - limit과 offset 조합"""
        user = create_test_user(db, username="pageuser", email="page@example.com")

        # 10개 활동 생성
        for i in range(10):
            create_activity(db, user.id, f"action_{i}", f"Action {i}")

        # offset=3, limit=2로 조회
        activities = get_activities_by_user(db, user.id, limit=2, offset=3)

        assert len(activities) == 2

    def test_get_activities_by_user_empty(self, db):
        """활동이 없는 사용자 조회"""
        user = create_test_user(db, username="emptyuser", email="empty@example.com")

        activities = get_activities_by_user(db, user.id)

        assert len(activities) == 0
        assert activities == []


class TestGetActivityById:
    """get_activity_by_id 함수 테스트"""

    def test_get_activity_by_id_exists(self, db):
        """존재하는 활동 조회 성공"""
        user = create_test_user(db, username="iduser", email="id@example.com")

        created_activity = create_activity(
            db, user.id, "login", "Login activity"
        )

        found_activity = get_activity_by_id(db, created_activity.id)

        assert found_activity is not None
        assert found_activity.id == created_activity.id
        assert found_activity.action_type == "login"
        assert found_activity.description == "Login activity"

    def test_get_activity_by_id_not_exists(self, db):
        """존재하지 않는 활동 조회 시 None 반환"""
        result = get_activity_by_id(db, 99999)

        assert result is None


class TestGetActivitiesByType:
    """get_activities_by_type 함수 테스트"""

    def test_get_activities_by_type_filter(self, db):
        """특정 action_type으로 필터링"""
        user = create_test_user(db, username="typeuser", email="type@example.com")

        # 다양한 유형의 활동 생성
        create_activity(db, user.id, "login", "Login 1")
        create_activity(db, user.id, "login", "Login 2")
        create_activity(db, user.id, "query", "Query 1")
        create_activity(db, user.id, "click", "Click 1")

        # login 유형만 조회
        activities = get_activities_by_type(db, user.id, "login")

        assert len(activities) == 2
        assert all(a.action_type == "login" for a in activities)

    def test_get_activities_by_type_excludes_others(self, db):
        """다른 유형은 제외되는지 확인"""
        user = create_test_user(db, username="excludeuser", email="exclude@example.com")

        create_activity(db, user.id, "login", "Login")
        create_activity(db, user.id, "query", "Query")
        create_activity(db, user.id, "click", "Click")

        # query 유형만 조회
        activities = get_activities_by_type(db, user.id, "query")

        assert len(activities) == 1
        assert activities[0].action_type == "query"
        assert activities[0].description == "Query"

    def test_get_activities_by_type_pagination(self, db):
        """페이지네이션 동작 확인"""
        user = create_test_user(db, username="typepageuser", email="typepage@example.com")

        # 같은 유형의 활동 5개 생성
        for i in range(5):
            create_activity(db, user.id, "login", f"Login {i}")

        # limit=2, offset=1로 조회
        activities = get_activities_by_type(db, user.id, "login", limit=2, offset=1)

        assert len(activities) == 2

    def test_get_activities_by_type_not_found(self, db):
        """존재하지 않는 유형 조회"""
        user = create_test_user(db, username="notypeuser", email="notype@example.com")

        create_activity(db, user.id, "login", "Login")

        activities = get_activities_by_type(db, user.id, "nonexistent_type")

        assert len(activities) == 0


class TestGetActivityStats:
    """get_activity_stats 함수 테스트"""

    def test_get_activity_stats_total_count(self, db):
        """총 개수 계산 확인"""
        user = create_test_user(db, username="statsuser", email="stats@example.com")

        for i in range(5):
            create_activity(db, user.id, "login", f"Login {i}")

        stats = get_activity_stats(db, user.id)

        assert stats["total_count"] == 5

    def test_get_activity_stats_by_type(self, db):
        """by_type 딕셔너리 확인 (유형별 카운트)"""
        user = create_test_user(db, username="bytypeuser", email="bytype@example.com")

        create_activity(db, user.id, "login", "Login 1")
        create_activity(db, user.id, "login", "Login 2")
        create_activity(db, user.id, "query", "Query 1")
        create_activity(db, user.id, "click", "Click 1")
        create_activity(db, user.id, "click", "Click 2")
        create_activity(db, user.id, "click", "Click 3")

        stats = get_activity_stats(db, user.id)

        assert stats["by_type"]["login"] == 2
        assert stats["by_type"]["query"] == 1
        assert stats["by_type"]["click"] == 3

    def test_get_activity_stats_by_date(self, db):
        """by_date 딕셔너리 확인 (날짜별 카운트)"""
        user = create_test_user(db, username="bydateuser", email="bydate@example.com")

        # 오늘 날짜의 활동들 생성
        create_activity(db, user.id, "login", "Today 1")
        create_activity(db, user.id, "query", "Today 2")

        stats = get_activity_stats(db, user.id)

        today = datetime.utcnow().strftime("%Y-%m-%d")
        assert today in stats["by_date"]
        assert stats["by_date"][today] == 2

    def test_get_activity_stats_most_common_action(self, db):
        """most_common_action 계산 확인"""
        user = create_test_user(db, username="commonuser", email="common@example.com")

        # click이 가장 많음
        create_activity(db, user.id, "login", "Login")
        create_activity(db, user.id, "click", "Click 1")
        create_activity(db, user.id, "click", "Click 2")
        create_activity(db, user.id, "click", "Click 3")

        stats = get_activity_stats(db, user.id)

        assert stats["most_common_action"] == "click"

    def test_get_activity_stats_date_filter(self, db):
        """start_date, end_date 필터링 동작 확인"""
        user = create_test_user(db, username="filteruser", email="filter@example.com")

        # 활동 생성 (기본 created_at은 현재 시간)
        act1 = create_activity(db, user.id, "login", "Recent login")

        # 날짜 필터로 조회
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # 어제부터 내일까지 조회 - 현재 활동 포함
        stats = get_activity_stats(db, user.id, start_date=yesterday, end_date=tomorrow)
        assert stats["total_count"] == 1

        # 미래 기간만 조회 - 활동 없음
        far_future = now + timedelta(days=10)
        stats_empty = get_activity_stats(db, user.id, start_date=far_future)
        assert stats_empty["total_count"] == 0

    def test_get_activity_stats_empty(self, db):
        """활동이 없을 때 통계"""
        user = create_test_user(db, username="emptystatsuser", email="emptystats@example.com")

        stats = get_activity_stats(db, user.id)

        assert stats["total_count"] == 0
        assert stats["by_type"] == {}
        assert stats["by_date"] == {}
        assert stats["most_common_action"] is None


class TestDeleteOldActivities:
    """delete_old_activities 함수 테스트"""

    def test_delete_old_activities_basic(self, db):
        """오래된 활동 삭제 확인"""
        user = create_test_user(db, username="delolduser", email="delold@example.com")

        # 오래된 활동 생성 (created_at을 수동으로 설정)
        old_activity = Activity(
            user_id=user.id,
            action_type="old_action",
            description="Old activity",
            created_at=datetime.utcnow() - timedelta(days=100),
        )
        db.add(old_activity)
        db.commit()

        # 최근 활동 생성
        create_activity(db, user.id, "recent_action", "Recent activity")

        # 90일 이전 활동 삭제
        deleted_count = delete_old_activities(db, days=90)

        assert deleted_count == 1

        # 삭제 후 확인
        activities = get_activities_by_user(db, user.id)
        assert len(activities) == 1
        assert activities[0].action_type == "recent_action"

    def test_delete_old_activities_custom_days(self, db):
        """days 파라미터 동작 확인"""
        user = create_test_user(db, username="customdaysuser", email="customdays@example.com")

        # 10일 전 활동
        activity_10_days = Activity(
            user_id=user.id,
            action_type="10_days_old",
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db.add(activity_10_days)

        # 5일 전 활동
        activity_5_days = Activity(
            user_id=user.id,
            action_type="5_days_old",
            created_at=datetime.utcnow() - timedelta(days=5),
        )
        db.add(activity_5_days)
        db.commit()

        # 7일 이전 활동 삭제
        deleted_count = delete_old_activities(db, days=7)

        assert deleted_count == 1

        # 5일 전 활동은 남아있어야 함
        activities = get_activities_by_user(db, user.id)
        assert len(activities) == 1
        assert activities[0].action_type == "5_days_old"

    def test_delete_old_activities_returns_count(self, db):
        """삭제된 개수 반환 확인"""
        user = create_test_user(db, username="countuser", email="count@example.com")

        # 오래된 활동 3개 생성
        for i in range(3):
            old_activity = Activity(
                user_id=user.id,
                action_type=f"old_{i}",
                created_at=datetime.utcnow() - timedelta(days=100),
            )
            db.add(old_activity)
        db.commit()

        deleted_count = delete_old_activities(db, days=90)

        assert deleted_count == 3

    def test_delete_old_activities_keeps_recent(self, db):
        """최근 활동은 삭제되지 않는지 확인"""
        user = create_test_user(db, username="keeprecentuser", email="keeprecent@example.com")

        # 최근 활동 생성
        create_activity(db, user.id, "recent1", "Recent 1")
        create_activity(db, user.id, "recent2", "Recent 2")

        # 삭제 시도 (90일 기본)
        deleted_count = delete_old_activities(db, days=90)

        assert deleted_count == 0

        # 모든 활동이 남아있어야 함
        activities = get_activities_by_user(db, user.id)
        assert len(activities) == 2

    def test_delete_old_activities_no_old_data(self, db):
        """오래된 데이터가 없을 때"""
        user = create_test_user(db, username="noolduser", email="noold@example.com")

        create_activity(db, user.id, "new", "New activity")

        deleted_count = delete_old_activities(db, days=90)

        assert deleted_count == 0


# ============================================================================
# Cascade Delete Test
# ============================================================================

class TestCascadeDelete:
    """사용자 삭제 시 관련 활동도 삭제되는지 테스트"""

    def test_user_delete_cascades_to_activities(self, db):
        """User 삭제 시 관련 Activity도 함께 삭제되는지 확인"""
        # 사용자 생성
        user = create_test_user(db, username="cascadeuser", email="cascade@example.com")
        user_id = user.id

        # 여러 활동 생성
        act1 = create_activity(db, user.id, "login", "Login")
        act2 = create_activity(db, user.id, "query", "Query")
        act3 = create_activity(db, user.id, "click", "Click")

        activity_ids = [act1.id, act2.id, act3.id]

        # 활동이 존재하는지 확인
        assert len(get_activities_by_user(db, user_id)) == 3

        # 사용자 삭제
        db.delete(user)
        db.commit()

        # 삭제된 사용자의 활동 조회 시도
        # (외래키로 인해 더 이상 조회되지 않아야 함)
        for activity_id in activity_ids:
            activity = get_activity_by_id(db, activity_id)
            assert activity is None, f"Activity {activity_id} should be deleted with user"
