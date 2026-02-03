from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """회원가입 요청 스키마"""
    username: str = Field(..., min_length=3, max_length=50, description="사용자 이름 (3-50자)")
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)")


class UserLogin(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호")


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
