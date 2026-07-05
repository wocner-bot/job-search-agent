from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import Session, select

from app.config import get_settings
from app.database import get_session
from app.models import ApplicationMaterial, CandidateProfile, StatusEvent, Vacancy
from app.schemas import StatusUpdate, VacancyCreate
from app.services.cv_parser import extract_profile_from_text, read_cv_text
from app.services.cv_writer import build_master_cv_document, build_tailored_cv_document
from app.services.exporter import export_zip_package
from app.services.importer import import_csv_rows, import_xlsx_sheet, normalize_queue_row
from app.services.materials import generate_materials
from app.services.recruiter import generate_role_recommendations
from app.services.scoring import score_vacancy
from app.services.vacancy_analysis import extract_vacancy_keywords, infer_vacancy_language
from app.status import assert_status_change_allowed

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "job-search-agent"}


@router.post("/candidate/text")
def create_candidate_from_text(payload: dict[str, str], session: Session = Depends(get_session)) -> CandidateProfile:
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="CV text is required")
    profile = extract_profile_from_text(text)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.post("/candidate/upload")
async def upload_candidate_cv(file: UploadFile = File(...), session: Session = Depends(get_session)) -> CandidateProfile:
    settings = get_settings()
    upload_dir = settings.storage_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename or "uploaded-cv.txt").name
    path = upload_dir / filename
    path.write_bytes(await file.read())
    try:
        text = read_cv_text(path)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    profile = extract_profile_from_text(text)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.get("/vacancies")
def list_vacancies(session: Session = Depends(get_session)) -> list[Vacancy]:
    return list(session.exec(select(Vacancy).order_by(Vacancy.rank, Vacancy.id)).all())


@router.post("/vacancies")
def create_vacancy(payload: VacancyCreate, session: Session = Depends(get_session)) -> Vacancy:
    vacancy_keywords = extract_vacancy_keywords(
        payload.title,
        payload.description_raw,
        payload.requirements,
        payload.responsibilities,
    )
    vacancy = Vacancy(
        external_id=payload.external_id,
        source=payload.source,
        company=payload.company,
        title=payload.title,
        location=payload.location,
        language=payload.language or infer_vacancy_language(
            " ".join([payload.title, payload.description_raw, payload.requirements, payload.responsibilities])
        ),
        source_url=payload.source_url,
        description_raw=payload.description_raw,
        requirements=payload.requirements,
        responsibilities=payload.responsibilities,
        vacancy_keywords=vacancy_keywords,
        top_match_keywords=vacancy_keywords,
    )
    session.add(vacancy)
    session.commit()
    session.refresh(vacancy)
    return vacancy


@router.patch("/vacancies/{vacancy_id}/status")
def update_status(vacancy_id: int, payload: StatusUpdate, session: Session = Depends(get_session)) -> Vacancy:
    vacancy = session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    actor = "user"
    try:
        assert_status_change_allowed(vacancy.submit_status, payload.status, actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    previous = vacancy.submit_status
    vacancy.submit_status = payload.status
    session.add(vacancy)
    session.add(
        StatusEvent(
            vacancy_id=vacancy.id,
            previous_status=previous.value,
            new_status=payload.status.value,
            actor=actor,
        )
    )
    session.commit()
    session.refresh(vacancy)
    return vacancy


@router.post("/imports/current-package")
def import_current_package(session: Session = Depends(get_session)) -> dict[str, int]:
    workbook = Path("../tailored_cv_package_with_PROJECT_MD/tailored_cv_package/application_queue_with_tailored_cv_links.xlsx")
    package_root = workbook.parent
    if not workbook.exists():
        raise HTTPException(status_code=404, detail="Current package workbook not found")
    rows = import_xlsx_sheet(workbook, "Application Queue")
    count = 0
    for row in rows:
        vacancy = normalize_queue_row(row, package_root)
        session.add(vacancy)
        count += 1
    session.commit()
    return {"imported": count}


@router.post("/imports/vacancies/upload")
async def import_uploaded_vacancies(file: UploadFile = File(...), session: Session = Depends(get_session)) -> dict[str, int]:
    settings = get_settings()
    upload_dir = settings.storage_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename or "vacancies.csv").name
    path = upload_dir / filename
    path.write_bytes(await file.read())

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            rows = import_csv_rows(path)
        elif suffix == ".xlsx":
            rows = import_xlsx_sheet(path, "Application Queue")
        else:
            raise ValueError("Unsupported vacancy file type. Use .csv or .xlsx.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not rows:
        raise HTTPException(status_code=400, detail="Vacancy file does not contain any rows.")

    count = 0
    for row in rows:
        session.add(normalize_queue_row(row, path.parent))
        count += 1
    session.commit()
    return {"imported": count}


@router.post("/analysis/run")
def run_analysis(session: Session = Depends(get_session)) -> dict[str, int]:
    profile = session.exec(select(CandidateProfile).order_by(CandidateProfile.id.desc())).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create a candidate profile first")
    vacancies = list(session.exec(select(Vacancy)).all())
    for vacancy in vacancies:
        result = score_vacancy(profile, vacancy)
        vacancy.fit_score = result.fit_score
        vacancy.priority = result.priority
        vacancy.top_match_keywords = result.matched_keywords
        vacancy.gaps_risks = result.gaps_risks
        vacancy.adaptation_strategy = result.adaptation_strategy
        if vacancy.id:
            vacancy.cv_file_path = f"/api/vacancies/{vacancy.id}/tailored-cv.docx"
        session.add(vacancy)
        material = generate_materials(profile, vacancy)
        session.add(material)
    session.commit()
    return {"analyzed": len(vacancies)}


@router.post("/analysis/from-cv")
def generate_analysis_from_cv(session: Session = Depends(get_session)) -> dict[str, int]:
    profile = session.exec(select(CandidateProfile).order_by(CandidateProfile.id.desc())).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create a candidate profile first")

    for material in session.exec(select(ApplicationMaterial)).all():
        session.delete(material)
    for event in session.exec(select(StatusEvent)).all():
        session.delete(event)
    for vacancy in session.exec(select(Vacancy)).all():
        session.delete(vacancy)
    session.commit()

    vacancies = generate_role_recommendations(profile)
    for vacancy in vacancies:
        session.add(vacancy)
    session.commit()

    for vacancy in session.exec(select(Vacancy).order_by(Vacancy.rank)).all():
        vacancy.cv_file_path = f"/api/vacancies/{vacancy.id}/tailored-cv.docx"
        session.add(vacancy)
        session.add(generate_materials(profile, vacancy))
    session.commit()
    return {"generated": len(vacancies), "analyzed": len(vacancies)}


@router.get("/candidate/master-cv.docx")
def download_master_cv(session: Session = Depends(get_session)) -> StreamingResponse:
    profile = session.exec(select(CandidateProfile).order_by(CandidateProfile.id.desc())).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create a candidate profile first")
    document = build_master_cv_document(profile)
    return StreamingResponse(
        document,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="master_cv_template.docx"'},
    )


@router.get("/vacancies/{vacancy_id}/tailored-cv.docx")
def download_tailored_cv(vacancy_id: int, session: Session = Depends(get_session)) -> StreamingResponse:
    profile = session.exec(select(CandidateProfile).order_by(CandidateProfile.id.desc())).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Create a candidate profile first")
    vacancy = session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    document = build_tailored_cv_document(profile, vacancy)
    filename = f"{vacancy.external_id}_{vacancy.title}".replace("/", "-").replace(" ", "_")
    return StreamingResponse(
        document,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}.docx"'},
    )


@router.get("/materials")
def list_materials(session: Session = Depends(get_session)) -> list[ApplicationMaterial]:
    return list(session.exec(select(ApplicationMaterial)).all())


def _export_zip_response(session: Session) -> FileResponse:
    settings = get_settings()
    vacancies = list(session.exec(select(Vacancy).order_by(Vacancy.rank, Vacancy.id)).all())
    materials = list(session.exec(select(ApplicationMaterial)).all())
    output = export_zip_package(settings.storage_dir / "exports", vacancies, materials)
    return FileResponse(output, filename=output.name)


@router.get("/exports/zip")
def export_zip_get(session: Session = Depends(get_session)) -> FileResponse:
    return _export_zip_response(session)


@router.post("/exports/zip")
def export_zip_post(session: Session = Depends(get_session)) -> FileResponse:
    return _export_zip_response(session)
