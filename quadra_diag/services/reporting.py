from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pandas as pd
from pydantic import ValidationError

from quadra_diag.core.config import get_settings
from quadra_diag.db.models import UploadReport
from quadra_diag.ml.catalog import DISEASE_SPECS
from quadra_diag.schemas import DISEASE_PAYLOAD_MODELS
from quadra_diag.services.prediction import predict_batch


class BatchProcessingError(ValueError):
    pass


def _read_uploaded_table(filename: str, content: bytes) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    stream = BytesIO(content)
    if suffix == ".csv":
        return pd.read_csv(stream)
    raise BatchProcessingError("Upload a CSV file for batch processing.")


def process_batch_upload(disease: str, filename: str, content: bytes) -> tuple[pd.DataFrame, dict]:
    settings = get_settings()
    if len(content) > settings.max_upload_bytes:
        raise BatchProcessingError(
            f"File exceeds maximum size of {settings.max_upload_size_mb} MB."
        )

    frame = _read_uploaded_table(filename, content)
    required_columns = DISEASE_SPECS[disease]["feature_names"]
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise BatchProcessingError(
            "Missing required columns: " + ", ".join(missing)
        )

    if len(frame) > settings.max_batch_rows:
        raise BatchProcessingError(
            f"Batch exceeds maximum of {settings.max_batch_rows:,} rows."
        )

    subset = frame[required_columns].copy()
    model = DISEASE_PAYLOAD_MODELS[disease]
    validated_rows = []
    for index, row in enumerate(subset.to_dict(orient="records"), start=1):
        try:
            validated_rows.append(model(**row).model_dump())
        except ValidationError as exc:
            raise BatchProcessingError(
                f"Row {index} failed validation: {exc.errors()[0]['msg']}"
            ) from exc

    predictions = predict_batch(disease, validated_rows)
    result_frame = subset.copy()
    result_frame["predicted_positive"] = [item["predicted_positive"] for item in predictions]
    result_frame["probability"] = [item["probability"] for item in predictions]
    result_frame["risk_band"] = [item["risk_band"] for item in predictions]

    summary = {
        "total_rows": len(result_frame),
        "high_risk": int((result_frame["risk_band"] == "high").sum()),
        "moderate_risk": int((result_frame["risk_band"] == "moderate").sum()),
        "low_risk": int((result_frame["risk_band"] == "low").sum()),
        "positive_predictions": int(result_frame["predicted_positive"].sum()),
    }
    return result_frame, summary


def persist_batch_report(
    disease: str,
    filename: str,
    frame: pd.DataFrame,
    summary: dict,
    user_id: int | None = None,
) -> UploadReport:
    settings = get_settings()
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{disease}_{uuid4().hex}.csv"
    output_path = settings.report_dir / stored_name
    frame.to_csv(output_path, index=False)
    return UploadReport(
        disease=disease,
        original_filename=filename,
        stored_filename=stored_name,
        total_rows=summary["total_rows"],
        positive_predictions=summary["positive_predictions"],
        high_risk=summary["high_risk"],
        moderate_risk=summary["moderate_risk"],
        low_risk=summary["low_risk"],
        user_id=user_id,
    )

