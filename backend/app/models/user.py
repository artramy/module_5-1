from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    User 모델

    Attributes:
        id: Primary Key, Auto Increment
        username: 사용자명 (50자 이내, Unique, Not Null)
        email: 이메일 (100자 이내, Unique, Not Null)
        password_hash: 비밀번호 해시 (255자 이내, Not Null)
        created_at: 생성 시간 (기본값: 현재 시간)
        updated_at: 수정 시간 (기본값: 현재 시간, 수정 시 자동 업데이트)

    Indexes:
        - ix_users_username: username (unique)
        - ix_users_email: email (unique)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_email", "email", unique=True),
    )

    # 관계 설정 - Activity와 1:N 관계
    # cascade="all, delete-orphan": 사용자 삭제 시 관련 활동도 삭제
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
