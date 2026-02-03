"""
테스트 픽스처 설정

테스트용 인메모리 SQLite DB를 사용하여 각 테스트를 격리합니다.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base


# 테스트용 인메모리 SQLite DB
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db() -> Session:
    """
    테스트용 DB 세션 픽스처

    각 테스트마다 새로운 인메모리 DB를 생성하고,
    테스트 종료 후 정리합니다.

    Yields:
        Session: SQLAlchemy 세션 객체
    """
    # 테스트용 엔진 생성
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 세션 생성
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()

    yield session

    # 정리
    session.close()
    Base.metadata.drop_all(bind=engine)
