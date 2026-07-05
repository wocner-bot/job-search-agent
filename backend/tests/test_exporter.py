from zipfile import ZipFile

from openpyxl import load_workbook

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
        [
            Vacancy(
                external_id="L08",
                company="42dot",
                title="Automotive Designer",
                cv_file_path="Tailored_CVs/08.docx",
                source_url="https://example.com",
            )
        ],
    )
    text = output.read_text(encoding="utf-8")
    assert 'href="Tailored_CVs/08.docx"' in text
    assert 'href="https://example.com"' in text


def test_export_queue_xlsx_writes_workbook(tmp_path):
    output = export_queue_xlsx(
        tmp_path,
        [
            Vacancy(
                external_id="L08",
                company="42dot",
                title="Automotive Designer",
                cv_file_path="/api/vacancies/1/tailored-cv.docx",
                source_url="https://example.com",
                description_raw="Original vacancy text",
                vacancy_keywords="Automotive UX; HMI",
            )
        ],
    )
    assert output.exists()
    assert output.suffix == ".xlsx"
    workbook = load_workbook(output)
    sheet = workbook["Application Queue"]
    assert sheet["H2"].hyperlink.target == "/api/vacancies/1/tailored-cv.docx"
    assert sheet["I2"].hyperlink.target == "https://example.com"
    assert sheet["K2"].value == "Original vacancy text"


def test_export_zip_package_contains_html_and_csv(tmp_path):
    vacancy = Vacancy(id=1, external_id="L08", company="42dot", title="Automotive Designer")
    material = ApplicationMaterial(vacancy_id=1, short_note="Hi", recruiter_dm="DM", email_cover_letter="Email")
    output = export_zip_package(tmp_path, [vacancy], [material])
    with ZipFile(output) as archive:
        assert "application_queue.csv" in archive.namelist()
        assert "application_queue.xlsx" in archive.namelist()
        assert "cv_links_index.html" in archive.namelist()
