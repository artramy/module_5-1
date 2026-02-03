"""
FastAPI 의존성 모듈

인증 및 공통 의존성 함수들을 제공합니다.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models.user import User
from app.crud.user import get_user_by_id
from app.utils.auth import decode_access_token

# Bearer 토큰 스키마
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자를 반환하는 의존성

    JWT 토큰을 검증하고 해당 사용자 객체를 반환합니다.

    Args:
        credentials: HTTP Authorization 헤더에서 추출한 Bearer 토큰
        db: SQLAlchemy 데이터베이스 세션

    Returns:
        User: 인증된 사용자 객체

    Raises:
        HTTPException 401: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # JWT 토큰 디코드
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # 사용자 조회
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user
