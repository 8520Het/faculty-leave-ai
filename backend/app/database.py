from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from paths import DB_PATH, DATA_DIR


class Base(DeclarativeBase):
    pass


class LeaveForm(Base):
    __tablename__ = "leave_forms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_path: Mapped[str] = mapped_column(Text)
    applicant_name: Mapped[str] = mapped_column(String(255), default="Unknown")
    year: Mapped[int] = mapped_column(Integer, default=2026)
    status: Mapped[str] = mapped_column(String(40), default="UPLOADED")
    detection_strategy: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    assignments: Mapped[list["AssignmentRow"]] = relationship(
        back_populates="form",
        cascade="all, delete-orphan",
        order_by="AssignmentRow.row_number",
    )
    emails: Mapped[list["EmailPreview"]] = relationship(
        back_populates="form",
        cascade="all, delete-orphan",
    )


class AssignmentRow(Base):
    __tablename__ = "assignment_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("leave_forms.id"))
    row_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), default="MANUAL_REVIEW_REQUIRED")
    image_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ink_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    requires_review: Mapped[bool] = mapped_column(Boolean, default=True)
    reviewed: Mapped[bool] = mapped_column(Boolean, default=False)

    form: Mapped[LeaveForm] = relationship(back_populates="assignments")


class EmailPreview(Base):
    __tablename__ = "email_previews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id: Mapped[str] = mapped_column(ForeignKey("leave_forms.id"))
    to_email: Mapped[str] = mapped_column(String(255))
    substitute_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assignment_count: Mapped[int] = mapped_column(Integer, default=0)
    subject: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    form: Mapped[LeaveForm] = relationship(back_populates="emails")


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    level: Mapped[str] = mapped_column(String(20), default="INFO")
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
