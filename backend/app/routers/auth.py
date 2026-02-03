"""
인증 관련 API 라우터

회원가입, 로그인 등 인증 관련 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.crud import get_user_by_email, get_user_by_username, create_user
from app.database import get_db
from app.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입 엔드포인트

    새로운 사용자를 등록하고 JWT 액세스 토큰을 반환합니다.

    Args:
        user_data: 회원가입 요청 데이터 (username, email, password)
        db: SQLAlchemy 데이터베이스 세션

    Returns:
        Token: 액세스 토큰과 토큰 타입

    Raises:
        HTTPException 400: 이메일 또는 사용자명이 이미 등록된 경우

    로직:
    1. 중복 email 체크
    2. 중복 username 체크
    3. 비밀번호 해싱
    4. User 생성
    5. JWT 토큰 발급
    6. Token 응답 반환
    """
    # 1. 중복 email 체크
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 2. 중복 username 체크
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # 3. 비밀번호 해싱
    password_hash = hash_password(user_data.password)

    # 4. User 생성
    user = create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash
    )

    # 5. JWT 토큰 발급
    access_token = create_access_token(data={"sub": str(user.id)})

    # 6. Token 응답 반환
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    로그인 엔드포인트

    이메일과 비밀번호로 사용자를 인증하고 JWT 액세스 토큰을 반환합니다.

    Args:
        login_data: 로그인 요청 데이터 (email, password)
        db: SQLAlchemy 데이터베이스 세션

    Returns:
        Token: 액세스 토큰과 토큰 타입

    Raises:
        HTTPException 401: 이메일 또는 비밀번호가 틀린 경우

    로직:
    1. email로 사용자 조회
    2. 사용자가 없으면 401 Unauthorized
    3. 비밀번호 검증
    4. 비밀번호가 틀리면 401 Unauthorized
    5. JWT 토큰 발급
    6. Token 응답 반환
    """
    # 1. email로 사용자 조회
    user = get_user_by_email(db, login_data.email)

    # 2. 사용자가 없으면 401 에러
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 비밀번호 검증
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 5. JWT 토큰 발급
    access_token = create_access_token(data={"sub": str(user.id)})

    # 6. Token 응답 반환
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회

    JWT 토큰을 검증하고 해당 사용자의 정보를 반환합니다.

    Args:
        current_user: get_current_user 의존성에서 자동으로 주입되는 현재 사용자

    Returns:
        UserResponse: 사용자 정보 (id, username, email, created_at)
    """
    return current_user
