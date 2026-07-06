from pathlib import Path
import re

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
        name=_extract_candidate_name(text),
        raw_cv_text=text,
        target_titles=target_titles,
        experience_areas="; ".join(matched) if matched else "Product Design; UX Strategy",
        languages="Russian native; English B2",
        constraints="Do not inflate language level, metrics, titles, or submission status.",
    )


def _extract_candidate_name(text: str) -> str:
    for raw_line in text.splitlines()[:12]:
        line = raw_line.strip(" \t|•-–—")
        if not line or "@" in line or "http" in line.lower():
            continue
        words = re.findall(r"[A-Za-zА-Яа-яЁё]+(?:['-][A-Za-zА-Яа-яЁё]+)?", line)
        if len(words) > 4 and _looks_like_job_title(" ".join(words[2:])) and not _looks_like_job_title(" ".join(words[:2])):
            return " ".join(word.capitalize() for word in words[:2])
        if _looks_like_job_title(line):
            continue
        if 2 <= len(words) <= 4 and all(len(word) > 1 for word in words):
            return " ".join(word.capitalize() for word in words)
    return "Candidate"


def _looks_like_job_title(line: str) -> bool:
    normalized = line.lower()
    title_terms = (
        "designer",
        "product",
        "manager",
        "engineer",
        "developer",
        "director",
        "lead",
        "senior",
        "junior",
        "ux",
        "ui",
        "researcher",
        "дизайнер",
        "менеджер",
        "разработчик",
        "руководитель",
    )
    return any(term in normalized for term in title_terms)
