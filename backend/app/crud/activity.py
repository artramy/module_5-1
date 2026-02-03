from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.models.activity import Activity


def create_activity(
    db: Session,
    user_id: int,
    action_type: str,
    description: Optional[str] = None,
    extra_data: Optional[dict] = None
) -> Activity:
    """
    활동 기록 생성

    Args:
        db: SQLAlchemy 세션
        user_id: 사용자 ID
        action_type: 행동 유형 (예: "login", "query", "click")
        description: 행동 설명 (선택)
        extra_data: 추가 정보 (선택)

    Returns:
        생성된 Activity 객체
    """
    db_activity = Activity(
        user_id=user_id,
        action_type=action_type,
        description=description,
        extra_data=extra_data
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def get_activities_by_user(
    db: Session,
    user_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Activity]:
    """
    사용자별 활동 조회 (최신순)

    Args:
        db: SQLAlchemy 세션
        user_id: 사용자 ID
        limit: 조회 개수 (기본 50)
        offset: 시작 위치 (페이지네이션)

    Returns:
        Activity 객체 리스트
    """
    return db.query(Activity)\
        .filter(Activity.user_id == user_id)\
        .order_by(Activity.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()


def get_activity_by_id(db: Session, activity_id: int) -> Optional[Activity]:
    """
    특정 활동 조회

    Args:
        db: SQLAlchemy 세션
        activity_id: 활동 ID

    Returns:
        Activity 객체 또는 None
    """
    return db.query(Activity).filter(Activity.id == activity_id).first()


def get_activities_by_type(
    db: Session,
    user_id: int,
    action_type: str,
    limit: int = 50,
    offset: int = 0
) -> List[Activity]:
    """
    유형별 활동 조회

    Args:
        db: SQLAlchemy 세션
        user_id: 사용자 ID
        action_type: 행동 유형
        limit: 조회 개수
        offset: 시작 위치

    Returns:
        필터링된 Activity 객체 리스트
    """
    return db.query(Activity)\
        .filter(and_(
            Activity.user_id == user_id,
            Activity.action_type == action_type
        ))\
        .order_by(Activity.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()


def get_activity_stats(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    사용자 활동 통계 조회

    Args:
        db: SQLAlchemy 세션
        user_id: 사용자 ID
        start_date: 시작 날짜 (선택)
        end_date: 종료 날짜 (선택)

    Returns:
        통계 딕셔너리 {
            "total_count": int,
            "by_type": {"login": 10, "query": 20, ...},
            "by_date": {"2024-01-01": 5, ...},
            "most_common_action": str
        }
    """
    query = db.query(Activity).filter(Activity.user_id == user_id)

    # 날짜 필터링
    if start_date:
        query = query.filter(Activity.created_at >= start_date)
    if end_date:
        query = query.filter(Activity.created_at <= end_date)

    activities = query.all()

    # 총 개수
    total_count = len(activities)

    # 유형별 카운트
    by_type = {}
    for activity in activities:
        by_type[activity.action_type] = by_type.get(activity.action_type, 0) + 1

    # 날짜별 카운트
    by_date = {}
    for activity in activities:
        date_str = activity.created_at.strftime("%Y-%m-%d")
        by_date[date_str] = by_date.get(date_str, 0) + 1

    # 가장 많은 행동
    most_common_action = max(by_type, key=by_type.get) if by_type else None

    return {
        "total_count": total_count,
        "by_type": by_type,
        "by_date": by_date,
        "most_common_action": most_common_action
    }


def delete_old_activities(db: Session, days: int = 90) -> int:
    """
    오래된 활동 삭제

    Args:
        db: SQLAlchemy 세션
        days: 보관 일수 (기본 90일)

    Returns:
        삭제된 활동 개수
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    deleted_count = db.query(Activity)\
        .filter(Activity.created_at < cutoff_date)\
        .delete()
    db.commit()
    return deleted_count
