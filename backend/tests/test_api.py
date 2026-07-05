from fastapi.testclient import TestClient
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
