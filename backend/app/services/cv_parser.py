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
