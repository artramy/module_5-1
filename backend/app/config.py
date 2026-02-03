"""
애플리케이션 설정 관리 모듈

환경 변수 또는 기본값을 사용하여 설정을 관리합니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings:
    """애플리케이션 설정 클래스"""

    # JWT 설정
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-here-change-this-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )


# 설정 인스턴스 (싱글톤)
settings = Settings()
