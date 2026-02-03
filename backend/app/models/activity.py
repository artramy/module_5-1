from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Activity(Base):
    """
    Activity 모델 - AI 행동 추적

    Attributes:
        id: Primary Key, Auto Increment
        user_id: 활동을 수행한 사용자 (users.id 참조, Not Null)
        action_type: 행동 유형 (100자 이내, Not Null) - 예: "login", "query", "click"
        description: 행동 설명 (Optional)
        extra_data: JSON 형태의 추가 정보 (Optional) - 예: {"ip": "127.0.0.1", "browser": "Chrome"}
        created_at: 활동 발생 시간 (기본값: 현재 시간)

    Indexes:
        - user_id: 사용자별 조회 성능 향상
        - action_type: 유형별 필터링
        - created_at: 시간별 조회

    Relationships:
        - user: User 모델과 N:1 관계
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 관계 설정 - User와 양방향 관계
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<Activity(id={self.id}, user_id={self.user_id}, action_type='{self.action_type}')>"
