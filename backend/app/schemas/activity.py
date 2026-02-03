from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict


class ActivityCreate(BaseModel):
    """활동 생성 요청 스키마"""
    action_type: str = Field(..., min_length=1, max_length=100, description="행동 유형")
    description: Optional[str] = Field(None, description="행동 설명")
    extra_data: Optional[Dict] = Field(None, description="추가 정보 (JSON)")


class ActivityResponse(BaseModel):
    """활동 정보 응답 스키마"""
    id: int
    user_id: int
    action_type: str
    description: Optional[str]
    extra_data: Optional[Dict]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityStats(BaseModel):
    """활동 통계 응답 스키마"""
    total_count: int = Field(..., description="총 활동 개수")
    by_type: Dict[str, int] = Field(..., description="유형별 카운트")
    by_date: Dict[str, int] = Field(..., description="날짜별 카운트")
    most_common_action: Optional[str] = Field(None, description="가장 많은 행동")
