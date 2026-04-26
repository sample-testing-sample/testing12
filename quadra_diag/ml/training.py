from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import get_logger
from quadra_diag.ml.catalog import DISEASE_SPECS


logger = get_logger(__name__)


def _normalise_liver_frame(df: pd.DataFrame) -> pd.DataFrame:
    if "gender" in df.columns:
        df["gender"] = df["gender"].astype(str).str.strip().str.title()
    return df


def _clean_frame(disease: str, df: pd.DataFrame, feature_names: list[str], target_name: str) -> pd.DataFrame:
    frame = df.copy()
    if disease == "liver":
        frame = _normalise_liver_frame(frame)

    for feature_name in feature_names:
        if disease == "liver" and feature_name == "gender":
            continue
        frame[feature_name] = pd.to_numeric(frame[feature_name], errors="coerce")

    frame[target_name] = pd.to_numeric(frame[target_name], errors="coerce")
    before = len(frame)
    frame = frame.dropna(subset=feature_names + [target_name]).copy()
    dropped = before - len(frame)
    if dropped:
        logger.warning("Dropped %s malformed rows while training %s", dropped, disease)
    frame[target_name] = frame[target_name].astype(int)
    return frame


def _build_pipeline(disease: str, feature_names: list[str]) -> Pipeline:
    if disease == "liver":
        numeric_features = [name for name in feature_names if name != "gender"]
        categorical_features = ["gender"]
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    numeric_features,
                ),
                (
                    "categorical",
                    Pipeline(
                        steps=[
                            ("imputer", SimpleImputer(strategy="most_frequent")),
                            (
                                "encoder",
                                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                            ),
                        ]
                    ),
                    categorical_features,
                ),
            ]
        )
    else:
        preprocessor = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=2000)),
        ]
    )


def train_model(disease: str) -> tuple[Path, Path]:
    settings = get_settings()
    spec = DISEASE_SPECS[disease]
    dataset_path = settings.dataset_dir / spec["dataset"]
    model_path = settings.model_dir / spec["model_file"]
    metadata_path = settings.model_dir / spec["metadata_file"]
    settings.model_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(dataset_path)

    feature_names = [feature["name"] for feature in spec["features"]]
    target_name = spec["target"]
    df = _clean_frame(disease, df, feature_names, target_name)
    X = df[feature_names].copy()
    y = df[target_name]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = _build_pipeline(disease, feature_names)
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "f1": round(float(f1_score(y_test, predictions)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
    }
    stats = {}
    for feature_name in feature_names:
        series = X[feature_name]
        if pd.api.types.is_numeric_dtype(series):
            stats[feature_name] = {
                "median": round(float(series.median()), 4),
                "p25": round(float(series.quantile(0.25)), 4),
                "p75": round(float(series.quantile(0.75)), 4),
            }

    metadata = {
        "disease": disease,
        "features": feature_names,
        "metrics": metrics,
        "threshold": spec["threshold"],
        "stats": stats,
    }

    joblib.dump(pipeline, model_path)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info("Trained %s model with metrics %s", disease, metrics)
    return model_path, metadata_path


def ensure_models_ready() -> None:
    settings = get_settings()
    if not settings.model_auto_train:
        return
    for disease, spec in DISEASE_SPECS.items():
        model_path = settings.model_dir / spec["model_file"]
        metadata_path = settings.model_dir / spec["metadata_file"]
        if model_path.exists() and metadata_path.exists():
            continue
        train_model(disease)
