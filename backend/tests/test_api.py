from fastapi.testclient import TestClient
from io import BytesIO
from docx import Document
from sqlmodel import SQLModel

from app.database import engine
from app.main import app


def reset_database() -> None:
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_health_returns_ok():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "job-search-agent"}


def test_root_returns_api_entrypoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "job-search-agent",
        "health": "/api/health",
        "docs": "/docs",
    }


def test_create_vacancy_and_list_it():
    reset_database()
    with TestClient(app) as client:
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


def test_create_vacancy_accepts_source_description_and_generates_tailored_cv():
    reset_database()
    with TestClient(app) as client:
        candidate = client.post(
            "/api/candidate/text",
            json={"text": "Aleksandr Grenkov Lead Product Designer Automotive UX Voice UX Design Systems English B2"},
        )
        assert candidate.status_code == 200

        created_response = client.post(
            "/api/vacancies",
            json={
                "external_id": "REAL-1",
                "source": "LinkedIn",
                "company": "Rivian",
                "title": "Sr. Lead Product Designer - Design System Frameworks",
                "location": "Palo Alto / Remote",
                "language": "English",
                "source_url": "https://www.linkedin.com/jobs/example",
                "description_raw": "Design system frameworks for automotive HMI products. Partner with engineering and product.",
                "requirements": "Design systems; Automotive UX; HMI; Figma; component governance",
                "responsibilities": "Define reusable frameworks and improve product consistency across vehicle experiences.",
            },
        )
        assert created_response.status_code == 200
        created = created_response.json()
        assert created["description_raw"].startswith("Design system frameworks")
        assert "Design Systems" in created["vacancy_keywords"]
        assert "Automotive UX" in created["vacancy_keywords"]
        assert "Component Governance" in created["vacancy_keywords"]

        analysis_response = client.post("/api/analysis/run")
        assert analysis_response.status_code == 200

        vacancy = client.get("/api/vacancies").json()[0]
        assert vacancy["cv_file_path"] == f"/api/vacancies/{vacancy['id']}/tailored-cv.docx"
        assert "Design Systems" in vacancy["top_match_keywords"]
        assert "Automotive" in vacancy["top_match_keywords"]

        cv_response = client.get(vacancy["cv_file_path"])
        assert cv_response.status_code == 200
        document = Document(BytesIO(cv_response.content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        assert "Rivian" in text
        assert "Sr. Lead Product Designer - Design System Frameworks" in text
        assert "Design Systems" in text
        assert "Automotive UX" in text
        assert "Vacancy Source" in text


def test_status_update_rejects_caller_controlled_actor():
    reset_database()
    with TestClient(app) as client:
        created = client.post(
            "/api/vacancies",
            json={"external_id": "MAN-2", "company": "TestCo", "title": "Lead Product Designer"},
        ).json()
        response = client.patch(
            f"/api/vacancies/{created['id']}/status",
            json={"status": "Sent", "actor": "system"},
        )
        assert response.status_code == 422


def test_user_status_update_can_mark_sent():
    reset_database()
    with TestClient(app) as client:
        created = client.post(
            "/api/vacancies",
            json={"external_id": "MAN-3", "company": "TestCo", "title": "Lead Product Designer"},
        ).json()
        response = client.patch(
            f"/api/vacancies/{created['id']}/status",
            json={"status": "Sent"},
        )
        assert response.status_code == 200
        assert response.json()["submit_status"] == "Sent"


def test_candidate_analysis_materials_and_export_flow():
    reset_database()
    with TestClient(app) as client:
        candidate_response = client.post(
            "/api/candidate/text",
            json={"text": "Aleksandr Grenkov Lead Product Designer Automotive UX Voice UX English B2"},
        )
        assert candidate_response.status_code == 200

        vacancy_response = client.post(
            "/api/vacancies",
            json={
                "external_id": "L08",
                "company": "42dot",
                "title": "Lead Brand / UI Designer - Automotive",
                "language": "English",
            },
        )
        assert vacancy_response.status_code == 200

        analysis_response = client.post("/api/analysis/run")
        assert analysis_response.status_code == 200
        assert analysis_response.json() == {"analyzed": 1}

        materials_response = client.get("/api/materials")
        assert materials_response.status_code == 200
        materials = materials_response.json()
        assert len(materials) == 1
        assert "42dot" in materials[0]["short_note"]

        export_response = client.get("/api/exports/zip")
        assert export_response.status_code == 200
        assert export_response.headers["content-type"] == "application/zip"


def test_analysis_from_cv_requires_candidate_profile():
    reset_database()
    with TestClient(app) as client:
        response = client.post("/api/analysis/from-cv")
        assert response.status_code == 400
        assert response.json()["detail"] == "Create a candidate profile first"


def test_analysis_from_cv_generates_twenty_recruiter_role_matches():
    reset_database()
    cv_text = (
        "Aleksandr Grenkov Lead Product Designer Automotive UX HMI Voice UX "
        "Conversational Design Design Systems Smart City Transport Enterprise UX "
        "Telecom B2B B2C Mobile UX English B2"
    )
    with TestClient(app) as client:
        candidate_response = client.post("/api/candidate/text", json={"text": cv_text})
        assert candidate_response.status_code == 200

        response = client.post("/api/analysis/from-cv")
        assert response.status_code == 200
        assert response.json() == {"generated": 20, "analyzed": 20}

        vacancies = client.get("/api/vacancies").json()
        assert len(vacancies) == 20
        assert vacancies[0]["source"] == "CV Recruiter Match"
        assert vacancies[0]["company"] == "Target role"
        assert vacancies[0]["date_status"] == "generated from CV, not a live vacancy"
        assert vacancies[0]["title"] == "Lead Product Designer"
        assert "Product Design" in vacancies[0]["top_match_keywords"]
        assert "English B2" in vacancies[0]["gaps_risks"]
        assert {row["rank"] for row in vacancies} == set(range(1, 21))

        materials = client.get("/api/materials").json()
        assert len(materials) == 20
        assert "Lead Product Designer" in materials[0]["short_note"]


def test_analysis_from_cv_links_every_row_to_tailored_cv_docx():
    reset_database()
    cv_text = (
        "Aleksandr Grenkov Lead Product Designer Automotive UX HMI Voice UX "
        "Design Systems Smart City Transport Enterprise UX English B2"
    )
    with TestClient(app) as client:
        client.post("/api/candidate/text", json={"text": cv_text})
        client.post("/api/analysis/from-cv")

        vacancies = client.get("/api/vacancies").json()
        assert len(vacancies) == 20
        assert all(row["cv_file_path"] == f"/api/vacancies/{row['id']}/tailored-cv.docx" for row in vacancies)

        first = vacancies[0]
        response = client.get(first["cv_file_path"])
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        document = Document(BytesIO(response.content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        assert "ALEKSANDR GRENKOV" in text
        assert first["title"] in text
        assert "Google XYZ" in text
        assert "English B2" in text
        assert "English C1" not in text
        assert "increased conversion by" not in text.lower()


def test_master_cv_template_docx_is_recruiter_safe_and_adaptable():
    reset_database()
    with TestClient(app) as client:
        client.post(
            "/api/candidate/text",
            json={
                "text": (
                    "Aleksandr Grenkov Lead Product Designer Automotive UX HMI Voice UX "
                    "Design Systems Smart City Transport Enterprise UX English B2"
                )
            },
        )
        response = client.get("/api/candidate/master-cv.docx")
        assert response.status_code == 200

        document = Document(BytesIO(response.content))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        assert "ATS-OPTIMIZED MASTER CV TEMPLATE" in text
        assert len(document.tables) == 0
        for section in [
            "Contact",
            "Target Title",
            "Professional Summary",
            "Target Keywords",
            "Core Skills",
            "Domain Expertise",
            "Professional Experience",
            "Selected Projects",
            "Education",
            "Languages",
            "Tools",
        ]:
            assert section in text
        assert "[TARGET ROLE]" in text
        assert "[ROLE]" in text
        assert "[COMPANY]" in text
        assert "[DOMAIN KEYWORDS]" in text
        assert "[VACANCY KEYWORDS]" in text
        assert "Google XYZ" in text
        assert "English B2" in text
        assert "English C1" not in text
        assert "worked on" not in text.lower()


def test_candidate_upload_sanitizes_filename(tmp_path, monkeypatch):
    reset_database()
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "storage_dir", tmp_path)
    with TestClient(app) as client:
        response = client.post(
            "/api/candidate/upload",
            files={"file": ("../cv.txt", b"Aleksandr Grenkov Lead Product Designer", "text/plain")},
        )
        assert response.status_code == 200
    assert (tmp_path / "uploads" / "cv.txt").exists()
    assert not (tmp_path / "cv.txt").exists()


def test_upload_vacancy_file_imports_csv_rows():
    reset_database()
    csv_bytes = (
        "Rank,ID,Source,Company,Vacancy,Location,Posted,Date Status,Language,Fit,Priority,Submit Status,Next Action,CV File Path,Source URL,Tailored Headline,Top Match Keywords,Gaps / Risks,Adaptation Strategy\n"
        "1,L08,LinkedIn,42dot,Lead Brand / UI Designer - Automotive,Remote,2 days ago,verified,English,96,Very High,Ready to submit manually,Submit manually,Tailored_CVs/08.docx,https://example.com/42dot,Lead Product Designer,Automotive; HMI,US location risk,Lead with ATOM\n"
        "2,L04,LinkedIn,ZOE,Lead Product Designer - Design System,Remote,4 days ago,verified,English,95,Very High,Ready to submit manually,Submit manually,Tailored_CVs/04.docx,https://example.com/zoe,Design Systems Lead,Design systems,Need token examples,Lead with systems\n"
    ).encode("utf-8")
    with TestClient(app) as client:
        response = client.post(
            "/api/imports/vacancies/upload",
            files={"file": ("vacancies.csv", csv_bytes, "text/csv")},
        )
        assert response.status_code == 200
        assert response.json() == {"imported": 2}

        vacancies_response = client.get("/api/vacancies")
        assert vacancies_response.status_code == 200
        rows = vacancies_response.json()
        assert [row["company"] for row in rows] == ["42dot", "ZOE"]
        assert rows[0]["source_url"] == "https://example.com/42dot"


def test_upload_vacancy_file_rejects_unsupported_format():
    reset_database()
    with TestClient(app) as client:
        response = client.post(
            "/api/imports/vacancies/upload",
            files={"file": ("vacancies.json", b"{}", "application/json")},
        )
        assert response.status_code == 400
        assert "Unsupported vacancy file type" in response.json()["detail"]
