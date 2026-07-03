from typing import Optional

from pydantic import BaseModel

from app.status import ApplicationStatus


class CandidateProfileRead(BaseModel):
    id: int
    name: str
    target_titles: str
    experience_areas: str
    languages: str
    constraints: str


class VacancyRead(BaseModel):
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
    external_id: str
    source: str = "Manual"
    company: str
    title: str
    location: str = ""
    language: str = ""
    source_url: str = ""
    description: str = ""


class StatusUpdate(BaseModel):
    status: ApplicationStatus
    actor: str = "user"


class ApplicationMaterialRead(BaseModel):
    vacancy_id: int
    short_note: str
    recruiter_dm: str
    email_cover_letter: str
    fit_summary: str
