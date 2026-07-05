from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, Enum as SQLAlchemyEnum
from sqlmodel import Field, SQLModel

from app.status import ApplicationStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CandidateProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = "Aleksandr Grenkov"
    raw_cv_text: str = ""
    target_titles: str = ""
    experience_areas: str = ""
    languages: str = "Russian native; English B2"
    constraints: str = "Do not inflate language level, metrics, titles, or submission status."
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Vacancy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True)
    rank: Optional[int] = None
    source: str = ""
    company: str = ""
    title: str = ""
    location: str = ""
    posted: str = ""
    date_status: str = ""
    language: str = ""
    fit_score: int = 0
    priority: str = "Medium"
    submit_status: ApplicationStatus = Field(
        default=ApplicationStatus.DRAFT,
        sa_column=Column(
            SQLAlchemyEnum(
                ApplicationStatus,
                values_callable=lambda enum_class: [status.value for status in enum_class],
                native_enum=False,
                validate_strings=True,
                create_constraint=True,
                name="application_status",
            ),
            nullable=False,
        ),
    )
    next_action: str = ""
    cv_file_path: str = ""
    pdf_file_path: str = ""
    png_preview_path: str = ""
    source_url: str = ""
    description_raw: str = ""
    requirements: str = ""
    responsibilities: str = ""
    vacancy_keywords: str = ""
    tailored_headline: str = ""
    top_match_keywords: str = ""
    gaps_risks: str = ""
    adaptation_strategy: str = ""
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ApplicationMaterial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vacancy_id: int = Field(foreign_key="vacancy.id", index=True)
    short_note: str = ""
    recruiter_dm: str = ""
    email_cover_letter: str = ""
    fit_summary: str = ""
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class StatusEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    vacancy_id: int = Field(foreign_key="vacancy.id", index=True)
    previous_status: str
    new_status: str
    actor: str
    created_at: datetime = Field(default_factory=utcnow)
