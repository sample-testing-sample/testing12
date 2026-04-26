from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from quadra_diag.api.routes import api_router
from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import configure_logging, get_logger
from quadra_diag.core.middleware import add_middleware_stack
from quadra_diag.db.session import init_db
from quadra_diag.ml.training import ensure_models_ready
from quadra_diag.web.routes import web_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info("Starting %s v3.0 in %s mode", settings.app_name, settings.app_env)
    settings.runtime_dir.mkdir(parents=True, exist_ok=True)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    settings.pdf_dir.mkdir(parents=True, exist_ok=True)
    init_db()
    ensure_models_ready()
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="3.0.0",
        description=(
            "Advanced multi-disease risk assessment platform with SHAP explainability, "
            "batch analytics, PDF reports, and role-based access control."
        ),
        lifespan=lifespan,
    )
    add_middleware_stack(app)
    app.mount(
        "/assets",
        StaticFiles(directory=str(settings.static_dir)),
        name="assets",
    )
    if settings.media_dir.exists():
        app.mount(
            "/media",
            StaticFiles(directory=str(settings.media_dir)),
            name="media",
        )
    app.include_router(web_router)
    app.include_router(api_router, prefix="/api/v1", tags=["API"])

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        accept = request.headers.get("accept", "")
        wants_html = "text/html" in accept or "*/*" in accept or not accept
        if exc.status_code == 404 and wants_html:
            from fastapi.templating import Jinja2Templates
            templates = Jinja2Templates(directory=str(settings.template_dir))
            return templates.TemplateResponse(
                request=request,
                name="404.html",
                context={
                    "request": request,
                    "app_name": settings.app_name,
                    "diseases": {},
                    "current_user": None,
                    "flashes": [],
                    "platform_metrics": {"total_users": 0, "total_assessments": 0, "total_reports": 0},
                },
                status_code=404,
            )
        return HTMLResponse(content=f'{{"detail":"{exc.detail}"}}', status_code=exc.status_code)

    return app


app = create_app()
