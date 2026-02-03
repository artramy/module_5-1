"""
Dashboard API 라우터

대시보드 기능을 위한 API 엔드포인트를 제공합니다.
- 활동 기록 생성/조회/삭제
- 활동 통계 조회
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityStats
from app.crud import (
    create_activity,
    get_activities_by_user,
    get_activity_by_id,
    get_activity_stats,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_user_activity(
    activity_data: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    활동 기록 생성

    현재 로그인한 사용자의 활동을 기록합니다.

    Args:
        activity_data: 활동 생성 데이터 (action_type, description, extra_data)
        current_user: 현재 인증된 사용자 (JWT 토큰에서 추출)
        db: 데이터베이스 세션

    Returns:
        생성된 활동 정보
    """
    activity = create_activity(
        db=db,
        user_id=current_user.id,
        action_type=activity_data.action_type,
        description=activity_data.description,
        extra_data=activity_data.extra_data
    )
    return activity


@router.get("/activities", response_model=List[ActivityResponse])
def get_user_activities(
    limit: int = Query(50, ge=1, le=100, description="조회할 활동 개수 (1-100)"),
    offset: int = Query(0, ge=0, description="시작 위치 (페이지네이션)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 활동 목록 조회

    최신순으로 정렬되며, 페이지네이션을 지원합니다.

    Args:
        limit: 조회할 활동 개수 (기본 50, 최대 100)
        offset: 시작 위치 (기본 0)
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        활동 목록 (최신순 정렬)
    """
    activities = get_activities_by_user(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return activities


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity_detail(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 활동 상세 조회

    본인의 활동만 조회 가능합니다.

    Args:
        activity_id: 조회할 활동 ID
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        활동 상세 정보

    Raises:
        HTTPException 404: 활동을 찾을 수 없는 경우
        HTTPException 403: 본인의 활동이 아닌 경우
    """
    activity = get_activity_by_id(db=db, activity_id=activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # 권한 체크: 본인의 활동만 조회 가능
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this activity"
        )

    return activity


@router.get("/stats", response_model=ActivityStats)
def get_user_activity_stats(
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 8601 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 8601 형식)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자 활동 통계 조회

    start_date, end_date로 날짜 범위를 지정할 수 있습니다.

    Args:
        start_date: 시작 날짜 (선택)
        end_date: 종료 날짜 (선택)
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        활동 통계 (총 개수, 유형별 카운트, 날짜별 카운트, 가장 많은 행동)
    """
    stats = get_activity_stats(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return stats


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 활동 삭제

    본인의 활동만 삭제 가능합니다.

    Args:
        activity_id: 삭제할 활동 ID
        current_user: 현재 인증된 사용자
        db: 데이터베이스 세션

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: 활동을 찾을 수 없는 경우
        HTTPException 403: 본인의 활동이 아닌 경우
    """
    activity = get_activity_by_id(db=db, activity_id=activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # 권한 체크: 본인의 활동만 삭제 가능
    if activity.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this activity"
        )

    db.delete(activity)
    db.commit()

    return None
