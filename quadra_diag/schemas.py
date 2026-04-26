from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterForm(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["patient", "clinician", "admin"] = "patient"


class LoginForm(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class PasswordChangeForm(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class DiabetesPayload(BaseModel):
    Pregnancies: int = Field(ge=0)
    Glucose: float = Field(ge=0)
    BloodPressure: float = Field(ge=0)
    SkinThickness: float = Field(ge=0)
    Insulin: float = Field(ge=0)
    BMI: float = Field(ge=0)
    DiabetesPedigreeFunction: float = Field(ge=0)
    Age: int = Field(ge=1)


class HeartPayload(BaseModel):
    age: int = Field(ge=1)
    sex: int = Field(ge=0, le=1)
    cp: int = Field(ge=0, le=3)
    trestbps: float = Field(ge=0)
    chol: float = Field(ge=0)
    fbs: int = Field(ge=0, le=1)
    restecg: int = Field(ge=0, le=2)
    thalach: float = Field(ge=0)
    exang: int = Field(ge=0, le=1)
    oldpeak: float = Field(ge=0)
    slope: int = Field(ge=0, le=2)
    ca: int = Field(ge=0, le=4)
    thal: int = Field(ge=0, le=3)


class LiverPayload(BaseModel):
    age: int = Field(ge=1)
    gender: Literal["Male", "Female", "male", "female"]
    tot_bilirubin: float = Field(ge=0)
    direct_bilirubin: float = Field(ge=0)
    tot_proteins: float = Field(ge=0)
    albumin: float = Field(ge=0)
    ag_ratio: float = Field(ge=0)
    sgpt: float = Field(ge=0)
    sgot: float = Field(ge=0)
    alkphos: float = Field(ge=0)

    @field_validator("gender")
    @classmethod
    def normalize_gender(cls, value: str) -> str:
        return value.strip().title()


class ParkinsonsPayload(BaseModel):
    MDVP_Fo: float = Field(ge=0)
    MDVP_Fhi: float = Field(ge=0)
    MDVP_Flo: float = Field(ge=0)
    Jitter: float = Field(ge=0)
    Jitter_Abs: float = Field(ge=0)
    MDVP_RAP: float = Field(ge=0)
    MDVP_PPQ: float = Field(ge=0)
    Jitter_DDP: float = Field(ge=0)
    MDVP_Shimmer: float = Field(ge=0)
    MDVP_Shimmer_dB: float = Field(ge=0)
    Shimmer_APQ3: float = Field(ge=0)
    Shimmer_APQ5: float = Field(ge=0)
    MDVP_APQ: float = Field(ge=0)
    Shimmer_DDA: float = Field(ge=0)
    NHR: float = Field(ge=0)
    HNR: float = Field(ge=0)
    RPDE: float = Field(ge=0)
    DFA: float = Field(ge=0)
    spread1: float
    spread2: float = Field(ge=0)
    D2: float = Field(ge=0)
    PPE: float = Field(ge=0)


DISEASE_PAYLOAD_MODELS = {
    "diabetes": DiabetesPayload,
    "heart": HeartPayload,
    "liver": LiverPayload,
    "parkinsons": ParkinsonsPayload,
}


# API Response Models
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "3.0.0"
    features: list[str] = Field(default_factory=list)


class PredictionMetrics(BaseModel):
    accuracy: float
    f1: float
    roc_auc: float


class ShapExplanation(BaseModel):
    base_value: float
    prediction: float
    feature_contributions: dict[str, float]
    top_positive: list[str]
    top_negative: list[str]


class PredictionResponse(BaseModel):
    disease: str
    predicted_positive: int
    probability: float
    risk_band: str
    threshold: float
    benchmarks: list[str]
    metrics: PredictionMetrics
    features: dict
    shap_explanation: ShapExplanation | None = None
    feature_importance: dict[str, float] | None = None


class BatchSummary(BaseModel):
    total_rows: int
    high_risk: int
    moderate_risk: int
    low_risk: int
    positive_predictions: int


class BatchResponse(BaseModel):
    disease: str
    summary: BatchSummary
    preview: list[dict]


class DiseaseSpec(BaseModel):
    title: str
    description: str
    tagline: str
    accent: str
    features_count: int


class DiseaseListResponse(BaseModel):
    diseases: dict[str, DiseaseSpec]


class AnalyticsTrendResponse(BaseModel):
    labels: list[str]
    datasets: list[dict]


class AnalyticsDistributionResponse(BaseModel):
    labels: list[str]
    data: list[int]
    colors: list[str]


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: str
    total_assessments: int
    total_uploads: int

