from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.status import ApplicationStatus


class CandidateProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_titles: str
    experience_areas: str
    languages: str
    constraints: str


class VacancyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    rank: Optional[int]
    source: str
    company: str
    title: str
    location: str
    posted: str
    date_status: str
    language: str
    fit_score: int
    priority: str
    submit_status: ApplicationStatus
    next_action: str
    cv_file_path: str
    pdf_file_path: str
    png_preview_path: str
    source_url: str
    tailored_headline: str
    top_match_keywords: str
    gaps_risks: str
    adaptation_strategy: str


class VacancyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_id: str = ""
    source: str = "Manual"
    company: str = ""
    title: str = ""
    location: str = ""
    language: str = ""
    source_url: str = ""
    description_raw: str = ""
    requirements: str = ""
    responsibilities: str = ""


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ApplicationStatus


class ApplicationMaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vacancy_id: int
    short_note: str
    recruiter_dm: str
    email_cover_letter: str
    fit_summary: str
