"""Simple SQLite migration helpers for schema evolution."""

from __future__ import annotations

from sqlalchemy import create_engine, inspect, text

from quadra_diag.core.logging import get_logger

logger = get_logger(__name__)


def _sqlite_add_column(engine, table: str, column: str, col_def: str) -> None:
    with engine.connect() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}"))
        conn.commit()
        logger.info("Added column %s to %s", column, table)


def migrate_sqlite_schema(engine) -> None:
    """Add missing columns to existing SQLite tables."""
    inspector = inspect(engine)

    # users table migrations
    user_cols = {c["name"] for c in inspector.get_columns("users")}
    if "role" not in user_cols:
        _sqlite_add_column(engine, "users", "role", "VARCHAR(20) DEFAULT 'patient'")
    if "is_active" not in user_cols:
        _sqlite_add_column(engine, "users", "is_active", "BOOLEAN DEFAULT 1")

    # prediction_records table migrations
    pred_cols = {c["name"] for c in inspector.get_columns("prediction_records")}
    if "shap_values" not in pred_cols:
        _sqlite_add_column(engine, "prediction_records", "shap_values", "JSON")
    if "feature_importance" not in pred_cols:
        _sqlite_add_column(engine, "prediction_records", "feature_importance", "JSON")

    # model_performances table migrations
    tables = inspector.get_table_names()
    if "model_performances" not in tables:
        from quadra_diag.db.models import Base
        Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables["model_performances"]])

    if "notifications" not in tables:
        from quadra_diag.db.models import Base
        Base.metadata.create_all(bind=engine, tables=[Base.metadata.tables["notifications"]])

