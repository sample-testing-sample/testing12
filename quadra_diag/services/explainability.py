"""SHAP-based model explainability service."""

from __future__ import annotations

from typing import Any

import numpy as np

from quadra_diag.core.config import get_settings
from quadra_diag.core.logging import get_logger
from quadra_diag.services.prediction import load_bundle

logger = get_logger(__name__)

_shap_available_cache = None


def _shap_available() -> bool:
    global _shap_available_cache
    if _shap_available_cache is None:
        try:
            import shap  # type: ignore # noqa: F401
            _shap_available_cache = True
        except Exception:
            _shap_available_cache = False
    return _shap_available_cache


def compute_shap_values(disease: str, features: dict) -> dict[str, Any] | None:
    """Compute SHAP values for a single prediction."""
    settings = get_settings()
    if not settings.enable_shap or not _shap_available():
        return None

    try:
        import shap  # type: ignore

        model, metadata = load_bundle(disease)
        feature_names = metadata["features"]
        import pandas as pd
        X_sample = pd.DataFrame([{k: features[k] for k in feature_names}])

        classifier = model.named_steps["classifier"]
        preprocessor = model.named_steps["preprocessor"]
        X_processed = preprocessor.transform(X_sample)

        try:
            explainer = shap.TreeExplainer(classifier)
            shap_vals = explainer.shap_values(X_processed)
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[1]
            base_value = float(explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value)
        except Exception:
            masker = shap.sample(X_processed, 100)
            explainer = shap.KernelExplainer(classifier.predict_proba, masker)
            shap_vals = explainer.shap_values(X_processed, nsamples=100)[1]
            base_value = float(explainer.expected_value[1])

        shap_vals_flat = np.array(shap_vals).flatten().tolist()
        feature_contributions = dict(zip(feature_names, shap_vals_flat))
        sorted_contributions = dict(sorted(feature_contributions.items(), key=lambda x: abs(x[1]), reverse=True))

        return {
            "base_value": round(base_value, 4),
            "prediction": round(base_value + sum(shap_vals_flat), 4),
            "feature_contributions": {k: round(v, 4) for k, v in sorted_contributions.items()},
            "top_positive": [k for k, v in sorted_contributions.items() if v > 0][:3],
            "top_negative": [k for k, v in sorted_contributions.items() if v < 0][:3],
        }
    except Exception as exc:
        logger.warning("SHAP computation failed for %s: %s", disease, exc)
        return None


def get_feature_importance(disease: str) -> dict[str, float] | None:
    try:
        model, metadata = load_bundle(disease)
        classifier = model.named_steps["classifier"]
        feature_names = metadata["features"]

        if hasattr(classifier, "coef_"):
            importance = np.abs(classifier.coef_[0]).tolist()
        elif hasattr(classifier, "feature_importances_"):
            importance = classifier.feature_importances_.tolist()
        else:
            return None

        return dict(sorted(zip(feature_names, [round(v, 4) for v in importance]), key=lambda x: x[1], reverse=True))
    except Exception as exc:
        logger.warning("Feature importance failed for %s: %s", disease, exc)
        return None

