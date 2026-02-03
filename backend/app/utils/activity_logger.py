"""
Activity Logging 유틸리티

활동 기록을 위한 데코레이터와 유틸리티 클래스를 제공합니다.
"""

import functools
import inspect
import asyncio
from typing import Optional, Callable, Any

from sqlalchemy.orm import Session

from app.crud.activity import create_activity
from app.models.activity import Activity


def log_activity(
    action_type: Optional[str] = None,
    description: Optional[str] = None,
    include_args: bool = False
) -> Callable:
    """
    함수 호출 시 자동으로 활동을 기록하는 데코레이터

    동기 및 비동기 함수 모두 지원합니다.
    함수 파라미터에서 current_user를 찾아 user_id를 추출하고,
    db 세션을 사용하여 활동을 기록합니다.

    Args:
        action_type: 행동 유형 (기본값: 함수 이름)
        description: 행동 설명 (선택)
        include_args: 함수 인자를 extra_data에 포함할지 여부 (기본값: False)

    Returns:
        데코레이터 함수

    Usage:
        @log_activity(action_type="user_create", description="새 사용자 생성")
        def create_user(user_data: UserCreate, db: Session, current_user: User):
            ...

        @log_activity(include_args=True)
        async def get_user(user_id: int, db: Session, current_user: User):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # 원래 함수 실행
            result = await func(*args, **kwargs)

            # 활동 로깅 시도 (실패해도 원래 함수 결과는 반환)
            try:
                _log_activity_from_call(
                    func, args, kwargs,
                    action_type=action_type,
                    description=description,
                    include_args=include_args
                )
            except Exception:
                # 로깅 실패 시 조용히 무시 (원래 기능에 영향 없음)
                pass

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # 원래 함수 실행
            result = func(*args, **kwargs)

            # 활동 로깅 시도 (실패해도 원래 함수 결과는 반환)
            try:
                _log_activity_from_call(
                    func, args, kwargs,
                    action_type=action_type,
                    description=description,
                    include_args=include_args
                )
            except Exception:
                # 로깅 실패 시 조용히 무시 (원래 기능에 영향 없음)
                pass

            return result

        # 비동기 함수인지 확인하여 적절한 래퍼 반환
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _log_activity_from_call(
    func: Callable,
    args: tuple,
    kwargs: dict,
    action_type: Optional[str],
    description: Optional[str],
    include_args: bool
) -> Optional[Activity]:
    """
    함수 호출 정보에서 활동 로깅에 필요한 정보를 추출하여 기록

    Args:
        func: 호출된 함수
        args: 위치 인자
        kwargs: 키워드 인자
        action_type: 행동 유형
        description: 행동 설명
        include_args: 인자 포함 여부

    Returns:
        생성된 Activity 객체 또는 None
    """
    # 함수 시그니처 분석
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    all_args = bound_args.arguments

    # db 세션 추출
    db: Optional[Session] = all_args.get("db")
    if db is None:
        return None

    # current_user에서 user_id 추출
    current_user = all_args.get("current_user")
    if current_user is None:
        return None

    user_id = getattr(current_user, "id", None)
    if user_id is None:
        return None

    # action_type 결정 (기본값: 함수 이름)
    resolved_action_type = action_type if action_type else func.__name__

    # extra_data 구성
    extra_data = None
    if include_args:
        extra_data = _serialize_args(all_args)

    # 활동 기록 생성
    return create_activity(
        db=db,
        user_id=user_id,
        action_type=resolved_action_type,
        description=description,
        extra_data=extra_data
    )


def _serialize_args(args_dict: dict) -> dict:
    """
    함수 인자를 JSON 직렬화 가능한 형태로 변환

    Session, User 등의 객체는 문자열 표현으로 변환합니다.

    Args:
        args_dict: 함수 인자 딕셔너리

    Returns:
        직렬화된 인자 딕셔너리
    """
    serialized = {}
    for key, value in args_dict.items():
        # 민감하거나 직렬화 불가능한 객체 필터링
        if key in ("db", "current_user", "password", "password_hash"):
            continue

        try:
            # 기본 타입은 그대로 사용
            if isinstance(value, (str, int, float, bool, type(None))):
                serialized[key] = value
            elif isinstance(value, (list, tuple)):
                serialized[key] = [
                    v if isinstance(v, (str, int, float, bool, type(None))) else str(v)
                    for v in value
                ]
            elif isinstance(value, dict):
                serialized[key] = {
                    k: v if isinstance(v, (str, int, float, bool, type(None))) else str(v)
                    for k, v in value.items()
                }
            elif hasattr(value, "model_dump"):
                # Pydantic 모델
                serialized[key] = value.model_dump()
            elif hasattr(value, "dict"):
                # 구버전 Pydantic 모델
                serialized[key] = value.dict()
            else:
                # 기타 객체는 문자열로 변환
                serialized[key] = str(value)
        except Exception:
            serialized[key] = f"<{type(value).__name__}>"

    return serialized


class ActivityLogger:
    """
    활동 로깅을 위한 유틸리티 클래스

    일반적인 활동 로깅 시나리오를 위한 정적 메서드를 제공합니다.

    Usage:
        # 로그인 기록
        ActivityLogger.log_login(db, user_id=1, ip_address="192.168.1.1")

        # API 호출 기록
        ActivityLogger.log_api_call(db, user_id=1, endpoint="/api/users", method="GET")

        # 에러 기록
        ActivityLogger.log_error(db, user_id=1, error_type="ValueError", error_message="Invalid input")
    """

    @staticmethod
    def log_login(
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Activity]:
        """
        사용자 로그인 활동 기록

        Args:
            db: SQLAlchemy 세션
            user_id: 사용자 ID
            ip_address: 클라이언트 IP 주소 (선택)
            user_agent: 클라이언트 User-Agent (선택)

        Returns:
            생성된 Activity 객체 또는 None (실패 시)
        """
        try:
            extra_data = {}
            if ip_address:
                extra_data["ip_address"] = ip_address
            if user_agent:
                extra_data["user_agent"] = user_agent

            return create_activity(
                db=db,
                user_id=user_id,
                action_type="login",
                description="User logged in",
                extra_data=extra_data if extra_data else None
            )
        except Exception:
            return None

    @staticmethod
    def log_api_call(
        db: Session,
        user_id: int,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None
    ) -> Optional[Activity]:
        """
        API 호출 활동 기록

        Args:
            db: SQLAlchemy 세션
            user_id: 사용자 ID
            endpoint: API 엔드포인트 경로
            method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
            status_code: HTTP 응답 상태 코드 (선택)

        Returns:
            생성된 Activity 객체 또는 None (실패 시)
        """
        try:
            extra_data = {
                "endpoint": endpoint,
                "method": method
            }
            if status_code is not None:
                extra_data["status_code"] = status_code

            return create_activity(
                db=db,
                user_id=user_id,
                action_type="api_call",
                description=f"{method} {endpoint}",
                extra_data=extra_data
            )
        except Exception:
            return None

    @staticmethod
    def log_error(
        db: Session,
        user_id: int,
        error_type: str,
        error_message: str,
        traceback_info: Optional[str] = None
    ) -> Optional[Activity]:
        """
        에러 발생 활동 기록

        Args:
            db: SQLAlchemy 세션
            user_id: 사용자 ID
            error_type: 에러 유형 (예: "ValueError", "HTTPException")
            error_message: 에러 메시지
            traceback_info: 트레이스백 정보 (선택)

        Returns:
            생성된 Activity 객체 또는 None (실패 시)
        """
        try:
            extra_data = {
                "error_type": error_type,
                "error_message": error_message
            }
            if traceback_info:
                extra_data["traceback"] = traceback_info

            return create_activity(
                db=db,
                user_id=user_id,
                action_type="error",
                description=f"{error_type}: {error_message}",
                extra_data=extra_data
            )
        except Exception:
            return None
