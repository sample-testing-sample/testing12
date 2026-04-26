"""Production middleware stack for QuadraDiag."""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from quadra_diag.core.config import get_settings


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request ID and start time to every request."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request.state.request_id = uuid.uuid4().hex[:12]
        request.state.start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - request.state.start_time) * 1000
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        return response


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """Block requests with non-standard host headers in production."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        if settings.app_env == "production":
            host = request.headers.get("host", "").split(":")[0]
            allowed = {"localhost", "127.0.0.1", "quadra-diag.vercel.app", "quadra-diag.com"}
            if host not in allowed and not host.endswith(".vercel.app"):
                return Response("Invalid host header", status_code=400)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


def add_middleware_stack(app: FastAPI) -> FastAPI:
    """Register all middleware in correct order."""
    settings = get_settings()

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(TrustedHostMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
    return app

