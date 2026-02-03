"""
인증 의존성 모듈

JWT 토큰을 검증하고 현재 로그인한 사용자를 반환하는 의존성 함수를 제공합니다.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.utils.auth import decode_access_token
from app.crud import get_user_by_id
from app.models.user import User

# OAuth2 토큰 URL 정의 (토큰을 어디서 얻는지 명시)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT 토큰에서 현재 사용자를 추출하는 의존성 함수

    로직:
    1. Authorization 헤더에서 Bearer 토큰 추출 (oauth2_scheme이 자동 처리)
    2. JWT 토큰 디코드
    3. user_id 추출
    4. DB에서 User 조회
    5. User가 없으면 401 Unauthorized
    6. User 객체 반환

    Args:
        token: JWT 액세스 토큰
        db: 데이터베이스 세션

    Returns:
        User: 현재 로그인한 사용자 객체

    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자가 없는 경우 401
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 2. JWT 토큰 디코드
        payload = decode_access_token(token)

        # 3. user_id 추출
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)

    except (JWTError, ValueError, KeyError):
        # JWTError: 토큰 디코드 실패
        # ValueError: user_id를 int로 변환 실패
        # KeyError: payload에서 필요한 키가 없음
        raise credentials_exception

    # 4. DB에서 User 조회
    user = get_user_by_id(db, user_id)

    # 5. User가 없으면 401
    if user is None:
        raise credentials_exception

    # 6. User 객체 반환
    return user
