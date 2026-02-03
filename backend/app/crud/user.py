from sqlalchemy.orm import Session

from app.models.user import User


def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    """
    새로운 사용자를 생성합니다.

    Args:
        db: SQLAlchemy 세션
        username: 사용자명
        email: 이메일
        password_hash: 비밀번호 해시

    Returns:
        생성된 User 객체
    """
    db_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    이메일로 사용자를 조회합니다.

    Args:
        db: SQLAlchemy 세션
        email: 조회할 이메일

    Returns:
        User 객체 또는 None (존재하지 않는 경우)
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    사용자명으로 사용자를 조회합니다.

    Args:
        db: SQLAlchemy 세션
        username: 조회할 사용자명

    Returns:
        User 객체 또는 None (존재하지 않는 경우)
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    사용자 ID로 사용자를 조회합니다.

    Args:
        db: SQLAlchemy 세션
        user_id: 조회할 사용자 ID

    Returns:
        User 객체 또는 None (존재하지 않는 경우)
    """
    return db.query(User).filter(User.id == user_id).first()
