from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from app.services.source_collector import _fetch_text
from app.services.vacancy_analysis import infer_vacancy_language


@dataclass(frozen=True)
class ExtractedVacancy:
    source: str
    company: str
    title: str
    location: str
    language: str
    description_raw: str


def extract_vacancy_from_url(source_url: str, fetch_text=_fetch_text) -> ExtractedVacancy:
    page = fetch_text(source_url)
    source = _source_from_url(source_url)
    title = _extract_title(page)
    company = _extract_company(page)
    location = _extract_location(page)
    description = _extract_description(page)
    return ExtractedVacancy(
        source=source,
        company=company or "Unknown company",
        title=title or "Untitled vacancy",
        location=location,
        language=infer_vacancy_language(" ".join([title, company, location, description])),
        description_raw=description,
    )


def _source_from_url(source_url: str) -> str:
    host = urlparse(source_url).netloc.lower()
    if "hh.ru" in host:
        return "HH.ru"
    if "linkedin.com" in host:
        return "LinkedIn"
    if "t.me" in host or "telegram" in host:
        return "Telegram"
    return host.replace("www.", "") or "Manual"


def _extract_title(page: str) -> str:
    return _clean_text(
        _first_match(page, r'<h1[^>]*data-qa="vacancy-title"[^>]*>([\s\S]*?)</h1>')
        or _meta_content(page, "og:title")
        or _first_match(page, r"<title[^>]*>([\s\S]*?)</title>")
    )


def _extract_company(page: str) -> str:
    return _clean_text(
        _first_match(page, r'data-qa="vacancy-company-name"[^>]*>([\s\S]*?)</span>')
        or _first_match(page, r'data-qa="vacancy-company-name"[^>]*>([\s\S]*?)</a>')
        or _first_match(page, r'data-qa="vacancy-serp__vacancy-employer-text"[^>]*>([\s\S]*?)</span>')
        or _first_match(page, r'"hiringOrganization"\s*:\s*\{[\s\S]*?"name"\s*:\s*"([^"]+)"')
    )


def _extract_location(page: str) -> str:
    return _clean_text(
        _first_match(page, r'data-qa="vacancy-view-raw-address"[^>]*>([\s\S]*?)</p>')
        or _first_match(page, r'data-qa="vacancy-view-location"[^>]*>([\s\S]*?)</p>')
        or _first_match(page, r'"jobLocation"[\s\S]*?"addressLocality"\s*:\s*"([^"]+)"')
    )


def _extract_description(page: str) -> str:
    text = _clean_text(
        _first_match(page, r'data-qa="vacancy-description"[^>]*>([\s\S]*?)</div>')
        or _meta_content(page, "description")
        or _meta_content(page, "og:description")
    )
    return text[:6000]


def _meta_content(page: str, name: str) -> str:
    patterns = (
        rf'<meta[^>]+(?:name|property)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\']{re.escape(name)}["\']',
    )
    for pattern in patterns:
        value = _first_match(page, pattern)
        if value:
            return value
    return ""


def _first_match(page: str, pattern: str) -> str:
    match = re.search(pattern, page, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def _clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()
