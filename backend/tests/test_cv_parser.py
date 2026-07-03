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
