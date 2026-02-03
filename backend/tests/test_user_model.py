"""
User 모델 테스트

User 모델의 필드 검증, 타임스탬프 자동 생성, unique 제약 조건을 테스트합니다.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.models.user import User


class TestUserModelFields:
    """User 모델 필드 검증 테스트"""

    def test_user_has_required_fields(self, db):
        """User 모델에 필수 필드가 존재하는지 확인"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_123"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 모든 필드가 존재하는지 확인
        assert hasattr(user, "id")
        assert hasattr(user, "username")
        assert hasattr(user, "email")
        assert hasattr(user, "password_hash")
        assert hasattr(user, "created_at")
        assert hasattr(user, "updated_at")

    def test_user_field_values(self, db):
        """User 모델 필드 값이 올바르게 저장되는지 확인"""
        user = User(
            username="fieldtest",
            email="field@example.com",
            password_hash="secure_hash_456"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.username == "fieldtest"
        assert user.email == "field@example.com"
        assert user.password_hash == "secure_hash_456"

    def test_user_id_auto_increment(self, db):
        """User ID가 자동 증가하는지 확인"""
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash="hash1"
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash="hash2"
        )
        db.add(user1)
        db.add(user2)
        db.commit()

        assert user1.id is not None
        assert user2.id is not None
        assert user2.id > user1.id

    def test_user_repr(self, db):
        """User __repr__ 메서드 테스트"""
        user = User(
            username="reprtest",
            email="repr@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        repr_str = repr(user)
        assert "reprtest" in repr_str
        assert "repr@example.com" in repr_str
        assert str(user.id) in repr_str


class TestUserTimestamps:
    """타임스탬프 (created_at, updated_at) 자동 생성 테스트"""

    def test_created_at_auto_generated(self, db):
        """created_at이 자동으로 생성되는지 확인"""
        before_create = datetime.now(timezone.utc)

        user = User(
            username="timestamp_user",
            email="timestamp@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        after_create = datetime.now(timezone.utc)

        assert user.created_at is not None
        # 타임스탬프가 적절한 범위 내에 있는지 확인 (timezone 차이 고려)
        # SQLite는 timezone 정보를 저장하지 않으므로 naive datetime으로 비교
        created_at_naive = user.created_at.replace(tzinfo=None) if user.created_at.tzinfo else user.created_at
        before_naive = before_create.replace(tzinfo=None)
        after_naive = after_create.replace(tzinfo=None)

        # 1분 이내의 차이 허용
        assert abs((created_at_naive - before_naive).total_seconds()) < 60

    def test_updated_at_auto_generated(self, db):
        """updated_at이 자동으로 생성되는지 확인"""
        user = User(
            username="update_user",
            email="update@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.updated_at is not None

    def test_created_at_and_updated_at_initially_same(self, db):
        """생성 시 created_at과 updated_at이 동일하거나 매우 가까운지 확인"""
        user = User(
            username="same_time_user",
            email="sametime@example.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 초 단위로 비교 (밀리초 차이 허용)
        created_ts = user.created_at.replace(microsecond=0)
        updated_ts = user.updated_at.replace(microsecond=0)

        # 1초 이내 차이 허용
        assert abs((created_ts - updated_ts).total_seconds()) <= 1


class TestUserUniqueConstraints:
    """unique 제약 조건 테스트"""

    def test_duplicate_username_raises_error(self, db):
        """중복 username 삽입 시 IntegrityError 발생 확인"""
        user1 = User(
            username="duplicate_name",
            email="unique1@example.com",
            password_hash="hash1"
        )
        db.add(user1)
        db.commit()

        user2 = User(
            username="duplicate_name",  # 중복 username
            email="unique2@example.com",
            password_hash="hash2"
        )
        db.add(user2)

        with pytest.raises(IntegrityError):
            db.commit()

    def test_duplicate_email_raises_error(self, db):
        """중복 email 삽입 시 IntegrityError 발생 확인"""
        user1 = User(
            username="unique1",
            email="duplicate@example.com",
            password_hash="hash1"
        )
        db.add(user1)
        db.commit()

        user2 = User(
            username="unique2",
            email="duplicate@example.com",  # 중복 email
            password_hash="hash2"
        )
        db.add(user2)

        with pytest.raises(IntegrityError):
            db.commit()

    def test_different_username_and_email_allowed(self, db):
        """서로 다른 username과 email은 허용되는지 확인"""
        user1 = User(
            username="allowed1",
            email="allowed1@example.com",
            password_hash="hash1"
        )
        user2 = User(
            username="allowed2",
            email="allowed2@example.com",
            password_hash="hash2"
        )

        db.add(user1)
        db.add(user2)
        db.commit()

        # 두 사용자 모두 성공적으로 저장됨
        assert user1.id is not None
        assert user2.id is not None
        assert user1.id != user2.id

    def test_case_sensitive_username(self, db):
        """username이 대소문자를 구분하는지 확인 (SQLite 기본 동작)"""
        user1 = User(
            username="CaseSensitive",
            email="case1@example.com",
            password_hash="hash1"
        )
        db.add(user1)
        db.commit()

        # SQLite에서는 기본적으로 대소문자를 구분함
        user2 = User(
            username="casesensitive",  # 다른 케이스
            email="case2@example.com",
            password_hash="hash2"
        )
        db.add(user2)
        db.commit()  # 성공해야 함

        assert user1.id is not None
        assert user2.id is not None
