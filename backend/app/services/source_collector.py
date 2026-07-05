from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models import CandidateProfile, Vacancy
from app.services.recruiter import RoleRecommendation
from app.services.vacancy_analysis import extract_vacancy_keywords, infer_vacancy_language
from app.status import ApplicationStatus

HH_API_URL = "https://api.hh.ru/vacancies"
HH_SOURCE = "HH.ru"
TELEGRAM_CHANNELS = (
    "wantapply_design",
    "young_relocate",
    "vdhl_good",
    "moskovskayarabota",
    "professionalsjob",
    "naudalenkebro",
    "zapwork",
)

JsonFetcher = Callable[[str, dict[str, str]], dict]
TextFetcher = Callable[[str], str]


@dataclass(frozen=True)
class TelegramPost:
    channel: str
    message_id: str
    published: date | None
    text: str

    @property
    def url(self) -> str:
        return f"https://t.me/{self.channel}/{self.message_id}"


def collect_live_vacancies(
    profile: CandidateProfile,
    roles: tuple[RoleRecommendation, ...],
    fetch_json: JsonFetcher | None = None,
    fetch_text: TextFetcher | None = None,
    today: date | None = None,
    telegram_channels: tuple[str, ...] = TELEGRAM_CHANNELS,
    per_role_limit: int = 2,
    max_results: int = 30,
) -> list[Vacancy]:
    fetch_json = fetch_json or _fetch_json
    fetch_text = fetch_text or _fetch_text
    today = today or datetime.now(timezone.utc).date()
    date_from = today - timedelta(days=7)

    vacancies: list[Vacancy] = []
    seen: set[str] = set()
    for role in roles[:8]:
        for vacancy in _collect_hh_vacancies(role, fetch_json, date_from, per_role_limit):
            _append_unique(vacancies, seen, vacancy, max_results)
    for vacancy in _collect_telegram_vacancies(profile, roles, fetch_text, date_from, telegram_channels):
        _append_unique(vacancies, seen, vacancy, max_results)
    return vacancies


def _collect_hh_vacancies(
    role: RoleRecommendation,
    fetch_json: JsonFetcher,
    date_from: date,
    per_role_limit: int,
) -> list[Vacancy]:
    params = {
        "text": role.title,
        "date_from": date_from.isoformat(),
        "per_page": str(per_role_limit),
        "page": "0",
        "order_by": "publication_time",
    }
    try:
        payload = fetch_json(HH_API_URL, params)
    except Exception:
        return [_hh_search_fallback(role)]

    rows: list[Vacancy] = []
    for item in payload.get("items", [])[:per_role_limit]:
        snippet = item.get("snippet") or {}
        requirement = _clean_text(snippet.get("requirement") or "")
        responsibility = _clean_text(snippet.get("responsibility") or "")
        title = _clean_text(item.get("name") or role.title)
        company = _clean_text((item.get("employer") or {}).get("name") or "")
        location = _clean_text((item.get("area") or {}).get("name") or "")
        source_url = item.get("alternate_url") or item.get("url") or ""
        description = " ".join(part for part in [requirement, responsibility] if part)
        keywords = extract_vacancy_keywords(title, description, requirement, responsibility)
        rows.append(
            Vacancy(
                external_id=f"HH-{item.get('id') or source_url or title}",
                source=HH_SOURCE,
                company=company or "HH.ru employer",
                title=title,
                location=location,
                posted=_format_posted(item.get("published_at")),
                date_status="verified within 7 days",
                language=infer_vacancy_language(" ".join([title, description])),
                fit_score=role.fit_score,
                priority=role.priority,
                submit_status=ApplicationStatus.DRAFT,
                next_action="Open source vacancy, verify fit, then send tailored CV manually.",
                source_url=source_url,
                description_raw=description,
                requirements=requirement,
                responsibilities=responsibility,
                vacancy_keywords=keywords,
                tailored_headline=role.headline,
                top_match_keywords="; ".join(role.keywords),
                gaps_risks="Verify vacancy is still open, location/relocation terms, and portfolio requirements before sending.",
                adaptation_strategy=role.strategy,
            )
        )
    return rows


def _hh_search_fallback(role: RoleRecommendation) -> Vacancy:
    params = urlencode({"text": role.title, "search_period": "7", "order_by": "publication_time"})
    return Vacancy(
        external_id=f"HH-SEARCH-{_slug(role.title)}",
        source=HH_SOURCE,
        company="HH.ru search",
        title=role.title,
        location="",
        posted="",
        date_status="source search link; verify live vacancy before sending",
        language=role.language,
        fit_score=role.fit_score,
        priority=role.priority,
        submit_status=ApplicationStatus.DRAFT,
        next_action="Open HH.ru search results, choose a live vacancy from the last 7 days, then add the exact vacancy text.",
        source_url=f"https://hh.ru/search/vacancy?{params}",
        description_raw=f"HH.ru search link for {role.title}. API did not return vacancy details from this environment.",
        vacancy_keywords="; ".join(role.keywords),
        tailored_headline=role.headline,
        top_match_keywords="; ".join(role.keywords),
        gaps_risks="HH.ru API was unavailable or blocked; verify exact vacancy, publication date, and requirements before sending.",
        adaptation_strategy=role.strategy,
    )


def _collect_telegram_vacancies(
    profile: CandidateProfile,
    roles: tuple[RoleRecommendation, ...],
    fetch_text: TextFetcher,
    date_from: date,
    channels: tuple[str, ...],
) -> list[Vacancy]:
    keywords = _profile_keywords(profile, roles)
    rows: list[Vacancy] = []
    for channel in channels:
        try:
            page = fetch_text(f"https://t.me/s/{channel}")
        except Exception:
            continue
        for post in _parse_telegram_posts(channel, page):
            if post.published and post.published < date_from:
                continue
            if not _matches_keywords(post.text, keywords):
                continue
            title = _telegram_title(post.text)
            vacancy_keywords = extract_vacancy_keywords(title, post.text)
            role = _best_role_for_text(roles, post.text)
            rows.append(
                Vacancy(
                    external_id=f"TG-{channel}-{post.message_id}",
                    source=f"Telegram @{channel}",
                    company=f"@{channel}",
                    title=title,
                    location="",
                    posted=post.published.isoformat() if post.published else "",
                    date_status="verified within 7 days",
                    language=infer_vacancy_language(post.text),
                    fit_score=role.fit_score if role else 82,
                    priority=role.priority if role else "High",
                    submit_status=ApplicationStatus.DRAFT,
                    next_action="Open Telegram post, verify contacts and deadline, then send tailored CV manually.",
                    source_url=post.url,
                    description_raw=post.text,
                    requirements="",
                    responsibilities="",
                    vacancy_keywords=vacancy_keywords,
                    tailored_headline=role.headline if role else title,
                    top_match_keywords="; ".join(role.keywords) if role else vacancy_keywords,
                    gaps_risks="Verify the Telegram post author, contact method, and whether the vacancy is still active.",
                    adaptation_strategy=role.strategy if role else f"Adapt CV to the Telegram vacancy language and mirror keywords: {vacancy_keywords}.",
                )
            )
    return rows


def _parse_telegram_posts(channel: str, page: str) -> list[TelegramPost]:
    posts: list[TelegramPost] = []
    pattern = re.compile(
        r'<div class="tgme_widget_message[^"]*"[^>]*data-post="(?P<post>[^"]+)"[\s\S]*?'
        r'(?:<time datetime="(?P<datetime>[^"]+)"></time>)?[\s\S]*?'
        r'<div class="tgme_widget_message_text[^"]*"[^>]*>(?P<text>[\s\S]*?)</div>',
        re.IGNORECASE,
    )
    for match in pattern.finditer(page):
        post_ref = match.group("post")
        if "/" not in post_ref:
            continue
        _, message_id = post_ref.rsplit("/", 1)
        posts.append(
            TelegramPost(
                channel=channel,
                message_id=message_id,
                published=_parse_date(match.group("datetime") or ""),
                text=_clean_text(match.group("text")),
            )
        )
    return posts


def _profile_keywords(profile: CandidateProfile, roles: tuple[RoleRecommendation, ...]) -> tuple[str, ...]:
    raw = " ".join(
        [
            profile.raw_cv_text,
            profile.target_titles,
            profile.experience_areas,
            " ".join(role.title for role in roles[:8]),
            " ".join(" ".join(role.keywords) for role in roles[:8]),
        ]
    ).lower()
    tokens = re.findall(r"[a-zа-яё][a-zа-яё/+.-]{2,}", raw)
    stopwords = {"and", "the", "with", "для", "или", "как", "что", "это", "designer", "design"}
    return tuple(dict.fromkeys(token for token in tokens if token not in stopwords))[:80]


def _matches_keywords(text: str, keywords: tuple[str, ...]) -> bool:
    normalized = text.lower()
    return any(keyword in normalized for keyword in keywords)


def _best_role_for_text(roles: tuple[RoleRecommendation, ...], text: str) -> RoleRecommendation | None:
    normalized = text.lower()
    best_role: RoleRecommendation | None = None
    best_score = -1
    for role in roles:
        score = int(role.title.lower() in normalized)
        score += sum(1 for keyword in role.keywords if keyword.lower() in normalized)
        if score > best_score:
            best_role = role
            best_score = score
    return best_role


def _telegram_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip(" -•")
        if len(line) >= 4:
            return line[:120]
    return "Telegram vacancy"


def _append_unique(rows: list[Vacancy], seen: set[str], vacancy: Vacancy, max_results: int) -> None:
    if len(rows) >= max_results:
        return
    key = vacancy.source_url or f"{vacancy.source}:{vacancy.title}:{vacancy.company}"
    if key in seen:
        return
    seen.add(key)
    vacancy.rank = len(rows) + 1
    rows.append(vacancy)


def _fetch_json(url: str, params: dict[str, str]) -> dict:
    request = Request(
        f"{url}?{urlencode(params)}",
        headers={
            "Accept": "application/json",
            "User-Agent": "job-search-agent/0.1 (https://github.com/wocner-bot/job-search-agent)",
            "HH-User-Agent": "job-search-agent/0.1 (https://github.com/wocner-bot/job-search-agent)",
        },
    )
    with urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "job-search-agent/0.1"})
    with urlopen(request, timeout=12) as response:
        return response.read().decode("utf-8", errors="replace")


def _clean_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").upper()
    return slug or "ROLE"


def _format_posted(value: str | None) -> str:
    if not value:
        return ""
    parsed = _parse_date(value)
    return parsed.isoformat() if parsed else value


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    if re.search(r"[+-]\d{4}$", normalized):
        normalized = f"{normalized[:-2]}:{normalized[-2:]}"
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        return None
