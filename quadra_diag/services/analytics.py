"""Analytics and insights service."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func

from quadra_diag.core.logging import get_logger
from quadra_diag.db.models import PredictionRecord, UploadReport, User, ModelPerformance
from quadra_diag.db.session import session_scope

logger = get_logger(__name__)


def get_user_trends(user_id: int, days: int = 30) -> dict:
    """Get time-series prediction trends for a user."""
    cutoff = datetime.now() - timedelta(days=days)
    with session_scope() as session:
        records = (
            session.query(PredictionRecord)
            .filter(PredictionRecord.user_id == user_id)
            .filter(PredictionRecord.created_at >= cutoff)
            .order_by(PredictionRecord.created_at)
            .all()
        )

    if not records:
        return {"labels": [], "datasets": []}

    # Group by date
    daily = defaultdict(lambda: {"count": 0, "avg_prob": 0.0, "high": 0})
    for r in records:
        date_key = r.created_at.strftime("%Y-%m-%d")
        daily[date_key]["count"] += 1
        daily[date_key]["avg_prob"] += r.probability
        if r.risk_band == "high":
            daily[date_key]["high"] += 1

    labels = sorted(daily.keys())
    for label in labels:
        daily[label]["avg_prob"] /= daily[label]["count"]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Avg Probability",
                "data": [round(daily[l]["avg_prob"] * 100, 1) for l in labels],
                "color": "#0d6b52",
            },
            {
                "label": "High Risk Count",
                "data": [daily[l]["high"] for l in labels],
                "color": "#8c2e24",
            },
        ],
    }


def get_disease_distribution(user_id: int | None = None) -> dict:
    """Get disease-wise prediction distribution."""
    with session_scope() as session:
        query = session.query(PredictionRecord.disease, func.count(PredictionRecord.id))
        if user_id:
            query = query.filter(PredictionRecord.user_id == user_id)
        results = query.group_by(PredictionRecord.disease).all()

    return {
        "labels": [r[0].title() for r in results],
        "data": [r[1] for r in results],
        "colors": ["#0d6b52", "#c45542", "#b07820", "#4a5ec8"],
    }


def get_risk_distribution(user_id: int | None = None) -> dict:
    """Get risk band distribution."""
    with session_scope() as session:
        query = session.query(PredictionRecord.risk_band, func.count(PredictionRecord.id))
        if user_id:
            query = query.filter(PredictionRecord.user_id == user_id)
        results = query.group_by(PredictionRecord.risk_band).all()

    risk_map = {"low": 0, "moderate": 0, "high": 0}
    for band, count in results:
        risk_map[band] = count

    return {
        "labels": ["Low", "Moderate", "High"],
        "data": [risk_map["low"], risk_map["moderate"], risk_map["high"]],
        "colors": ["#1a7a58", "#a86a14", "#8c2e24"],
    }


def get_system_metrics() -> dict:
    """Get platform-wide system metrics for admin dashboard."""
    with session_scope() as session:
        total_users = session.query(func.count(User.id)).scalar() or 0
        total_predictions = session.query(func.count(PredictionRecord.id)).scalar() or 0
        total_uploads = session.query(func.count(UploadReport.id)).scalar() or 0

        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_predictions = (
            session.query(func.count(PredictionRecord.id))
            .filter(PredictionRecord.created_at >= week_ago)
            .scalar()
            or 0
        )
        recent_uploads = (
            session.query(func.count(UploadReport.id))
            .filter(UploadReport.created_at >= week_ago)
            .scalar()
            or 0
        )

        # Disease breakdown
        disease_breakdown = (
            session.query(PredictionRecord.disease, func.count(PredictionRecord.id))
            .group_by(PredictionRecord.disease)
            .all()
        )

        # User roles
        role_breakdown = (
            session.query(User.role, func.count(User.id))
            .group_by(User.role)
            .all()
        )

    return {
        "total_users": int(total_users),
        "total_predictions": int(total_predictions),
        "total_uploads": int(total_uploads),
        "recent_predictions": int(recent_predictions),
        "recent_uploads": int(recent_uploads),
        "disease_breakdown": {d: int(c) for d, c in disease_breakdown},
        "role_breakdown": {r: int(c) for r, c in role_breakdown},
    }


def get_model_performance_history(disease: str) -> dict:
    """Get model performance history for drift detection."""
    with session_scope() as session:
        records = (
            session.query(ModelPerformance)
            .filter(ModelPerformance.disease == disease)
            .order_by(ModelPerformance.created_at)
            .limit(20)
            .all()
        )

    return {
        "labels": [r.created_at.strftime("%Y-%m-%d %H:%M") for r in records],
        "accuracy": [round(r.accuracy, 3) for r in records],
        "f1": [round(r.f1_score, 3) for r in records],
        "roc_auc": [round(r.roc_auc, 3) for r in records],
    }

