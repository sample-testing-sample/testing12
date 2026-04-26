from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from quadra_diag.ml.catalog import DISEASE_SPECS
from quadra_diag.schemas import (
    DISEASE_PAYLOAD_MODELS,
    DiabetesPayload,
    HeartPayload,
    LiverPayload,
    ParkinsonsPayload,
    HealthResponse,
    PredictionResponse,
    BatchResponse,
    BatchSummary,
    DiseaseListResponse,
    DiseaseSpec,
)
from quadra_diag.services.prediction import predict_disease
from quadra_diag.services.explainability import compute_shap_values, get_feature_importance
from quadra_diag.services.reporting import BatchProcessingError, process_batch_upload
from quadra_diag.services.analytics import (
    get_user_trends,
    get_disease_distribution,
    get_risk_distribution,
    get_system_metrics,
)


api_router = APIRouter()


@api_router.get("/health", response_model=HealthResponse)
def healthcheck() -> dict:
    return {
        "status": "ok",
        "version": "2.1.0",
        "features": ["shap", "pdf_export", "excel_export", "analytics", "dark_mode"],
    }


@api_router.get("/diseases", response_model=DiseaseListResponse)
def list_diseases() -> dict:
    specs = {}
    for key, spec in DISEASE_SPECS.items():
        specs[key] = DiseaseSpec(
            title=spec["title"],
            description=spec["description"],
            tagline=spec["tagline"],
            accent=spec["accent"],
            features_count=len(spec["features"]),
        )
    return {"diseases": specs}


@api_router.post("/predict/diabetes", response_model=PredictionResponse)
def predict_diabetes(payload: DiabetesPayload) -> dict:
    return _predict_with_explainability("diabetes", payload.model_dump())


@api_router.post("/predict/heart", response_model=PredictionResponse)
def predict_heart(payload: HeartPayload) -> dict:
    return _predict_with_explainability("heart", payload.model_dump())


@api_router.post("/predict/liver", response_model=PredictionResponse)
def predict_liver(payload: LiverPayload) -> dict:
    return _predict_with_explainability("liver", payload.model_dump())


@api_router.post("/predict/parkinsons", response_model=PredictionResponse)
def predict_parkinsons(payload: ParkinsonsPayload) -> dict:
    return _predict_with_explainability("parkinsons", payload.model_dump())


@api_router.post("/predict/{disease}", response_model=PredictionResponse)
def predict_dynamic(disease: str, payload: dict) -> dict:
    if disease not in DISEASE_SPECS:
        raise HTTPException(status_code=404, detail="Unknown disease type.")
    model = DISEASE_PAYLOAD_MODELS[disease]
    validated = model(**payload).model_dump()
    return _predict_with_explainability(disease, validated)


def _predict_with_explainability(disease: str, features: dict) -> dict:
    result = predict_disease(disease, features)
    shap = compute_shap_values(disease, features)
    importance = get_feature_importance(disease)
    if shap:
        result["shap_explanation"] = shap
    if importance:
        result["feature_importance"] = importance
    return result


@api_router.post("/predict/{disease}/batch", response_model=BatchResponse)
async def predict_batch_upload(disease: str, file: UploadFile = File(...)) -> dict:
    if disease not in DISEASE_SPECS:
        raise HTTPException(status_code=404, detail="Unknown disease type.")
    try:
        frame, summary = process_batch_upload(disease, file.filename or "upload.csv", await file.read())
    except BatchProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "disease": disease,
        "summary": BatchSummary(**summary),
        "preview": frame.head(10).to_dict(orient="records"),
    }


@api_router.get("/analytics/trends")
def analytics_trends(user_id: int, days: int = 30) -> dict:
    return get_user_trends(user_id, days)


@api_router.get("/analytics/disease-distribution")
def analytics_disease_distribution(user_id: int | None = None) -> dict:
    return get_disease_distribution(user_id)


@api_router.get("/analytics/risk-distribution")
def analytics_risk_distribution(user_id: int | None = None) -> dict:
    return get_risk_distribution(user_id)


@api_router.get("/admin/system-metrics")
def admin_system_metrics() -> dict:
    return get_system_metrics()


@api_router.get("/explain/{disease}")
def explain_prediction(disease: str, payload: dict) -> dict:
    if disease not in DISEASE_SPECS:
        raise HTTPException(status_code=404, detail="Unknown disease type.")
    model = DISEASE_PAYLOAD_MODELS[disease]
    validated = model(**payload).model_dump()
    shap = compute_shap_values(disease, validated)
    importance = get_feature_importance(disease)
    return {
        "disease": disease,
        "shap": shap,
        "feature_importance": importance,
    }

