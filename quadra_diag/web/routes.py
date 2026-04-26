from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import func

from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import get_logger
from quadra_diag.db.models import PredictionRecord, UploadReport, User
from quadra_diag.db.session import session_scope
from quadra_diag.ml.catalog import DISEASE_SPECS
from quadra_diag.schemas import DISEASE_PAYLOAD_MODELS, LoginForm, RegisterForm, PasswordChangeForm
from quadra_diag.services.auth import hash_password, verify_password, _is_strong_password
from quadra_diag.services.prediction import predict_disease
from quadra_diag.services.reporting import (
    BatchProcessingError,
    persist_batch_report,
    process_batch_upload,
)
from quadra_diag.services.explainability import compute_shap_values, get_feature_importance
from quadra_diag.services.pdf_generator import generate_assessment_pdf
from quadra_diag.services.analytics import (
    get_user_trends,
    get_disease_distribution,
    get_risk_distribution,
    get_system_metrics,
)
from quadra_diag.web.flash import pop_flashes, push_flash
from quadra_diag.core.cache import ttl_cache

logger = get_logger(__name__)
templates = Jinja2Templates(directory=str(get_settings().template_dir))
web_router = APIRouter()


@ttl_cache(ttl=60)
def _platform_metrics() -> dict:
    with session_scope() as session:
        total_users = session.query(func.count(User.id)).scalar() or 0
        total_assessments = session.query(func.count(PredictionRecord.id)).scalar() or 0
        total_reports = session.query(func.count(UploadReport.id)).scalar() or 0
    return {
        "total_users": int(total_users),
        "total_assessments": int(total_assessments),
        "total_reports": int(total_reports),
    }


def _get_current_user(request: Request) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    try:
        with session_scope() as session:
            return session.get(User, user_id)
    except Exception:
        return None


def _require_role(request: Request, roles: list[str]) -> User | None:
    user = _get_current_user(request)
    if not user:
        return None
    if user.role not in roles:
        return None
    return user


def _context(request: Request, **extra) -> dict:
    user = _get_current_user(request)
    return {
        "request": request,
        "app_name": get_settings().app_name,
        "diseases": DISEASE_SPECS,
        "current_user": user,
        "flashes": pop_flashes(request),
        "platform_metrics": _platform_metrics(),
        "dark_mode": request.session.get("dark_mode", False),
        "is_admin": user and user.role == "admin",
        "is_clinician": user and user.role in ["admin", "clinician"],
        **extra,
    }


def _render(request: Request, template_name: str, status_code: int = 200, **context) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=_context(request, **context),
        status_code=status_code,
    )


def _dashboard_payload(user_id: int) -> tuple[list[PredictionRecord], list[UploadReport], dict, list[dict]]:
    with session_scope() as session:
        predictions = (
            session.query(PredictionRecord)
            .filter(PredictionRecord.user_id == user_id)
            .order_by(PredictionRecord.created_at.desc())
            .limit(12)
            .all()
        )
        uploads = (
            session.query(UploadReport)
            .filter(UploadReport.user_id == user_id)
            .order_by(UploadReport.created_at.desc())
            .limit(8)
            .all()
        )

    stats = {
        "total": len(predictions),
        "high_risk": sum(1 for record in predictions if record.risk_band == "high"),
        "positive": sum(record.predicted_positive for record in predictions),
        "uploads": len(uploads),
    }
    distribution = [
        {"label": "Low", "value": sum(1 for r in predictions if r.risk_band == "low"), "tone": "low"},
        {"label": "Moderate", "value": sum(1 for r in predictions if r.risk_band == "moderate"), "tone": "moderate"},
        {"label": "High", "value": sum(1 for r in predictions if r.risk_band == "high"), "tone": "high"},
    ]
    return predictions, uploads, stats, distribution


@web_router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return _render(
        request,
        "home.html",
        disease_cards=list(DISEASE_SPECS.items()),
        upload_disease="diabetes",
    )


@web_router.get("/disease/{disease}", response_class=HTMLResponse)
def disease_form(request: Request, disease: str) -> HTMLResponse:
    spec = DISEASE_SPECS.get(disease)
    if not spec:
        return _render(request, "404.html", status_code=404)
    return _render(
        request,
        "disease_form.html",
        active_disease=disease,
        spec=spec,
        values={},
        errors=[],
    )


@web_router.post("/assess/{disease}", response_class=HTMLResponse)
async def assess(request: Request, disease: str) -> HTMLResponse:
    spec = DISEASE_SPECS.get(disease)
    if not spec:
        return _render(request, "404.html", status_code=404)

    form_data = dict(await request.form())
    try:
        payload = DISEASE_PAYLOAD_MODELS[disease](**form_data).model_dump()
        result = predict_disease(disease, payload)
    except ValidationError as exc:
        errors = [error["msg"] for error in exc.errors()]
        return _render(
            request,
            "disease_form.html",
            status_code=422,
            active_disease=disease,
            spec=spec,
            values=form_data,
            errors=errors,
        )

    shap_result = compute_shap_values(disease, payload)
    if shap_result:
        result["shap_explanation"] = shap_result
    importance = get_feature_importance(disease)
    if importance:
        result["feature_importance"] = importance

    current_user = _get_current_user(request)
    if current_user:
        with session_scope() as session:
            session.add(
                PredictionRecord(
                    disease=disease,
                    predicted_positive=result["predicted_positive"],
                    probability=result["probability"],
                    risk_band=result["risk_band"],
                    submitted_features=result["features"],
                    shap_values=shap_result,
                    feature_importance=importance,
                    user_id=current_user.id,
                )
            )
        push_flash(request, f"{spec['title']} completed and saved to your dashboard.", "success")

    logger.info("Generated %s assessment with risk band %s", disease, result["risk_band"])
    return _render(request, "result.html", result=result, spec=spec)


@web_router.get("/register", response_class=HTMLResponse)
def register_page(request: Request) -> HTMLResponse:
    return _render(request, "auth.html", mode="register", errors=[])


@web_router.post("/register")
async def register(request: Request):
    data = dict(await request.form())
    try:
        form = RegisterForm(**data)
    except ValidationError as exc:
        return _render(
            request,
            "auth.html",
            status_code=422,
            mode="register",
            errors=[error["msg"] for error in exc.errors()],
        )

    is_strong, pwd_error = _is_strong_password(form.password)
    if not is_strong:
        return _render(
            request,
            "auth.html",
            status_code=422,
            mode="register",
            errors=[pwd_error],
        )

    with session_scope() as session:
        existing = session.query(User).filter((User.email == form.email) | (User.username == form.username)).first()
        if existing:
            return _render(
                request,
                "auth.html",
                status_code=409,
                mode="register",
                errors=["A user with these credentials already exists."],
            )
        user = User(
            username=form.username,
            email=form.email,
            password_hash=hash_password(form.password),
            role=form.role,
        )
        session.add(user)
        session.flush()
        request.session["user_id"] = user.id
    push_flash(request, "Welcome to QuadraDiag. Your account is ready.", "success")
    return RedirectResponse(url="/dashboard", status_code=303)


@web_router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return _render(request, "auth.html", mode="login", errors=[])


@web_router.post("/login")
async def login(request: Request):
    data = dict(await request.form())
    try:
        form = LoginForm(**data)
    except ValidationError as exc:
        return _render(
            request,
            "auth.html",
            status_code=422,
            mode="login",
            errors=[error["msg"] for error in exc.errors()],
        )

    with session_scope() as session:
        user = session.query(User).filter(User.email == form.email).first()
        if not user or not verify_password(form.password, user.password_hash):
            return _render(
                request,
                "auth.html",
                status_code=401,
                mode="login",
                errors=["Invalid email or password."],
            )
        request.session["user_id"] = user.id
    push_flash(request, "Signed in successfully.", "success")
    return RedirectResponse(url="/dashboard", status_code=303)


@web_router.get("/logout")
def logout(request: Request):
    request.session.clear()
    push_flash(request, "Signed out successfully.", "info")
    return RedirectResponse(url="/", status_code=303)


@web_router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to access your workspace.", "info")
        return RedirectResponse(url="/login", status_code=303)

    predictions, uploads, stats, distribution = _dashboard_payload(current_user.id)
    trends = get_user_trends(current_user.id, 30)
    disease_dist = get_disease_distribution(current_user.id)
    risk_dist = get_risk_distribution(current_user.id)

    return _render(
        request,
        "dashboard.html",
        records=predictions,
        uploads=uploads,
        stats=stats,
        distribution=distribution,
        trends=trends,
        disease_dist=disease_dist,
        risk_dist=risk_dist,
    )


@web_router.post("/batch-lab/{disease}")
async def batch_lab(request: Request, disease: str, file: UploadFile = File(...)):
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Create an account to use the batch upload lab.", "info")
        return RedirectResponse(url="/login", status_code=303)
    if disease not in DISEASE_SPECS:
        return _render(request, "404.html", status_code=404)

    try:
        result_frame, summary = process_batch_upload(disease, file.filename or "upload.csv", await file.read())
    except BatchProcessingError as exc:
        predictions, uploads, stats, distribution = _dashboard_payload(current_user.id)
        trends = get_user_trends(current_user.id, 30)
        disease_dist = get_disease_distribution(current_user.id)
        risk_dist = get_risk_distribution(current_user.id)
        return _render(
            request,
            "dashboard.html",
            status_code=400,
            records=predictions,
            uploads=uploads,
            stats=stats,
            distribution=distribution,
            trends=trends,
            disease_dist=disease_dist,
            risk_dist=risk_dist,
            batch_error=str(exc),
        )

    with session_scope() as session:
        report = persist_batch_report(
            disease=disease,
            filename=file.filename or "upload.csv",
            frame=result_frame,
            summary=summary,
            user_id=current_user.id,
        )
        session.add(report)
        session.flush()
        report_id = report.id

    push_flash(request, "Batch report processed successfully and saved to your dashboard.", "success")
    return RedirectResponse(url=f"/reports/{report_id}", status_code=303)


@web_router.get("/reports/{report_id}", response_class=HTMLResponse)
def report_detail(request: Request, report_id: int) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to access reports.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        report = session.get(UploadReport, report_id)
        if not report or report.user_id != current_user.id:
            return _render(request, "404.html", status_code=404)

    return _render(request, "report_detail.html", report=report)


@web_router.get("/reports/{report_id}/download")
def download_report(request: Request, report_id: int):
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to download reports.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        report = session.get(UploadReport, report_id)
        if not report or report.user_id != current_user.id:
            return _render(request, "404.html", status_code=404)

    output_path = get_settings().report_dir / report.stored_filename
    if not output_path.exists():
        return _render(request, "404.html", status_code=404)
    return FileResponse(
        path=output_path,
        filename=f"{Path(report.original_filename).stem}_quadra_diag_report.csv",
        media_type="text/csv",
    )


@web_router.get("/reports/{report_id}/download-excel")
def download_report_excel(request: Request, report_id: int):
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to download reports.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        report = session.get(UploadReport, report_id)
        if not report or report.user_id != current_user.id:
            return _render(request, "404.html", status_code=404)

    csv_path = get_settings().report_dir / report.stored_filename
    if not csv_path.exists():
        return _render(request, "404.html", status_code=404)

    df = pd.read_csv(csv_path)
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={Path(report.original_filename).stem}_quadra_diag_report.xlsx"
        },
    )


@web_router.get("/templates/{disease}/download")
def download_template(disease: str):
    spec = DISEASE_SPECS.get(disease)
    if not spec:
        return RedirectResponse(url="/", status_code=303)
    sample_row = {feature["name"]: feature.get("placeholder", "") for feature in spec["features"]}
    frame = pd.DataFrame([sample_row])
    output_path = get_settings().report_dir / f"{disease}_batch_template.csv"
    get_settings().report_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return FileResponse(
        path=output_path,
        filename=f"{disease}_batch_template.csv",
        media_type="text/csv",
    )


@web_router.get("/assessments/{record_id}", response_class=HTMLResponse)
def assessment_detail(request: Request, record_id: int) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to view assessments.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        record = session.get(PredictionRecord, record_id)
        if not record or record.user_id != current_user.id:
            return _render(request, "404.html", status_code=404)

    spec = DISEASE_SPECS.get(record.disease, {})
    return _render(
        request,
        "assessment_detail.html",
        record=record,
        spec=spec,
    )


@web_router.get("/assessments/{record_id}/pdf")
def download_assessment_pdf(request: Request, record_id: int):
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to download reports.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        record = session.get(PredictionRecord, record_id)
        if not record or record.user_id != current_user.id:
            return _render(request, "404.html", status_code=404)

    spec = DISEASE_SPECS.get(record.disease, {})
    result = {
        "disease": record.disease,
        "predicted_positive": record.predicted_positive,
        "probability": record.probability,
        "risk_band": record.risk_band,
        "threshold": DISEASE_SPECS[record.disease]["threshold"],
        "benchmarks": [],
        "metrics": record.feature_importance or {"accuracy": 0.9, "f1": 0.85, "roc_auc": 0.92},
        "features": record.submitted_features,
        "shap_explanation": record.shap_values,
    }

    pdf_bytes = generate_assessment_pdf(result, spec)
    if pdf_bytes is None:
        push_flash(request, "PDF generation not available.", "error")
        return RedirectResponse(url=f"/assessments/{record_id}", status_code=303)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={record.disease}_assessment_{record_id}.pdf"
        },
    )


@web_router.get("/compare", response_class=HTMLResponse)
def compare_assessments(request: Request) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to use comparison.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        records = (
            session.query(PredictionRecord)
            .filter(PredictionRecord.user_id == current_user.id)
            .order_by(PredictionRecord.created_at.desc())
            .limit(20)
            .all()
        )

    return _render(request, "compare.html", records=records)


@web_router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to view analytics.", "info")
        return RedirectResponse(url="/login", status_code=303)

    trends = get_user_trends(current_user.id, 30)
    disease_dist = get_disease_distribution(current_user.id)
    risk_dist = get_risk_distribution(current_user.id)

    return _render(
        request,
        "analytics.html",
        trends=trends,
        disease_dist=disease_dist,
        risk_dist=risk_dist,
    )


@web_router.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to view your profile.", "info")
        return RedirectResponse(url="/login", status_code=303)

    predictions, uploads, stats, _ = _dashboard_payload(current_user.id)
    return _render(
        request,
        "profile.html",
        stats=stats,
        password_errors=[],
        password_success=None,
    )


@web_router.post("/profile/change-password")
async def change_password(request: Request):
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in.", "info")
        return RedirectResponse(url="/login", status_code=303)

    data = dict(await request.form())
    try:
        form = PasswordChangeForm(**data)
    except ValidationError as exc:
        predictions, uploads, stats, _ = _dashboard_payload(current_user.id)
        return _render(
            request,
            "profile.html",
            stats=stats,
            password_errors=[error["msg"] for error in exc.errors()],
            password_success=None,
        )

    if form.new_password != form.confirm_password:
        predictions, uploads, stats, _ = _dashboard_payload(current_user.id)
        return _render(
            request,
            "profile.html",
            stats=stats,
            password_errors=["Passwords do not match."],
            password_success=None,
        )

    is_strong, pwd_error = _is_strong_password(form.new_password)
    if not is_strong:
        predictions, uploads, stats, _ = _dashboard_payload(current_user.id)
        return _render(
            request,
            "profile.html",
            stats=stats,
            password_errors=[pwd_error],
            password_success=None,
        )

    with session_scope() as session:
        user = session.get(User, current_user.id)
        if not user or not verify_password(form.current_password, user.password_hash):
            predictions, uploads, stats, _ = _dashboard_payload(current_user.id)
            return _render(
                request,
                "profile.html",
                stats=stats,
                password_errors=["Current password is incorrect."],
                password_success=None,
            )
        user.password_hash = hash_password(form.new_password)

    push_flash(request, "Password updated successfully.", "success")
    predictions, uploads, stats, _ = _dashboard_payload(current_user.id)
    return _render(
        request,
        "profile.html",
        stats=stats,
        password_errors=[],
        password_success="Password updated successfully.",
    )


@web_router.get("/profile/export")
def export_user_data(request: Request):
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to export your data.", "info")
        return RedirectResponse(url="/login", status_code=303)

    with session_scope() as session:
        predictions = (
            session.query(PredictionRecord)
            .filter(PredictionRecord.user_id == current_user.id)
            .order_by(PredictionRecord.created_at.desc())
            .all()
        )
        uploads = (
            session.query(UploadReport)
            .filter(UploadReport.user_id == current_user.id)
            .order_by(UploadReport.created_at.desc())
            .all()
        )

    data = {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        },
        "predictions": [
            {
                "id": p.id,
                "disease": p.disease,
                "probability": p.probability,
                "risk_band": p.risk_band,
                "predicted_positive": p.predicted_positive,
                "submitted_features": p.submitted_features,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in predictions
        ],
        "uploads": [
            {
                "id": u.id,
                "disease": u.disease,
                "original_filename": u.original_filename,
                "total_rows": u.total_rows,
                "positive_predictions": u.positive_predictions,
                "high_risk": u.high_risk,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in uploads
        ],
    }

    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename={current_user.username}_export.json"},
    )


@web_router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> HTMLResponse:
    current_user = _get_current_user(request)
    if not current_user:
        push_flash(request, "Please sign in to access settings.", "info")
        return RedirectResponse(url="/login", status_code=303)
    return _render(request, "settings.html")


@web_router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request) -> HTMLResponse:
    user = _require_role(request, ["admin"])
    if not user:
        push_flash(request, "Admin access required.", "error")
        return RedirectResponse(url="/", status_code=303)

    metrics = get_system_metrics()
    with session_scope() as session:
        users = session.query(User).order_by(User.created_at.desc()).limit(50).all()
        recent_predictions = (
            session.query(PredictionRecord)
            .order_by(PredictionRecord.created_at.desc())
            .limit(20)
            .all()
        )

    return _render(
        request,
        "admin.html",
        metrics=metrics,
        users=users,
        recent_predictions=recent_predictions,
    )


@web_router.post("/toggle-dark-mode")
async def toggle_dark_mode(request: Request):
    current = request.session.get("dark_mode", False)
    request.session["dark_mode"] = not current
    return {"dark_mode": not current}

