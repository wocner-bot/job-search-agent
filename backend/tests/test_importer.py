from pathlib import Path

from app.services.importer import (
    import_csv_rows,
    import_xlsx_sheet,
    normalize_material_row,
    normalize_queue_row,
)


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


def test_normalize_material_row_imports_messages_and_fit_summary():
    row = {
        "Short Platform Note": "Short note for LinkedIn",
        "Recruiter / Telegram DM": "DM for recruiter",
        "Email Cover Letter": "Cover letter body",
        "Fit Summary": "Strong HMI and automotive fit.",
    }
    material = normalize_material_row(row, vacancy_id=12)
    assert material.vacancy_id == 12
    assert material.short_note == "Short note for LinkedIn"
    assert material.recruiter_dm == "DM for recruiter"
    assert material.email_cover_letter == "Cover letter body"
    assert material.fit_summary == "Strong HMI and automotive fit."

    material_from_summary = normalize_material_row({"Summary": "Summary field fit text."}, vacancy_id=13)
    assert material_from_summary.fit_summary == "Summary field fit text."

    material_with_fallback = normalize_material_row({}, vacancy_id=14)
    assert material_with_fallback.fit_summary == "Imported from tailored package."


def test_real_package_imports_26_rows_when_present():
    workbook = Path(
        "../tailored_cv_package_with_PROJECT_MD/tailored_cv_package/application_queue_with_tailored_cv_links.xlsx"
    )
    if not workbook.exists():
        return
    rows = import_xlsx_sheet(workbook, "Application Queue")
    assert len(rows) == 26
    vacancies = [normalize_queue_row(row, workbook.parent) for row in rows]
    assert sum(1 for vacancy in vacancies if vacancy.priority == "Very High") == 7
    assert all(vacancy.source_url for vacancy in vacancies)
