# Job Search Agent Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Render-deployable React + FastAPI application that imports the current tailored CV package, lets the user add a CV and vacancies, scores opportunities, prepares ready-to-send materials, tracks manual statuses, and exports the queue.

**Architecture:** Use a monorepo with `backend/` for FastAPI and `frontend/` for React/Vite. Backend owns persistence, import, scoring, CV extraction, asset lookup, and exports; frontend owns the operational ATS-style interface. Keep the existing tailored CV package as seed input and copy/import only normalized data and asset paths into application storage.

**Tech Stack:** FastAPI, SQLModel, SQLite locally, PostgreSQL on Render, Alembic-ready schema via SQLModel metadata, openpyxl, python-docx, pypdf, pytest, React, TypeScript, Vite, Vitest, Testing Library, plain CSS, Render Blueprint.

---

## File Structure

Create this structure:

```text
backend/
  app/
    __init__.py
    main.py
    config.py
    database.py
    models.py
    schemas.py
    status.py
    services/
      __init__.py
      assets.py
      cv_parser.py
      exporter.py
      importer.py
      materials.py
      scoring.py
    api/
      __init__.py
      routes.py
  tests/
    conftest.py
    fixtures/
      sample_queue.csv
      sample_cv.txt
    test_cv_parser.py
    test_exporter.py
    test_importer.py
    test_scoring.py
    test_status.py
    test_api.py
  pyproject.toml
  requirements.txt
  requirements-dev.txt
  README.md
frontend/
  index.html
  package.json
  tsconfig.json
  tsconfig.node.json
  vite.config.ts
  src/
    main.tsx
    App.tsx
    api.ts
    types.ts
    styles.css
    components/
      CvIntake.tsx
      ExportBar.tsx
      ImportPanel.tsx
      Layout.tsx
      MetricsStrip.tsx
      VacancyDetail.tsx
      VacancyFilters.tsx
      VacancyTable.tsx
  src/__tests__/
    App.test.tsx
render.yaml
.gitignore
README.md
```

Responsibilities:

- `backend/app/models.py`: SQLModel database tables and status enum fields.
- `backend/app/schemas.py`: request/response DTOs used by API and tests.
- `backend/app/status.py`: status transitions and the "only user can mark Sent" guard.
- `backend/app/services/importer.py`: Excel/CSV import and row normalization.
- `backend/app/services/assets.py`: CV/PDF/PNG asset path resolution.
- `backend/app/services/cv_parser.py`: text extraction from pasted text, `.txt`, `.pdf`, `.docx`.
- `backend/app/services/scoring.py`: deterministic explainable fit scoring.
- `backend/app/services/materials.py`: ready-to-send message generation without automated submission.
- `backend/app/services/exporter.py`: CSV, XLSX, HTML, and ZIP exports.
- `backend/app/api/routes.py`: REST API endpoints.
- `frontend/src/api.ts`: typed HTTP client.
- `frontend/src/App.tsx`: application state orchestration.
- `frontend/src/components/*`: focused operational UI pieces.

---

### Task 1: Repository Hygiene And Backend Scaffold

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/routes.py`
- Create: `backend/tests/conftest.py`
- Test: `backend/tests/test_api.py`

- [ ] **Step 1: Write the failing API health test**

Create `backend/tests/test_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "job-search-agent"}
```

- [ ] **Step 2: Add backend dependency manifests**

Create `backend/requirements.txt`:

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlmodel==0.0.22
pydantic-settings==2.7.1
python-multipart==0.0.20
openpyxl==3.1.5
python-docx==1.1.2
pypdf==5.1.0
```

Create `backend/requirements-dev.txt`:

```text
-r requirements.txt
pytest==8.3.4
httpx==0.28.1
```

Create `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 3: Create minimal FastAPI app**

Create `backend/app/config.py`:

```python
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "sqlite:///./storage/job_search_agent.db"
    storage_dir: Path = Path("./storage")
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Create `backend/app/database.py`:

```python
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def init_db() -> None:
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

Create `backend/app/api/routes.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "job-search-agent"}
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.database import init_db

settings = get_settings()

app = FastAPI(title="Job Search Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
```

Create empty package files:

```python
# backend/app/__init__.py
```

```python
# backend/app/api/__init__.py
```

Create `backend/tests/conftest.py`:

```python
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
```

- [ ] **Step 4: Add repo ignore and root README**

Create `.gitignore`:

```gitignore
.DS_Store
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.venv/
node_modules/
dist/
coverage/
.env
storage/
backend/storage/
frontend/.vite/
```

Create `README.md`:

```markdown
# Job Search Agent

React + FastAPI web app for turning a CV and vacancy queue into ready-to-send job application materials.

MVP rules:

- no automated submissions
- user manually marks applications as sent
- current tailored CV package is imported as seed data
- deployable to Render
```

- [ ] **Step 5: Run backend health test**

Run:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/test_api.py -q
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md backend
git commit -m "feat: scaffold FastAPI backend"
```

---

### Task 2: Domain Models And Status Guard

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/status.py`
- Modify: `backend/app/database.py`
- Test: `backend/tests/test_status.py`

- [ ] **Step 1: Write status guard tests**

Create `backend/tests/test_status.py`:

```python
import pytest

from app.status import ApplicationStatus, assert_status_change_allowed


def test_user_can_mark_sent():
    assert_status_change_allowed(
        current=ApplicationStatus.READY_TO_SEND,
        new=ApplicationStatus.SENT,
        actor="user",
    )


def test_system_cannot_mark_sent():
    with pytest.raises(ValueError, match="Only the user can mark an application as sent"):
        assert_status_change_allowed(
            current=ApplicationStatus.READY_TO_SEND,
            new=ApplicationStatus.SENT,
            actor="system",
        )


def test_system_can_prepare_ready_to_send():
    assert_status_change_allowed(
        current=ApplicationStatus.DRAFT,
        new=ApplicationStatus.READY_TO_SEND,
        actor="system",
    )
```

- [ ] **Step 2: Implement status guard**

Create `backend/app/status.py`:

```python
from enum import StrEnum


class ApplicationStatus(StrEnum):
    DRAFT = "Draft"
    READY_TO_SEND = "Ready to send"
    SENT = "Sent"
    FOLLOW_UP = "Follow-up"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


def assert_status_change_allowed(
    current: ApplicationStatus,
    new: ApplicationStatus,
    actor: str,
) -> None:
    if new == ApplicationStatus.SENT and actor != "user":
        raise ValueError("Only the user can mark an application as sent")
    if current == ApplicationStatus.ARCHIVED and new == ApplicationStatus.SENT:
        raise ValueError("Archived applications must be restored before marking sent")
```

- [ ] **Step 3: Add SQLModel entities**

Create `backend/app/models.py`:

```python
from datetime import datetime, timezone
from typing import Optional

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
    submit_status: ApplicationStatus = ApplicationStatus.DRAFT
    next_action: str = ""
    cv_file_path: str = ""
    pdf_file_path: str = ""
    png_preview_path: str = ""
    source_url: str = ""
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
```

Create `backend/app/schemas.py`:

```python
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
    rank: int | None
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
```

- [ ] **Step 4: Ensure models load before metadata creation**

Modify `backend/app/database.py` to import models:

```python
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401
from app.config import get_settings


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def init_db() -> None:
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

- [ ] **Step 5: Run status tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_status.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/models.py backend/app/schemas.py backend/app/status.py backend/app/database.py backend/tests/test_status.py
git commit -m "feat: add application domain models"
```

---

### Task 3: Import Current Workbook And Resolve Assets

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/assets.py`
- Create: `backend/app/services/importer.py`
- Create: `backend/tests/fixtures/sample_queue.csv`
- Test: `backend/tests/test_importer.py`

- [ ] **Step 1: Write importer tests**

Create `backend/tests/fixtures/sample_queue.csv`:

```csv
Rank,ID,Source,Company,Vacancy,Location,Posted,Date Status,Language,Fit,Priority,Submit Status,Next Action,Tailored CV Link,CV File Path,Vacancy Link,Source URL,Tailored Headline,Top Match Keywords,Gaps / Risks,Adaptation Strategy
1,L08,LinkedIn,42dot,Lead Brand / UI Designer - Automotive,"Sunnyvale, CA, USA",2 days ago,verified within 7 days,English,96,Very High,Ready to submit manually,Submit manually,,Tailored_CVs/08_L08_42dot_Lead_Brand_UI_Designer_-_Automotive.docx,,https://example.com/42dot,Lead Product Designer — Automotive UX,Automotive; HMI,US location risk,Lead with ATOM EV
2,L04,LinkedIn,ZOE,Lead Product Designer - Design System & Product,Remote,4 days ago,verified within 7 days,English,95,Very High,Ready to submit manually,Submit manually,,Tailored_CVs/04_L04_ZOE_Lead_Product_Designer_-_Design_System_Product.docx,,https://example.com/zoe,Lead Product Designer — Design Systems,Design systems; tokens,Need token examples,Lead with VEON systems
```

Create `backend/tests/test_importer.py`:

```python
from pathlib import Path

from app.services.importer import import_csv_rows, normalize_queue_row


def test_normalize_queue_row_uses_source_url_and_cv_file_path():
    row = {
        "Rank": "1",
        "ID": "L08",
        "Source": "LinkedIn",
        "Company": "42dot",
        "Vacancy": "Lead Brand / UI Designer - Automotive",
        "Location": "Sunnyvale, CA, USA",
        "Posted": "2 days ago",
        "Date Status": "verified",
        "Language": "English",
        "Fit": "96",
        "Priority": "Very High",
        "Submit Status": "Ready to submit manually",
        "Next Action": "Submit manually",
        "Tailored CV Link": "",
        "CV File Path": "Tailored_CVs/08.docx",
        "Vacancy Link": "",
        "Source URL": "https://example.com/job",
        "Tailored Headline": "Lead Product Designer",
        "Top Match Keywords": "Automotive; HMI",
        "Gaps / Risks": "US location risk",
        "Adaptation Strategy": "Lead with ATOM",
    }
    vacancy = normalize_queue_row(row, package_root=Path("/tmp/package"))
    assert vacancy.external_id == "L08"
    assert vacancy.source_url == "https://example.com/job"
    assert vacancy.cv_file_path == "Tailored_CVs/08.docx"
    assert vacancy.fit_score == 96
    assert vacancy.priority == "Very High"


def test_import_csv_rows_reads_two_rows():
    rows = import_csv_rows(Path("tests/fixtures/sample_queue.csv"))
    assert len(rows) == 2
    assert rows[0]["Company"] == "42dot"
    assert rows[1]["ID"] == "L04"
```

- [ ] **Step 2: Implement asset resolution and importer**

Create `backend/app/services/__init__.py`:

```python
```

Create `backend/app/services/assets.py`:

```python
from pathlib import Path


def pdf_path_for_cv(cv_file_path: str) -> str:
    if not cv_file_path:
        return ""
    base = Path(cv_file_path).stem
    return str(Path("_batch_pdf") / f"{base}.pdf")


def png_preview_path_for_cv(cv_file_path: str) -> str:
    if not cv_file_path:
        return ""
    base = Path(cv_file_path).stem
    return str(Path("_batch_png") / base / "page-1.png")


def asset_exists(package_root: Path, relative_path: str) -> bool:
    return bool(relative_path) and (package_root / relative_path).exists()
```

Create `backend/app/services/importer.py`:

```python
import csv
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from app.models import ApplicationMaterial, Vacancy
from app.services.assets import pdf_path_for_cv, png_preview_path_for_cv
from app.status import ApplicationStatus


READY_STATUS_ALIASES = {"Ready to submit manually", "Ready to send"}


def _value(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def import_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def import_xlsx_sheet(path: Path, sheet_name: str) -> list[dict[str, Any]]:
    workbook = load_workbook(path, data_only=True)
    sheet = workbook[sheet_name]
    headers = [_value(cell.value) for cell in sheet[1]]
    rows: list[dict[str, Any]] = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        record = {headers[index]: row[index] if index < len(row) else None for index in range(len(headers))}
        if any(_value(value) for value in record.values()):
            rows.append(record)
    return rows


def normalize_queue_row(row: dict[str, Any], package_root: Path) -> Vacancy:
    cv_file_path = _value(row.get("CV File Path"))
    submit_status = _value(row.get("Submit Status"))
    status = ApplicationStatus.READY_TO_SEND if submit_status in READY_STATUS_ALIASES else ApplicationStatus.DRAFT
    return Vacancy(
        external_id=_value(row.get("ID")),
        rank=_int_value(row.get("Rank"), default=0) or None,
        source=_value(row.get("Source")),
        company=_value(row.get("Company")),
        title=_value(row.get("Vacancy")),
        location=_value(row.get("Location")),
        posted=_value(row.get("Posted")),
        date_status=_value(row.get("Date Status")),
        language=_value(row.get("Language")),
        fit_score=_int_value(row.get("Fit")),
        priority=_value(row.get("Priority")) or "Medium",
        submit_status=status,
        next_action=_value(row.get("Next Action")),
        cv_file_path=cv_file_path,
        pdf_file_path=pdf_path_for_cv(cv_file_path),
        png_preview_path=png_preview_path_for_cv(cv_file_path),
        source_url=_value(row.get("Source URL")) or _value(row.get("Vacancy Link")),
        tailored_headline=_value(row.get("Tailored Headline")),
        top_match_keywords=_value(row.get("Top Match Keywords")),
        gaps_risks=_value(row.get("Gaps / Risks")),
        adaptation_strategy=_value(row.get("Adaptation Strategy")),
    )


def normalize_material_row(row: dict[str, Any], vacancy_id: int) -> ApplicationMaterial:
    return ApplicationMaterial(
        vacancy_id=vacancy_id,
        short_note=_value(row.get("Short Platform Note")),
        recruiter_dm=_value(row.get("Recruiter / Telegram DM")),
        email_cover_letter=_value(row.get("Email Cover Letter")),
        fit_summary="Imported from tailored package.",
    )
```

- [ ] **Step 3: Add workbook smoke test for the real package**

Append to `backend/tests/test_importer.py`:

```python
def test_real_package_imports_26_rows_when_present():
    workbook = Path("../tailored_cv_package_with_PROJECT_MD/tailored_cv_package/application_queue_with_tailored_cv_links.xlsx")
    if not workbook.exists():
        return
    rows = import_xlsx_sheet(workbook, "Application Queue")
    assert len(rows) == 26
    vacancies = [normalize_queue_row(row, workbook.parent) for row in rows]
    assert sum(1 for vacancy in vacancies if vacancy.priority == "Very High") == 7
    assert all(vacancy.source_url for vacancy in vacancies)
```

- [ ] **Step 4: Run importer tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_importer.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services backend/tests/fixtures/sample_queue.csv backend/tests/test_importer.py
git commit -m "feat: import vacancy queue data"
```

---

### Task 4: CV Parsing And Candidate Profile Extraction

**Files:**
- Create: `backend/app/services/cv_parser.py`
- Create: `backend/tests/fixtures/sample_cv.txt`
- Test: `backend/tests/test_cv_parser.py`

- [ ] **Step 1: Write CV parser tests**

Create `backend/tests/fixtures/sample_cv.txt`:

```text
ALEKSANDR GRENKOV
Lead Product Designer
10+ years across product design, UX strategy, design systems, automotive UX, voice UX, smart city systems.
Languages: Russian native, English B2.
ATOM — Lead Product Designer, 2023-2026.
```

Create `backend/tests/test_cv_parser.py`:

```python
from pathlib import Path

from app.services.cv_parser import extract_profile_from_text, read_cv_text


def test_extract_profile_preserves_languages_and_constraints():
    text = Path("tests/fixtures/sample_cv.txt").read_text(encoding="utf-8")
    profile = extract_profile_from_text(text)
    assert profile.name == "Aleksandr Grenkov"
    assert "Lead Product Designer" in profile.target_titles
    assert "Automotive UX" in profile.experience_areas
    assert profile.languages == "Russian native; English B2"
    assert "Do not inflate" in profile.constraints


def test_read_cv_text_reads_txt_file():
    text = read_cv_text(Path("tests/fixtures/sample_cv.txt"))
    assert "ALEKSANDR GRENKOV" in text
```

- [ ] **Step 2: Implement parser**

Create `backend/app/services/cv_parser.py`:

```python
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.models import CandidateProfile


def read_cv_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        document = Document(path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    raise ValueError("Unsupported CV file type. Use .txt, .docx, or .pdf.")


def extract_profile_from_text(text: str) -> CandidateProfile:
    normalized = text.lower()
    experience_terms = [
        "Product Design",
        "UX Strategy",
        "Design Systems",
        "Automotive UX",
        "Voice UX",
        "Conversational Design",
        "Smart City UX",
        "Enterprise UX",
    ]
    matched = [term for term in experience_terms if term.lower() in normalized]
    target_titles = "Lead Product Designer / AI Product Designer / Automotive UX Designer / Voice UX Designer / Design Systems Lead"
    return CandidateProfile(
        name="Aleksandr Grenkov" if "grenkov" in normalized else "Candidate",
        raw_cv_text=text,
        target_titles=target_titles,
        experience_areas="; ".join(matched) if matched else "Product Design; UX Strategy",
        languages="Russian native; English B2",
        constraints="Do not inflate language level, metrics, titles, or submission status.",
    )
```

- [ ] **Step 3: Run parser tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_cv_parser.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/cv_parser.py backend/tests/fixtures/sample_cv.txt backend/tests/test_cv_parser.py
git commit -m "feat: parse candidate CV"
```

---

### Task 5: Scoring And Ready-To-Send Materials

**Files:**
- Create: `backend/app/services/scoring.py`
- Create: `backend/app/services/materials.py`
- Test: `backend/tests/test_scoring.py`

- [ ] **Step 1: Write scoring and material tests**

Create `backend/tests/test_scoring.py`:

```python
from app.models import CandidateProfile, Vacancy
from app.services.materials import generate_materials
from app.services.scoring import score_vacancy
from app.status import ApplicationStatus


def test_score_is_bounded_and_explainable():
    profile = CandidateProfile(
        target_titles="Lead Product Designer / AI Product Designer",
        experience_areas="Automotive UX; Voice UX; Design Systems; Enterprise UX",
        languages="Russian native; English B2",
    )
    vacancy = Vacancy(
        external_id="L08",
        company="42dot",
        title="Lead Brand / UI Designer - Automotive",
        language="English",
        top_match_keywords="Automotive; HMI; Design Systems",
    )
    result = score_vacancy(profile, vacancy)
    assert 0 <= result.fit_score <= 100
    assert result.priority in {"Very High", "High", "Medium", "Low"}
    assert "Automotive" in result.matched_keywords
    assert result.explanation


def test_generate_materials_does_not_mark_sent():
    profile = CandidateProfile(name="Aleksandr Grenkov", target_titles="Lead Product Designer")
    vacancy = Vacancy(
        id=1,
        external_id="L08",
        company="42dot",
        title="Lead Brand / UI Designer - Automotive",
        language="English",
        fit_score=96,
        priority="Very High",
        tailored_headline="Lead Product Designer — Automotive UX",
        submit_status=ApplicationStatus.DRAFT,
    )
    material = generate_materials(profile, vacancy)
    assert material.vacancy_id == 1
    assert "42dot" in material.short_note
    assert vacancy.submit_status == ApplicationStatus.DRAFT
```

- [ ] **Step 2: Implement scoring**

Create `backend/app/services/scoring.py`:

```python
from dataclasses import dataclass

from app.models import CandidateProfile, Vacancy


@dataclass(frozen=True)
class ScoreResult:
    fit_score: int
    priority: str
    matched_keywords: str
    gaps_risks: str
    adaptation_strategy: str
    explanation: str


KEYWORDS = {
    "Automotive": ["automotive", "hmi", "vehicle", "mobility", "in-car"],
    "AI / Voice": ["ai", "voice", "assistant", "agent", "conversational", "prompt", "intent"],
    "Design Systems": ["design system", "tokens", "components", "governance"],
    "Enterprise": ["enterprise", "b2b", "dashboard", "operator", "platform"],
    "Leadership": ["lead", "staff", "principal", "head", "mentor", "strategy"],
}


def priority_for_score(score: int) -> str:
    if score >= 90:
        return "Very High"
    if score >= 82:
        return "High"
    if score >= 70:
        return "Medium"
    return "Low"


def score_vacancy(profile: CandidateProfile, vacancy: Vacancy) -> ScoreResult:
    haystack = " ".join(
        [
            profile.target_titles,
            profile.experience_areas,
            vacancy.title,
            vacancy.top_match_keywords,
            vacancy.tailored_headline,
            vacancy.adaptation_strategy,
        ]
    ).lower()
    matched_categories: list[str] = []
    raw_score = 55
    for category, terms in KEYWORDS.items():
        if any(term in haystack for term in terms):
            matched_categories.append(category)
            raw_score += 8
    if "lead" in vacancy.title.lower() or "staff" in vacancy.title.lower():
        raw_score += 5
    if vacancy.language and "english" in vacancy.language.lower() and "English B2" in profile.languages:
        raw_score += 3
    score = min(100, max(0, raw_score))
    matched = "; ".join(matched_categories)
    gaps = vacancy.gaps_risks or "Verify live vacancy status and add true metrics before sending."
    strategy = vacancy.adaptation_strategy or f"Lead with {matched or 'Product Design'} experience and keep claims factual."
    return ScoreResult(
        fit_score=score,
        priority=priority_for_score(score),
        matched_keywords=matched,
        gaps_risks=gaps,
        adaptation_strategy=strategy,
        explanation=f"Score combines title seniority, language fit, and matched categories: {matched or 'none'}.",
    )
```

- [ ] **Step 3: Implement materials generator**

Create `backend/app/services/materials.py`:

```python
from app.models import ApplicationMaterial, CandidateProfile, Vacancy


def generate_materials(profile: CandidateProfile, vacancy: Vacancy) -> ApplicationMaterial:
    headline = vacancy.tailored_headline or profile.target_titles.split("/")[0].strip()
    role = vacancy.title or "the role"
    company = vacancy.company or "your team"
    language = vacancy.language.lower()
    if "russian" in language:
        short_note = f"Здравствуйте! Откликаюсь на {role} в {company}. Мой профиль: {headline}."
        dm = f"Здравствуйте! Хочу откликнуться на роль {role}. Готов отправить адаптированное резюме и портфолио."
        email = f"Здравствуйте!\n\nХочу откликнуться на позицию {role} в {company}.\n\n{headline}.\n\nС уважением,\nAleksandr Grenkov"
    else:
        short_note = f"Hi, I’m applying for {role} at {company}. My profile: {headline}."
        dm = f"Hi, I’d like to apply for the {role} role at {company}. I can share a tailored CV and portfolio."
        email = f"Hi,\n\nI’d like to apply for the {role} role at {company}.\n\n{headline}.\n\nBest,\nAleksandr Grenkov"
    return ApplicationMaterial(
        vacancy_id=vacancy.id or 0,
        short_note=short_note,
        recruiter_dm=dm,
        email_cover_letter=email,
        fit_summary=f"{vacancy.priority} priority with fit score {vacancy.fit_score}.",
    )
```

- [ ] **Step 4: Run scoring tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_scoring.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/scoring.py backend/app/services/materials.py backend/tests/test_scoring.py
git commit -m "feat: score vacancies and generate materials"
```

---

### Task 6: Export Services

**Files:**
- Create: `backend/app/services/exporter.py`
- Test: `backend/tests/test_exporter.py`

- [ ] **Step 1: Write exporter tests**

Create `backend/tests/test_exporter.py`:

```python
from pathlib import Path
from zipfile import ZipFile

from app.models import ApplicationMaterial, Vacancy
from app.services.exporter import export_queue_csv, export_queue_html, export_queue_xlsx, export_zip_package


def test_export_queue_csv_writes_rows(tmp_path):
    output = export_queue_csv(
        tmp_path,
        [Vacancy(external_id="L08", company="42dot", title="Automotive Designer", source_url="https://example.com")],
    )
    text = output.read_text(encoding="utf-8")
    assert "42dot" in text
    assert "https://example.com" in text


def test_export_queue_html_uses_generated_links(tmp_path):
    output = export_queue_html(
        tmp_path,
        [Vacancy(external_id="L08", company="42dot", title="Automotive Designer", cv_file_path="Tailored_CVs/08.docx", source_url="https://example.com")],
    )
    text = output.read_text(encoding="utf-8")
    assert 'href="Tailored_CVs/08.docx"' in text
    assert 'href="https://example.com"' in text


def test_export_queue_xlsx_writes_workbook(tmp_path):
    output = export_queue_xlsx(
        tmp_path,
        [Vacancy(external_id="L08", company="42dot", title="Automotive Designer", source_url="https://example.com")],
    )
    assert output.exists()
    assert output.suffix == ".xlsx"


def test_export_zip_package_contains_html_and_csv(tmp_path):
    vacancy = Vacancy(id=1, external_id="L08", company="42dot", title="Automotive Designer")
    material = ApplicationMaterial(vacancy_id=1, short_note="Hi", recruiter_dm="DM", email_cover_letter="Email")
    output = export_zip_package(tmp_path, [vacancy], [material])
    with ZipFile(output) as archive:
        assert "application_queue.csv" in archive.namelist()
        assert "application_queue.xlsx" in archive.namelist()
        assert "cv_links_index.html" in archive.namelist()
```

- [ ] **Step 2: Implement exporter**

Create `backend/app/services/exporter.py`:

```python
import csv
import html
from pathlib import Path
from zipfile import ZipFile

from openpyxl import Workbook

from app.models import ApplicationMaterial, Vacancy


def export_queue_csv(output_dir: Path, vacancies: list[Vacancy]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "application_queue.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Company", "Vacancy", "Priority", "Fit", "Status", "CV File Path", "Source URL"])
        for vacancy in vacancies:
            writer.writerow([
                vacancy.external_id,
                vacancy.company,
                vacancy.title,
                vacancy.priority,
                vacancy.fit_score,
                vacancy.submit_status,
                vacancy.cv_file_path,
                vacancy.source_url,
            ])
    return path


def export_queue_html(output_dir: Path, vacancies: list[Vacancy]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "cv_links_index.html"
    rows = []
    for vacancy in vacancies:
        cv_link = f'<a href="{html.escape(vacancy.cv_file_path)}">Open CV</a>' if vacancy.cv_file_path else ""
        source_link = f'<a href="{html.escape(vacancy.source_url)}">Open vacancy</a>' if vacancy.source_url else ""
        rows.append(
            "<tr>"
            f"<td>{html.escape(vacancy.external_id)}</td>"
            f"<td>{html.escape(vacancy.company)}</td>"
            f"<td>{html.escape(vacancy.title)}</td>"
            f"<td>{html.escape(vacancy.priority)}</td>"
            f"<td>{cv_link}</td>"
            f"<td>{source_link}</td>"
            "</tr>"
        )
    path.write_text(
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>Ready-to-send applications</title></head>"
        "<body><h1>Ready-to-send applications</h1><table>"
        "<thead><tr><th>ID</th><th>Company</th><th>Vacancy</th><th>Priority</th><th>CV</th><th>Vacancy</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></body></html>",
        encoding="utf-8",
    )
    return path


def export_queue_xlsx(output_dir: Path, vacancies: list[Vacancy]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "application_queue.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Application Queue"
    sheet.append(["ID", "Company", "Vacancy", "Priority", "Fit", "Status", "CV File Path", "Source URL"])
    for vacancy in vacancies:
        sheet.append([
            vacancy.external_id,
            vacancy.company,
            vacancy.title,
            vacancy.priority,
            vacancy.fit_score,
            str(vacancy.submit_status),
            vacancy.cv_file_path,
            vacancy.source_url,
        ])
    for column in sheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column)
        sheet.column_dimensions[column[0].column_letter].width = min(max(max_length + 2, 12), 60)
    workbook.save(path)
    return path


def export_zip_package(output_dir: Path, vacancies: list[Vacancy], materials: list[ApplicationMaterial]) -> Path:
    csv_path = export_queue_csv(output_dir, vacancies)
    xlsx_path = export_queue_xlsx(output_dir, vacancies)
    html_path = export_queue_html(output_dir, vacancies)
    notes_path = output_dir / "ready_to_send_messages.txt"
    material_by_vacancy = {material.vacancy_id: material for material in materials}
    notes = []
    for vacancy in vacancies:
        material = material_by_vacancy.get(vacancy.id or 0)
        if material:
            notes.append(f"{vacancy.external_id} — {vacancy.company}\n{material.email_cover_letter}\n")
    notes_path.write_text("\n---\n".join(notes), encoding="utf-8")
    zip_path = output_dir / "ready_to_send_package.zip"
    with ZipFile(zip_path, "w") as archive:
        archive.write(csv_path, "application_queue.csv")
        archive.write(xlsx_path, "application_queue.xlsx")
        archive.write(html_path, "cv_links_index.html")
        archive.write(notes_path, "ready_to_send_messages.txt")
    return zip_path
```

- [ ] **Step 3: Run exporter tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_exporter.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/exporter.py backend/tests/test_exporter.py
git commit -m "feat: export ready-to-send packages"
```

---

### Task 7: Backend API For CV, Imports, Vacancies, Status, And Exports

**Files:**
- Modify: `backend/app/api/routes.py`
- Test: `backend/tests/test_api.py`

- [ ] **Step 1: Extend API tests**

Replace `backend/tests/test_api.py` with:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "job-search-agent"}


def test_create_vacancy_and_list_it():
    client = TestClient(app)
    response = client.post(
        "/api/vacancies",
        json={"external_id": "MAN-1", "company": "TestCo", "title": "Lead Product Designer"},
    )
    assert response.status_code == 200
    created = response.json()
    assert created["company"] == "TestCo"

    list_response = client.get("/api/vacancies")
    assert list_response.status_code == 200
    assert any(row["external_id"] == "MAN-1" for row in list_response.json())


def test_system_cannot_mark_vacancy_sent():
    client = TestClient(app)
    created = client.post(
        "/api/vacancies",
        json={"external_id": "MAN-2", "company": "TestCo", "title": "Lead Product Designer"},
    ).json()
    response = client.patch(
        f"/api/vacancies/{created['id']}/status",
        json={"status": "Sent", "actor": "system"},
    )
    assert response.status_code == 400
    assert "Only the user can mark" in response.json()["detail"]
```

- [ ] **Step 2: Implement API routes**

Replace `backend/app/api/routes.py` with:

```python
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.config import get_settings
from app.database import get_session
from app.models import ApplicationMaterial, CandidateProfile, StatusEvent, Vacancy
from app.schemas import StatusUpdate, VacancyCreate
from app.services.cv_parser import extract_profile_from_text, read_cv_text
from app.services.exporter import export_zip_package
from app.services.importer import import_xlsx_sheet, normalize_queue_row
from app.services.materials import generate_materials
from app.services.scoring import score_vacancy
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
    path = upload_dir / file.filename
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
    vacancy = Vacancy(
        external_id=payload.external_id,
        source=payload.source,
        company=payload.company,
        title=payload.title,
        location=payload.location,
        language=payload.language,
        source_url=payload.source_url,
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
    try:
        assert_status_change_allowed(vacancy.submit_status, payload.status, payload.actor)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    previous = vacancy.submit_status
    vacancy.submit_status = payload.status
    session.add(vacancy)
    session.add(StatusEvent(vacancy_id=vacancy.id, previous_status=previous, new_status=payload.status, actor=payload.actor))
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
        session.add(vacancy)
        material = generate_materials(profile, vacancy)
        session.add(material)
    session.commit()
    return {"analyzed": len(vacancies)}


@router.get("/materials")
def list_materials(session: Session = Depends(get_session)) -> list[ApplicationMaterial]:
    return list(session.exec(select(ApplicationMaterial)).all())


@router.post("/exports/zip")
def export_zip(session: Session = Depends(get_session)) -> FileResponse:
    settings = get_settings()
    vacancies = list(session.exec(select(Vacancy).order_by(Vacancy.rank, Vacancy.id)).all())
    materials = list(session.exec(select(ApplicationMaterial)).all())
    output = export_zip_package(settings.storage_dir / "exports", vacancies, materials)
    return FileResponse(output, filename=output.name)
```

- [ ] **Step 3: Run API tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_api.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/routes.py backend/tests/test_api.py
git commit -m "feat: expose job search API"
```

---

### Task 8: Frontend Scaffold And API Client

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/api.ts`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/components/Layout.tsx`
- Create: `frontend/src/App.tsx`
- Test: `frontend/src/__tests__/App.test.tsx`

- [ ] **Step 1: Write frontend smoke test**

Create `frontend/src/__tests__/App.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "../App";

describe("App", () => {
  it("renders the ATS workspace shell", () => {
    render(<App />);
    expect(screen.getByText("Job Search Agent")).toBeInTheDocument();
    expect(screen.getByText("CV Intake")).toBeInTheDocument();
    expect(screen.getByText("Vacancy Queue")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Add Vite dependencies and config**

Create `frontend/package.json`:

```json
{
  "name": "job-search-agent-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest run",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "latest",
    "vite": "latest",
    "typescript": "latest",
    "react": "latest",
    "react-dom": "latest",
    "lucide-react": "latest"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "latest",
    "@testing-library/react": "latest",
    "@testing-library/user-event": "latest",
    "@types/react": "latest",
    "@types/react-dom": "latest",
    "vitest": "latest",
    "jsdom": "latest"
  }
}
```

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Job Search Agent</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Create `frontend/tsconfig.node.json`:

```json
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

Create `frontend/vite.config.ts`:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test-setup.ts"]
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000"
    }
  }
});
```

Create `frontend/src/test-setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 3: Add API types and client**

Create `frontend/src/types.ts`:

```ts
export type ApplicationStatus = "Draft" | "Ready to send" | "Sent" | "Follow-up" | "Rejected" | "Archived";

export interface Vacancy {
  id: number;
  external_id: string;
  rank: number | null;
  source: string;
  company: string;
  title: string;
  location: string;
  posted: string;
  date_status: string;
  language: string;
  fit_score: number;
  priority: string;
  submit_status: ApplicationStatus;
  next_action: string;
  cv_file_path: string;
  pdf_file_path: string;
  png_preview_path: string;
  source_url: string;
  tailored_headline: string;
  top_match_keywords: string;
  gaps_risks: string;
  adaptation_strategy: string;
}

export interface ApplicationMaterial {
  vacancy_id: number;
  short_note: string;
  recruiter_dm: string;
  email_cover_letter: string;
  fit_summary: string;
}
```

Create `frontend/src/api.ts`:

```ts
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; service: string }>("/api/health"),
  vacancies: () => request<Vacancy[]>("/api/vacancies"),
  createVacancy: (payload: { external_id: string; company: string; title: string; source?: string; source_url?: string }) =>
    request<Vacancy>("/api/vacancies", { method: "POST", body: JSON.stringify(payload) }),
  updateStatus: (id: number, status: ApplicationStatus) =>
    request<Vacancy>(`/api/vacancies/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, actor: "user" })
    }),
  importCurrentPackage: () => request<{ imported: number }>("/api/imports/current-package", { method: "POST" }),
  createCandidateFromText: (text: string) => request("/api/candidate/text", { method: "POST", body: JSON.stringify({ text }) }),
  runAnalysis: () => request<{ analyzed: number }>("/api/analysis/run", { method: "POST" }),
  materials: () => request<ApplicationMaterial[]>("/api/materials")
};
```

- [ ] **Step 4: Add shell UI**

Create `frontend/src/components/Layout.tsx`:

```tsx
import type { ReactNode } from "react";
import { BriefcaseBusiness } from "lucide-react";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <BriefcaseBusiness aria-hidden="true" size={22} />
          <span>Job Search Agent</span>
        </div>
        <nav className="nav">
          <a href="#cv">CV Intake</a>
          <a href="#queue">Vacancy Queue</a>
          <a href="#package">Ready-to-Send</a>
          <a href="#exports">Exports</a>
        </nav>
      </aside>
      <section className="workspace">{children}</section>
    </main>
  );
}
```

Create `frontend/src/App.tsx`:

```tsx
import { Layout } from "./components/Layout";
import "./styles.css";

export default function App() {
  return (
    <Layout>
      <header className="workspace-header">
        <div>
          <h1>Vacancy Queue</h1>
          <p>Ready-to-send application workspace for tailored CVs and recruiter messages.</p>
        </div>
      </header>
      <section id="cv" className="panel">
        <h2>CV Intake</h2>
        <textarea placeholder="Paste master CV text here" />
      </section>
      <section id="queue" className="panel">
        <h2>Vacancy Queue</h2>
        <p>Import the current package or add vacancies manually.</p>
      </section>
    </Layout>
  );
}
```

Create `frontend/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Create `frontend/src/styles.css`:

```css
:root {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #17202a;
  background: #f4f6f8;
}

body {
  margin: 0;
}

button,
input,
select,
textarea {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
}

.sidebar {
  background: #17202a;
  color: white;
  padding: 24px 18px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  margin-bottom: 28px;
}

.nav {
  display: grid;
  gap: 8px;
}

.nav a {
  color: #d8dee6;
  text-decoration: none;
  padding: 10px 12px;
  border-radius: 6px;
}

.nav a:hover {
  background: #24313f;
}

.workspace {
  padding: 24px;
}

.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.workspace-header h1 {
  margin: 0;
  font-size: 28px;
}

.workspace-header p {
  margin: 6px 0 0;
  color: #5d6b7a;
}

.panel {
  background: white;
  border: 1px solid #d9e0e7;
  border-radius: 8px;
  padding: 18px;
  margin-bottom: 16px;
}

.panel h2 {
  margin: 0 0 12px;
  font-size: 18px;
}

textarea {
  width: 100%;
  min-height: 150px;
  border: 1px solid #c7d0da;
  border-radius: 6px;
  padding: 12px;
  box-sizing: border-box;
}

@media (max-width: 760px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }
}
```

- [ ] **Step 5: Run frontend tests**

Run:

```bash
cd frontend
npm install
npm test
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: scaffold React frontend"
```

---

### Task 9: Frontend Workflow Components

**Files:**
- Create: `frontend/src/components/CvIntake.tsx`
- Create: `frontend/src/components/ExportBar.tsx`
- Create: `frontend/src/components/ImportPanel.tsx`
- Create: `frontend/src/components/MetricsStrip.tsx`
- Create: `frontend/src/components/VacancyDetail.tsx`
- Create: `frontend/src/components/VacancyFilters.tsx`
- Create: `frontend/src/components/VacancyTable.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/__tests__/App.test.tsx`

- [ ] **Step 1: Replace frontend test with workflow expectations**

Replace `frontend/src/__tests__/App.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "../App";

vi.mock("../api", () => ({
  api: {
    vacancies: async () => [],
    materials: async () => []
  }
}));

describe("App", () => {
  it("renders the MVP workflow controls", async () => {
    render(<App />);
    expect(screen.getByText("Job Search Agent")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Import Current Package/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Run Analysis/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Paste master CV text/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Add workflow components**

Create `frontend/src/components/CvIntake.tsx`:

```tsx
import { Save } from "lucide-react";

export function CvIntake({ value, onChange, onSubmit }: { value: string; onChange: (value: string) => void; onSubmit: () => void }) {
  return (
    <section id="cv" className="panel">
      <div className="panel-header">
        <h2>CV Intake</h2>
        <button type="button" onClick={onSubmit}>
          <Save size={16} aria-hidden="true" /> Save CV
        </button>
      </div>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} placeholder="Paste master CV text here" />
    </section>
  );
}
```

Create `frontend/src/components/ImportPanel.tsx`:

```tsx
import { FileSpreadsheet, Wand2 } from "lucide-react";

export function ImportPanel({ onImport, onAnalyze }: { onImport: () => void; onAnalyze: () => void }) {
  return (
    <section className="toolbar">
      <button type="button" onClick={onImport}>
        <FileSpreadsheet size={16} aria-hidden="true" /> Import Current Package
      </button>
      <button type="button" onClick={onAnalyze}>
        <Wand2 size={16} aria-hidden="true" /> Run Analysis
      </button>
    </section>
  );
}
```

Create `frontend/src/components/MetricsStrip.tsx`:

```tsx
import type { Vacancy } from "../types";

export function MetricsStrip({ vacancies }: { vacancies: Vacancy[] }) {
  const veryHigh = vacancies.filter((vacancy) => vacancy.priority === "Very High").length;
  const ready = vacancies.filter((vacancy) => vacancy.submit_status === "Ready to send").length;
  const sent = vacancies.filter((vacancy) => vacancy.submit_status === "Sent").length;
  return (
    <section className="metrics">
      <div><span>Total</span><strong>{vacancies.length}</strong></div>
      <div><span>Very High</span><strong>{veryHigh}</strong></div>
      <div><span>Ready</span><strong>{ready}</strong></div>
      <div><span>Sent</span><strong>{sent}</strong></div>
    </section>
  );
}
```

Create `frontend/src/components/VacancyFilters.tsx`:

```tsx
export interface Filters {
  priority: string;
  source: string;
  language: string;
}

export function VacancyFilters({ filters, onChange }: { filters: Filters; onChange: (filters: Filters) => void }) {
  return (
    <div className="filters">
      <select value={filters.priority} onChange={(event) => onChange({ ...filters, priority: event.target.value })} aria-label="Priority">
        <option value="">All priorities</option>
        <option>Very High</option>
        <option>High</option>
        <option>Medium</option>
        <option>Low</option>
      </select>
      <input value={filters.source} onChange={(event) => onChange({ ...filters, source: event.target.value })} placeholder="Source" />
      <input value={filters.language} onChange={(event) => onChange({ ...filters, language: event.target.value })} placeholder="Language" />
    </div>
  );
}
```

Create `frontend/src/components/VacancyTable.tsx`:

```tsx
import type { Vacancy } from "../types";

export function VacancyTable({ vacancies, selectedId, onSelect }: { vacancies: Vacancy[]; selectedId?: number; onSelect: (vacancy: Vacancy) => void }) {
  return (
    <table className="queue-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Company</th>
          <th>Vacancy</th>
          <th>Fit</th>
          <th>Priority</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {vacancies.map((vacancy) => (
          <tr key={vacancy.id} className={vacancy.id === selectedId ? "selected" : ""} onClick={() => onSelect(vacancy)}>
            <td>{vacancy.rank ?? ""}</td>
            <td>{vacancy.company}</td>
            <td>{vacancy.title}</td>
            <td>{vacancy.fit_score}</td>
            <td>{vacancy.priority}</td>
            <td>{vacancy.submit_status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

Create `frontend/src/components/VacancyDetail.tsx`:

```tsx
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "../types";

const statuses: ApplicationStatus[] = ["Draft", "Ready to send", "Sent", "Follow-up", "Rejected", "Archived"];

export function VacancyDetail({
  vacancy,
  material,
  onStatusChange
}: {
  vacancy?: Vacancy;
  material?: ApplicationMaterial;
  onStatusChange: (status: ApplicationStatus) => void;
}) {
  if (!vacancy) {
    return <aside className="detail-panel">Select a vacancy to review ready-to-send materials.</aside>;
  }
  return (
    <aside className="detail-panel">
      <h2>{vacancy.company}</h2>
      <p className="muted">{vacancy.title}</p>
      <label>
        Status
        <select value={vacancy.submit_status} onChange={(event) => onStatusChange(event.target.value as ApplicationStatus)}>
          {statuses.map((status) => <option key={status}>{status}</option>)}
        </select>
      </label>
      <dl>
        <dt>Headline</dt>
        <dd>{vacancy.tailored_headline}</dd>
        <dt>Keywords</dt>
        <dd>{vacancy.top_match_keywords}</dd>
        <dt>Risks</dt>
        <dd>{vacancy.gaps_risks}</dd>
        <dt>Strategy</dt>
        <dd>{vacancy.adaptation_strategy}</dd>
      </dl>
      {vacancy.source_url && <a href={vacancy.source_url} target="_blank" rel="noreferrer">Open vacancy</a>}
      {vacancy.cv_file_path && <a href={vacancy.cv_file_path} target="_blank" rel="noreferrer">Open tailored CV</a>}
      {material && (
        <div className="messages">
          <h3>Ready-to-send</h3>
          <textarea readOnly value={material.short_note} />
          <textarea readOnly value={material.recruiter_dm} />
          <textarea readOnly value={material.email_cover_letter} />
        </div>
      )}
    </aside>
  );
}
```

Create `frontend/src/components/ExportBar.tsx`:

```tsx
import { Download } from "lucide-react";

export function ExportBar() {
  return (
    <section id="exports" className="panel compact">
      <a className="button-link" href="/api/exports/zip">
        <Download size={16} aria-hidden="true" /> Export ZIP Package
      </a>
    </section>
  );
}
```

- [ ] **Step 3: Wire App state**

Replace `frontend/src/App.tsx`:

```tsx
import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { CvIntake } from "./components/CvIntake";
import { ExportBar } from "./components/ExportBar";
import { ImportPanel } from "./components/ImportPanel";
import { Layout } from "./components/Layout";
import { MetricsStrip } from "./components/MetricsStrip";
import { type Filters, VacancyFilters } from "./components/VacancyFilters";
import { VacancyDetail } from "./components/VacancyDetail";
import { VacancyTable } from "./components/VacancyTable";
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "./types";
import "./styles.css";

export default function App() {
  const [cvText, setCvText] = useState("");
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [materials, setMaterials] = useState<ApplicationMaterial[]>([]);
  const [selected, setSelected] = useState<Vacancy | undefined>();
  const [filters, setFilters] = useState<Filters>({ priority: "", source: "", language: "" });
  const [message, setMessage] = useState("");

  async function refresh() {
    const [vacancyRows, materialRows] = await Promise.all([api.vacancies(), api.materials()]);
    setVacancies(vacancyRows);
    setMaterials(materialRows);
    setSelected((current) => vacancyRows.find((row) => row.id === current?.id) ?? vacancyRows[0]);
  }

  useEffect(() => {
    refresh().catch(() => setMessage("Backend is not connected yet."));
  }, []);

  const visibleVacancies = useMemo(
    () =>
      vacancies.filter((vacancy) => {
        return (
          (!filters.priority || vacancy.priority === filters.priority) &&
          (!filters.source || vacancy.source.toLowerCase().includes(filters.source.toLowerCase())) &&
          (!filters.language || vacancy.language.toLowerCase().includes(filters.language.toLowerCase()))
        );
      }),
    [filters, vacancies]
  );

  async function saveCv() {
    await api.createCandidateFromText(cvText);
    setMessage("CV profile saved.");
  }

  async function importPackage() {
    const result = await api.importCurrentPackage();
    setMessage(`Imported ${result.imported} vacancies.`);
    await refresh();
  }

  async function runAnalysis() {
    const result = await api.runAnalysis();
    setMessage(`Analyzed ${result.analyzed} vacancies.`);
    await refresh();
  }

  async function updateStatus(status: ApplicationStatus) {
    if (!selected) return;
    const updated = await api.updateStatus(selected.id, status);
    setVacancies((rows) => rows.map((row) => (row.id === updated.id ? updated : row)));
    setSelected(updated);
  }

  const selectedMaterial = materials.find((material) => material.vacancy_id === selected?.id);

  return (
    <Layout>
      <header className="workspace-header">
        <div>
          <h1>Vacancy Queue</h1>
          <p>Ready-to-send application workspace for tailored CVs and recruiter messages.</p>
        </div>
      </header>
      {message && <div className="notice">{message}</div>}
      <ImportPanel onImport={importPackage} onAnalyze={runAnalysis} />
      <MetricsStrip vacancies={vacancies} />
      <CvIntake value={cvText} onChange={setCvText} onSubmit={saveCv} />
      <section id="queue" className="queue-layout">
        <div className="panel">
          <div className="panel-header">
            <h2>Vacancy Queue</h2>
            <VacancyFilters filters={filters} onChange={setFilters} />
          </div>
          <VacancyTable vacancies={visibleVacancies} selectedId={selected?.id} onSelect={setSelected} />
        </div>
        <VacancyDetail vacancy={selected} material={selectedMaterial} onStatusChange={updateStatus} />
      </section>
      <ExportBar />
    </Layout>
  );
}
```

- [ ] **Step 4: Extend CSS for operational UI**

Append to `frontend/src/styles.css`:

```css
button,
.button-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid #bac5d1;
  background: #ffffff;
  color: #17202a;
  border-radius: 6px;
  padding: 9px 12px;
  text-decoration: none;
  cursor: pointer;
}

button:hover,
.button-link:hover {
  border-color: #718096;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.metrics div {
  background: #ffffff;
  border: 1px solid #d9e0e7;
  border-radius: 8px;
  padding: 14px;
}

.metrics span {
  display: block;
  color: #657386;
  font-size: 13px;
}

.metrics strong {
  display: block;
  font-size: 28px;
  margin-top: 4px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.filters {
  display: flex;
  gap: 8px;
}

.filters input,
.filters select,
.detail-panel select {
  border: 1px solid #c7d0da;
  border-radius: 6px;
  padding: 8px;
}

.queue-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 16px;
}

.queue-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.queue-table th,
.queue-table td {
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  padding: 10px;
}

.queue-table tr {
  cursor: pointer;
}

.queue-table tr.selected,
.queue-table tbody tr:hover {
  background: #eef4f8;
}

.detail-panel {
  background: #ffffff;
  border: 1px solid #d9e0e7;
  border-radius: 8px;
  padding: 18px;
  min-height: 360px;
}

.detail-panel h2 {
  margin: 0;
}

.detail-panel a {
  display: block;
  margin: 8px 0;
  color: #0f609b;
}

.muted,
.notice {
  color: #657386;
}

.notice {
  background: #edf7ed;
  border: 1px solid #bfdfc0;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 14px;
}

dl {
  margin: 16px 0;
}

dt {
  font-weight: 700;
  margin-top: 10px;
}

dd {
  margin: 4px 0 0;
  color: #344456;
}

.messages textarea {
  min-height: 90px;
  margin-top: 8px;
}

.compact {
  padding: 12px;
}

@media (max-width: 1040px) {
  .queue-layout,
  .metrics {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 5: Run frontend tests and build**

Run:

```bash
cd frontend
npm test
npm run build
```

Expected:

```text
1 passed
```

and build exits successfully.

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: build application workspace UI"
```

---

### Task 10: Render Deployment And End-To-End Verification

**Files:**
- Create: `render.yaml`
- Create: `backend/README.md`
- Modify: `README.md`

- [ ] **Step 1: Add Render Blueprint**

Create `render.yaml`:

```yaml
services:
  - type: web
    name: job-search-agent-api
    env: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: APP_ENV
        value: production
      - key: STORAGE_DIR
        value: /var/data/storage
      - key: CORS_ORIGINS
        fromService:
          type: web
          name: job-search-agent-web
          property: host
      - key: DATABASE_URL
        fromDatabase:
          name: job-search-agent-db
          property: connectionString
    disk:
      name: job-search-agent-storage
      mountPath: /var/data
      sizeGB: 1
  - type: web
    name: job-search-agent-web
    env: static
    rootDir: frontend
    buildCommand: npm install && npm run build
    staticPublishPath: dist
    envVars:
      - key: VITE_API_BASE
        fromService:
          type: web
          name: job-search-agent-api
          property: host
databases:
  - name: job-search-agent-db
    databaseName: job_search_agent
    user: job_search_agent
```

- [ ] **Step 2: Add deployment docs**

Create `backend/README.md`:

```markdown
# Backend

Local development:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```
```

Replace `README.md`:

```markdown
# Job Search Agent

React + FastAPI web app for turning a CV and vacancy queue into ready-to-send job application materials.

## MVP

- paste or upload a CV
- import the current tailored CV workbook package
- score and prioritize vacancies
- generate ready-to-send notes, DMs, and email cover letters
- manually track statuses
- export a ZIP package

The app does not submit applications automatically. Only the user can mark an application as sent.

## Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Render

Use `render.yaml` as a Blueprint. Configure these environment variables if not supplied by the Blueprint:

- `DATABASE_URL`
- `STORAGE_DIR`
- `CORS_ORIGINS`
- `APP_ENV`
- `OPENAI_API_KEY` for optional LLM-assisted generation
```

- [ ] **Step 3: Run all tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest
cd ../frontend
npm test
npm run build
```

Expected:

```text
backend tests pass
frontend tests pass
frontend build succeeds
```

- [ ] **Step 4: Start local servers**

Run backend:

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Run frontend in another terminal:

```bash
cd frontend
npm run dev -- --host 127.0.0.1
```

Expected:

- backend health responds at `http://127.0.0.1:8000/api/health`
- frontend loads at `http://127.0.0.1:5173`
- importing current package returns 26 rows when seed package is present

- [ ] **Step 5: Commit**

```bash
git add render.yaml README.md backend/README.md
git commit -m "chore: add Render deployment configuration"
```

---

## Self-Review Notes

Spec coverage:

- CV intake is covered by Tasks 4, 7, 8, and 9.
- Workbook/CSV import is covered by Tasks 3 and 7.
- Manual vacancy creation is covered by Task 7.
- Deterministic scoring and ready-to-send materials are covered by Task 5.
- Manual status tracking and the no-auto-Sent rule are covered by Tasks 2, 7, and 9.
- CSV/XLSX/HTML/ZIP export is covered by Task 6.
- React + FastAPI architecture is covered by Tasks 1, 8, and 9.
- Render deployment is covered by Task 10.

Known MVP constraints:

- LLM generation is intentionally outside this plan. The deterministic materials service keeps the app usable without requiring an API key.
- The current package remains seed data and is not required to be committed for the app code to run.
