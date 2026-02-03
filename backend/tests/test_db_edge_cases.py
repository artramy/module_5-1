"""
DB 엣지 케이스 테스트

NULL 값 처리, 빈 문자열, 긴 문자열, 특수문자, 트랜잭션 롤백,
대량 데이터 처리 등의 엣지 케이스를 테스트합니다.
"""

import pytest
import time
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.crud.user import create_user, get_user_by_id, get_user_by_email, get_user_by_username


class TestNullValueHandling:
    """NULL 값 처리 테스트"""

    def test_password_hash_cannot_be_none(self, db):
        """password_hash에 None 전달 시 에러 발생 확인"""
        user = User(
            username="null_test",
            email="null@example.com",
            password_hash=None  # NULL 값
        )
        db.add(user)

        with pytest.raises(IntegrityError):
            db.commit()

    def test_username_cannot_be_none(self, db):
        """username에 None 전달 시 에러 발생 확인"""
        user = User(
            username=None,  # NULL 값
            email="username_null@example.com",
            password_hash="hash"
        )
        db.add(user)

        with pytest.raises(IntegrityError):
            db.commit()

    def test_email_cannot_be_none(self, db):
        """email에 None 전달 시 에러 발생 확인"""
        user = User(
            username="email_null_test",
            email=None,  # NULL 값
            password_hash="hash"
        )
        db.add(user)

        with pytest.raises(IntegrityError):
            db.commit()


class TestEmptyStringHandling:
    """빈 문자열 처리 테스트"""

    def test_empty_username_allowed(self, db):
        """빈 username 문자열이 허용되는지 확인 (DB 레벨에서는 허용됨)"""
        user = User(
            username="",  # 빈 문자열
            email="empty_username@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.username == ""
        assert user.id is not None

    def test_empty_email_allowed(self, db):
        """빈 email 문자열이 허용되는지 확인 (DB 레벨에서는 허용됨)"""
        user = User(
            username="empty_email_user",
            email="",  # 빈 문자열
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.email == ""
        assert user.id is not None

    def test_empty_password_hash_allowed(self, db):
        """빈 password_hash 문자열이 허용되는지 확인 (DB 레벨에서는 허용됨)"""
        user = User(
            username="empty_hash_user",
            email="empty_hash@example.com",
            password_hash=""  # 빈 문자열
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.password_hash == ""
        assert user.id is not None


class TestLongStringHandling:
    """매우 긴 문자열 처리 테스트"""

    def test_username_max_length(self, db):
        """username 최대 길이 (50자) 테스트"""
        # 정확히 50자
        long_username = "a" * 50
        user = User(
            username=long_username,
            email="long_username@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert len(user.username) == 50

    def test_username_exceeds_max_length(self, db):
        """username이 최대 길이를 초과할 때의 동작 테스트"""
        # 51자 (초과)
        # SQLite는 String 길이 제한을 강제하지 않음
        very_long_username = "a" * 100
        user = User(
            username=very_long_username,
            email="very_long_username@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # SQLite에서는 저장됨 (길이 제한 미적용)
        assert user.username == very_long_username

    def test_email_max_length(self, db):
        """email 최대 길이 (100자) 테스트"""
        # 정확히 100자
        long_email = "a" * 88 + "@example.com"  # 88 + 12 = 100
        user = User(
            username="long_email_user",
            email=long_email,
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert len(user.email) == 100

    def test_email_exceeds_max_length(self, db):
        """email이 최대 길이를 초과할 때의 동작 테스트"""
        # 200자 (초과)
        very_long_email = "a" * 188 + "@example.com"
        user = User(
            username="very_long_email_user",
            email=very_long_email,
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # SQLite에서는 저장됨 (길이 제한 미적용)
        assert user.email == very_long_email

    def test_password_hash_max_length(self, db):
        """password_hash 최대 길이 (255자) 테스트"""
        long_hash = "x" * 255
        user = User(
            username="long_hash_user",
            email="long_hash@example.com",
            password_hash=long_hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert len(user.password_hash) == 255


class TestSpecialCharacterHandling:
    """특수문자 포함 문자열 처리 테스트"""

    def test_username_with_special_characters(self, db):
        """username에 특수문자 포함 테스트"""
        special_username = "user_name-123.test"
        user = User(
            username=special_username,
            email="special@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.username == special_username

    def test_email_with_plus_sign(self, db):
        """email에 + 기호 포함 테스트"""
        email_with_plus = "user+tag@example.com"
        user = User(
            username="plus_email_user",
            email=email_with_plus,
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.email == email_with_plus

    def test_username_with_unicode(self, db):
        """username에 유니코드 문자 포함 테스트"""
        unicode_username = "사용자_테스트"
        user = User(
            username=unicode_username,
            email="unicode@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.username == unicode_username

    def test_password_hash_with_special_characters(self, db):
        """password_hash에 특수문자 포함 테스트"""
        special_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.AFL6/ylpmSv.uu"
        user = User(
            username="special_hash_user",
            email="special_hash@example.com",
            password_hash=special_hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.password_hash == special_hash

    def test_sql_injection_attempt_in_username(self, db):
        """SQL 인젝션 시도가 문자열로 저장되는지 확인"""
        injection_attempt = "'; DROP TABLE users; --"
        user = User(
            username=injection_attempt,
            email="injection@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # SQL 인젝션이 실행되지 않고 문자열로 저장됨
        assert user.username == injection_attempt

        # 테이블이 여전히 존재하는지 확인
        all_users = db.query(User).all()
        assert len(all_users) >= 1


class TestTransactionRollback:
    """DB 트랜잭션 롤백 테스트"""

    def test_rollback_on_error(self, db):
        """에러 발생 시 롤백이 정상 작동하는지 확인"""
        # 첫 번째 사용자 생성
        user1 = User(
            username="rollback_test1",
            email="rollback1@example.com",
            password_hash="hash"
        )
        db.add(user1)
        db.commit()

        # 두 번째 사용자 (중복 email로 에러 유발)
        user2 = User(
            username="rollback_test2",
            email="rollback1@example.com",  # 중복 email
            password_hash="hash"
        )
        db.add(user2)

        with pytest.raises(IntegrityError):
            db.commit()

        # 롤백
        db.rollback()

        # 첫 번째 사용자는 여전히 존재해야 함
        existing_user = get_user_by_email(db, "rollback1@example.com")
        assert existing_user is not None
        assert existing_user.username == "rollback_test1"

    def test_explicit_rollback(self, db):
        """명시적 롤백 테스트"""
        user = User(
            username="explicit_rollback",
            email="explicit_rollback@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.flush()  # DB에 쓰지만 커밋하지 않음

        # 명시적 롤백
        db.rollback()

        # 롤백 후 사용자가 존재하지 않아야 함
        result = get_user_by_email(db, "explicit_rollback@example.com")
        assert result is None

    def test_multiple_operations_in_transaction(self, db):
        """트랜잭션 내 여러 작업 테스트"""
        # 여러 사용자 추가
        users = []
        for i in range(5):
            user = User(
                username=f"multi_user_{i}",
                email=f"multi_{i}@example.com",
                password_hash="hash"
            )
            db.add(user)
            users.append(user)

        db.commit()

        # 모든 사용자가 저장되었는지 확인
        for i in range(5):
            result = get_user_by_email(db, f"multi_{i}@example.com")
            assert result is not None


class TestBulkDataPerformance:
    """대량 데이터 (100개 이상) 생성/조회 성능 테스트"""

    def test_bulk_create_100_users(self, db):
        """100개 사용자 생성 테스트"""
        users = []
        for i in range(100):
            user = User(
                username=f"bulk_user_{i}",
                email=f"bulk_{i}@example.com",
                password_hash=f"hash_{i}"
            )
            users.append(user)

        db.add_all(users)
        db.commit()

        # 모든 사용자가 생성되었는지 확인
        count = db.query(User).count()
        assert count == 100

    def test_bulk_create_performance(self, db):
        """대량 생성 성능 테스트 (150개, 5초 이내)"""
        start_time = time.time()

        users = []
        for i in range(150):
            user = User(
                username=f"perf_user_{i}",
                email=f"perf_{i}@example.com",
                password_hash=f"hash_{i}"
            )
            users.append(user)

        db.add_all(users)
        db.commit()

        elapsed_time = time.time() - start_time

        # 5초 이내에 완료되어야 함
        assert elapsed_time < 5.0
        assert db.query(User).count() == 150

    def test_bulk_query_all(self, db):
        """대량 데이터 전체 조회 테스트"""
        # 먼저 데이터 생성
        users = []
        for i in range(100):
            user = User(
                username=f"query_user_{i}",
                email=f"query_{i}@example.com",
                password_hash=f"hash_{i}"
            )
            users.append(user)

        db.add_all(users)
        db.commit()

        # 전체 조회
        start_time = time.time()
        all_users = db.query(User).all()
        elapsed_time = time.time() - start_time

        assert len(all_users) == 100
        # 1초 이내에 완료되어야 함
        assert elapsed_time < 1.0

    def test_bulk_query_with_filter(self, db):
        """대량 데이터 필터 조회 테스트"""
        # 먼저 데이터 생성
        users = []
        for i in range(100):
            user = User(
                username=f"filter_user_{i}",
                email=f"filter_{i}@example.com",
                password_hash=f"hash_{i}"
            )
            users.append(user)

        db.add_all(users)
        db.commit()

        # 특정 패턴으로 필터링 (LIKE 쿼리)
        start_time = time.time()
        filtered_users = db.query(User).filter(
            User.username.like("filter_user_5%")
        ).all()
        elapsed_time = time.time() - start_time

        # filter_user_5, filter_user_50-59 = 11개
        assert len(filtered_users) == 11
        # 1초 이내에 완료되어야 함
        assert elapsed_time < 1.0

    def test_bulk_query_with_pagination(self, db):
        """대량 데이터 페이지네이션 조회 테스트"""
        # 먼저 데이터 생성
        users = []
        for i in range(100):
            user = User(
                username=f"page_user_{i:03d}",  # 정렬을 위해 제로패딩
                email=f"page_{i}@example.com",
                password_hash=f"hash_{i}"
            )
            users.append(user)

        db.add_all(users)
        db.commit()

        # 페이지네이션 조회 (페이지 크기 10)
        page_size = 10
        page_number = 5  # 0-indexed, 50-59번째 항목

        start_time = time.time()
        paginated_users = db.query(User)\
            .order_by(User.username)\
            .offset(page_number * page_size)\
            .limit(page_size)\
            .all()
        elapsed_time = time.time() - start_time

        assert len(paginated_users) == 10
        # 1초 이내에 완료되어야 함
        assert elapsed_time < 1.0


class TestCRUDFunctions:
    """CRUD 함수 엣지 케이스 테스트"""

    def test_get_user_by_id_not_found(self, db):
        """존재하지 않는 ID로 조회 시 None 반환"""
        result = get_user_by_id(db, 99999)
        assert result is None

    def test_get_user_by_email_not_found(self, db):
        """존재하지 않는 이메일로 조회 시 None 반환"""
        result = get_user_by_email(db, "nonexistent@example.com")
        assert result is None

    def test_get_user_by_username_not_found(self, db):
        """존재하지 않는 사용자명으로 조회 시 None 반환"""
        result = get_user_by_username(db, "nonexistent_user")
        assert result is None

    def test_create_user_and_retrieve(self, db):
        """사용자 생성 후 조회 테스트"""
        user = create_user(
            db,
            username="crud_test",
            email="crud@example.com",
            password_hash="secure_hash"
        )

        # ID로 조회
        by_id = get_user_by_id(db, user.id)
        assert by_id is not None
        assert by_id.username == "crud_test"

        # 이메일로 조회
        by_email = get_user_by_email(db, "crud@example.com")
        assert by_email is not None
        assert by_email.id == user.id

        # 사용자명으로 조회
        by_username = get_user_by_username(db, "crud_test")
        assert by_username is not None
        assert by_username.id == user.id
