"""
User CRUD 함수 테스트

테스트 항목:
- 사용자 생성 및 필드 검증
- 중복 email/username 시 IntegrityError 발생
- email/username/id로 사용자 조회
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id,
)


class TestCreateUser:
    """사용자 생성 테스트"""

    def test_create_user(self, db):
        """사용자 생성 및 필드 검증"""
        user = create_user(
            db=db,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_123",
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_user_duplicate_email(self, db):
        """중복 email 시 IntegrityError 발생 확인"""
        # 첫 번째 사용자 생성
        create_user(
            db=db,
            username="user1",
            email="same@example.com",
            password_hash="hash1",
        )

        # 동일 email로 두 번째 사용자 생성 시도
        with pytest.raises(IntegrityError):
            create_user(
                db=db,
                username="user2",
                email="same@example.com",
                password_hash="hash2",
            )

    def test_create_user_duplicate_username(self, db):
        """중복 username 시 IntegrityError 발생 확인"""
        # 첫 번째 사용자 생성
        create_user(
            db=db,
            username="sameuser",
            email="user1@example.com",
            password_hash="hash1",
        )

        # 동일 username으로 두 번째 사용자 생성 시도
        with pytest.raises(IntegrityError):
            create_user(
                db=db,
                username="sameuser",
                email="user2@example.com",
                password_hash="hash2",
            )


class TestGetUserByEmail:
    """email로 사용자 조회 테스트"""

    def test_get_user_by_email_exists(self, db):
        """존재하는 email로 조회"""
        # 사용자 생성
        created_user = create_user(
            db=db,
            username="emailuser",
            email="find@example.com",
            password_hash="hash",
        )

        # email로 조회
        found_user = get_user_by_email(db, "find@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "emailuser"
        assert found_user.email == "find@example.com"

    def test_get_user_by_email_not_exists(self, db):
        """존재하지 않는 email로 조회"""
        result = get_user_by_email(db, "notexist@example.com")

        assert result is None


class TestGetUserByUsername:
    """username으로 사용자 조회 테스트"""

    def test_get_user_by_username_exists(self, db):
        """존재하는 username으로 조회"""
        # 사용자 생성
        created_user = create_user(
            db=db,
            username="findme",
            email="username@example.com",
            password_hash="hash",
        )

        # username으로 조회
        found_user = get_user_by_username(db, "findme")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "findme"
        assert found_user.email == "username@example.com"

    def test_get_user_by_username_not_exists(self, db):
        """존재하지 않는 username으로 조회"""
        result = get_user_by_username(db, "notexistuser")

        assert result is None


class TestGetUserById:
    """ID로 사용자 조회 테스트"""

    def test_get_user_by_id_exists(self, db):
        """존재하는 ID로 조회"""
        # 사용자 생성
        created_user = create_user(
            db=db,
            username="iduser",
            email="id@example.com",
            password_hash="hash",
        )

        # ID로 조회
        found_user = get_user_by_id(db, created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "iduser"
        assert found_user.email == "id@example.com"

    def test_get_user_by_id_not_exists(self, db):
        """존재하지 않는 ID로 조회"""
        result = get_user_by_id(db, 99999)

        assert result is None
