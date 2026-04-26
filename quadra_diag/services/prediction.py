from __future__ import annotations

import json
from functools import lru_cache

import joblib
import pandas as pd

from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import get_logger
from quadra_diag.ml.catalog import DISEASE_SPECS

logger = get_logger(__name__)


def _risk_band(probability: float) -> str:
    if probability >= 0.75:
        return "high"
    if probability >= 0.45:
        return "moderate"
    return "low"


@lru_cache(maxsize=8)
def load_bundle(disease: str) -> tuple[object, dict]:
    settings = get_settings()
    spec = DISEASE_SPECS[disease]
    model = joblib.load(settings.model_dir / spec["model_file"])
    metadata = json.loads((settings.model_dir / spec["metadata_file"]).read_text(encoding="utf-8"))
    return model, metadata


def get_benchmarks(disease: str, features: dict) -> list[str]:
    _, metadata = load_bundle(disease)
    insights = []
    for field in DISEASE_SPECS[disease]["highlights"]:
        stats = metadata["stats"].get(field)
        if not stats:
            continue
        value = features.get(field)
        if value is None:
            continue
        if value >= stats["p75"]:
            insights.append(f"{field} is above the 75th percentile of the training data.")
        elif value <= stats["p25"]:
            insights.append(f"{field} is below the 25th percentile of the training data.")
    return insights


def _prepare_frame(disease: str, records: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(records)
    if disease == "liver" and "gender" in frame.columns:
        frame["gender"] = frame["gender"].astype(str).str.strip().str.title()
    return frame


def predict_batch(disease: str, records: list[dict]) -> list[dict]:
    model, metadata = load_bundle(disease)
    frame = _prepare_frame(disease, records)
    probabilities = model.predict_proba(frame)[:, 1]
    threshold = float(metadata["threshold"])
    results = []
    for record, probability in zip(records, probabilities, strict=False):
        probability_value = float(probability)
        results.append(
            {
                "predicted_positive": int(probability_value >= threshold),
                "probability": round(probability_value, 4),
                "risk_band": _risk_band(probability_value),
                "benchmarks": get_benchmarks(disease, record),
                "features": record,
            }
        )
    return results


def predict_disease(disease: str, features: dict) -> dict:
    metadata = load_bundle(disease)[1]
    prediction = predict_batch(disease, [features])[0]
    threshold = float(metadata["threshold"])
    return {
        "disease": disease,
        "predicted_positive": prediction["predicted_positive"],
        "probability": prediction["probability"],
        "risk_band": prediction["risk_band"],
        "threshold": threshold,
        "benchmarks": prediction["benchmarks"],
        "metrics": metadata["metrics"],
        "features": features,
    }

