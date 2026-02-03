"""
인증 유틸리티 모듈

비밀번호 해싱 및 JWT 토큰 관리를 위한 함수들을 제공합니다.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt, JWTError

from app.config import settings


def hash_password(password: str) -> str:
    """
    평문 비밀번호를 bcrypt로 해싱합니다.

    Args:
        password: 해싱할 평문 비밀번호

    Returns:
        bcrypt로 해싱된 비밀번호 문자열
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교합니다.

    Args:
        plain_password: 검증할 평문 비밀번호
        hashed_password: 저장된 해시 비밀번호

    Returns:
        비밀번호가 일치하면 True, 아니면 False
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:
    """
    JWT 액세스 토큰을 생성합니다.

    Args:
        data: 토큰에 포함할 페이로드 데이터 (예: {"sub": "user_id"})
        expires_delta: 토큰 만료 시간 (기본값: ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        JWT 인코딩된 액세스 토큰 문자열
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # JWT 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    JWT 토큰을 디코드하고 검증합니다.

    Args:
        token: 디코드할 JWT 토큰 문자열

    Returns:
        디코드된 페이로드 딕셔너리

    Raises:
        JWTError: 토큰이 유효하지 않거나 만료된 경우
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    return payload
