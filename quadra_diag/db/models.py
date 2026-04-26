from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="patient", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    predictions: Mapped[list["PredictionRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    uploads: Mapped[list["UploadReport"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease: Mapped[str] = mapped_column(String(50), index=True)
    predicted_positive: Mapped[int] = mapped_column(Integer)
    probability: Mapped[float] = mapped_column(Float)
    risk_band: Mapped[str] = mapped_column(String(20))
    submitted_features: Mapped[dict] = mapped_column(JSON)
    shap_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    feature_importance: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[User | None] = relationship(back_populates="predictions")


class UploadReport(Base):
    __tablename__ = "upload_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease: Mapped[str] = mapped_column(String(50), index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)
    total_rows: Mapped[int] = mapped_column(Integer)
    positive_predictions: Mapped[int] = mapped_column(Integer)
    high_risk: Mapped[int] = mapped_column(Integer)
    moderate_risk: Mapped[int] = mapped_column(Integer)
    low_risk: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[User | None] = relationship(back_populates="uploads")


class ModelPerformance(Base):
    __tablename__ = "model_performances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease: Mapped[str] = mapped_column(String(50), index=True)
    accuracy: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)
    roc_auc: Mapped[float] = mapped_column(Float)
    training_samples: Mapped[int] = mapped_column(Integer)
    prediction_drift: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String(1000))
    level: Mapped[str] = mapped_column(String(20), default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    user: Mapped[User] = relationship(back_populates="notifications")

