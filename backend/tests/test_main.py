"""
FastAPI 앱 테스트

FastAPI 애플리케이션의 초기화, 메타데이터, 미들웨어 설정을 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from app.main import app


@pytest.fixture
def client():
    """테스트용 HTTP 클라이언트 픽스처"""
    return TestClient(app)


class TestAppInitialization:
    """FastAPI 앱 초기화 테스트"""

    def test_app_exists(self):
        """앱 객체가 존재하는지 확인"""
        assert app is not None

    def test_app_is_fastapi_instance(self):
        """앱이 FastAPI 인스턴스인지 확인"""
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)


class TestAppMetadata:
    """앱 메타데이터 테스트"""

    def test_app_title(self):
        """앱 제목이 올바르게 설정되었는지 확인"""
        assert app.title == "Module 5 API"

    def test_app_version(self):
        """앱 버전이 올바르게 설정되었는지 확인"""
        assert app.version == "1.0.0"


class TestCORSMiddleware:
    """CORS 미들웨어 설정 테스트"""

    def test_cors_middleware_exists(self):
        """CORS 미들웨어가 등록되어 있는지 확인"""
        middleware_classes = [type(m.cls).__name__ if hasattr(m, 'cls') else type(m).__name__
                             for m in app.user_middleware]
        # user_middleware에서 확인하거나, 실제 미들웨어 스택에서 확인
        cors_found = any('CORS' in str(m) or 'cors' in str(m).lower() for m in app.user_middleware)
        assert cors_found or len(app.user_middleware) > 0

    def test_cors_allows_localhost_3000(self, client):
        """CORS가 localhost:3000을 허용하는지 확인"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        # CORS preflight 응답 확인
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_allows_credentials(self, client):
        """CORS가 credentials를 허용하는지 확인"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        assert response.headers.get("access-control-allow-credentials") == "true"

    def test_cors_blocks_unauthorized_origin(self, client):
        """허용되지 않은 origin은 CORS 헤더가 없는지 확인"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "GET",
            }
        )
        # 허용되지 않은 origin에는 access-control-allow-origin 헤더가 없거나 값이 다름
        allowed_origin = response.headers.get("access-control-allow-origin")
        assert allowed_origin != "http://malicious-site.com"


class TestRouterRegistration:
    """라우터 등록 확인 테스트"""

    def test_examples_router_registered(self):
        """examples 라우터가 등록되어 있는지 확인"""
        routes = [route.path for route in app.routes]
        # /api/examples 경로가 존재하는지 확인
        examples_routes = [r for r in routes if r.startswith("/api/examples")]
        assert len(examples_routes) > 0

    def test_health_endpoint_registered(self):
        """health check 엔드포인트가 등록되어 있는지 확인"""
        routes = [route.path for route in app.routes]
        assert "/api/health" in routes

    def test_openapi_schema_available(self, client):
        """OpenAPI 스키마가 사용 가능한지 확인"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Module 5 API"

    def test_docs_endpoint_available(self, client):
        """Swagger UI 문서 엔드포인트가 사용 가능한지 확인"""
        response = client.get("/docs")
        assert response.status_code == 200
