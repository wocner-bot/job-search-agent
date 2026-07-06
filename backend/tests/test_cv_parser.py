from pathlib import Path

from io import BytesIO
from docx import Document

from app.models import Vacancy
from app.services.cv_writer import build_tailored_cv_document
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


def test_extract_profile_uses_name_and_surname_from_source_cv_in_tailored_cv():
    profile = extract_profile_from_text(
        "MARIA IVANOVA\n"
        "Lead Product Designer\n"
        "Product Strategy, UX Strategy, Design Systems, Automotive UX.\n"
        "Languages: Russian native, English B2."
    )
    vacancy = Vacancy(
        external_id="EN-1",
        company="VehicleCo",
        title="Senior Product Designer",
        language="English",
        description_raw="We need a Senior Product Designer for automotive HMI and design systems.",
    )

    document = Document(BytesIO(build_tailored_cv_document(profile, vacancy).getvalue()))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)

    assert profile.name == "Maria Ivanova"
    assert "MARIA IVANOVA" in text
    assert "Candidate" not in text
    assert "ALEKSANDR GRENKOV" not in text
