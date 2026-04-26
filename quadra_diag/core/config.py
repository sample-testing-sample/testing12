from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "QuadraDiag"
    app_env: str = "development"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./runtime/quadra_diag.db"
    model_dir: Path = Field(default=BASE_DIR / "models")
    dataset_dir: Path = Field(default=BASE_DIR / "Dataset")
    media_dir: Path = Field(default=BASE_DIR / "static")
    runtime_dir: Path = Field(default=BASE_DIR / "runtime")
    model_auto_train: bool = True
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default=["*"])
    max_upload_size_mb: int = Field(default=10)
    max_batch_rows: int = Field(default=10000)
    metrics_cache_ttl: float = Field(default=60.0)
    enable_shap: bool = Field(default=True)
    enable_pdf_export: bool = Field(default=True)
    enable_excel_export: bool = Field(default=True)
    admin_email: str = Field(default="admin@quadradiag.local")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def template_dir(self) -> Path:
        return BASE_DIR / "quadra_diag" / "web" / "templates"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "quadra_diag" / "web" / "static"

    @property
    def report_dir(self) -> Path:
        return self.runtime_dir / "reports"

    @property
    def pdf_dir(self) -> Path:
        return self.runtime_dir / "pdfs"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

