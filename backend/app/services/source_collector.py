from __future__ import annotations

import html
import http.cookiejar
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Callable
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen

from app.models import CandidateProfile, Vacancy
from app.services.recruiter import RoleRecommendation
from app.services.vacancy_analysis import extract_vacancy_keywords, infer_vacancy_language
from app.status import ApplicationStatus

HH_API_URL = "https://api.hh.ru/vacancies"
HH_SOURCE = "HH.ru"
LINKEDIN_SOURCE = "LinkedIn"
DESIGN_SIGNAL_TERMS = (
    "product designer",
    "ux",
    "ui",
    "ux/ui",
    "ui/ux",
    "designer",
    "design system",
    "figma",
    "hmi",
    "automotive",
    "researcher",
    "дизайнер",
    "дизайн",
    "интерфейс",
    "исследователь",
)
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
    max_results: int = 0,
) -> list[Vacancy]:
    fetch_json = fetch_json or _fetch_json
    fetch_text = fetch_text or _fetch_text
    today = today or datetime.now(timezone.utc).date()
    date_from = today - timedelta(days=7)

    candidates: list[Vacancy] = []
    seen: set[str] = set()
    for role in roles[:8]:
        for vacancy in _collect_linkedin_vacancies(role, fetch_text, per_role_limit):
            _append_unique(candidates, seen, vacancy)
        for vacancy in _collect_hh_vacancies(role, fetch_json, fetch_text, date_from, per_role_limit):
            _append_unique(candidates, seen, vacancy)
    for vacancy in _collect_telegram_vacancies(profile, roles, fetch_text, date_from, telegram_channels):
        _append_unique(candidates, seen, vacancy)
    return _rank_vacancies(profile, roles, candidates, max_results)


def _collect_hh_vacancies(
    role: RoleRecommendation,
    fetch_json: JsonFetcher,
    fetch_text: TextFetcher,
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
        return _collect_hh_public_page_vacancies(role, fetch_text, date_from, per_role_limit)

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
                fit_score=0,
                priority="Medium",
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


def _collect_hh_public_page_vacancies(
    role: RoleRecommendation,
    fetch_text: TextFetcher,
    date_from: date,
    per_role_limit: int,
) -> list[Vacancy]:
    params = urlencode({"text": role.title, "search_period": "7", "order_by": "publication_time"})
    url = f"https://hh.ru/search/vacancy?{params}"
    try:
        page = fetch_text(url)
    except Exception:
        try:
            page = _fetch_hh_text_with_cookies(url)
        except Exception:
            return []
    return _parse_hh_public_cards(page, role, date_from)[:per_role_limit]


def _parse_hh_public_cards(page: str, role: RoleRecommendation, date_from: date) -> list[Vacancy]:
    rows: list[Vacancy] = []
    seen_urls: set[str] = set()
    for index, raw_card in enumerate(_hh_vacancy_snippets(page), start=1):
        source_url = _clean_hh_url(_extract_first_match(raw_card, r'href="([^"]*hh\.ru/vacancy/\d+[^"]*)"'))
        if not source_url:
            continue
        if source_url in seen_urls:
            continue
        seen_urls.add(source_url)
        title = _clean_text(_extract_first_match(raw_card, r'<a[^>]+href="[^"]*hh\.ru/vacancy/\d+[^"]*"[^>]*>([\s\S]*?)</a>')) or role.title
        company = (
            _clean_text(_extract_first_match(raw_card, r'data-qa="vacancy-serp__vacancy-employer"[^>]*>([\s\S]*?)</a>'))
            or _clean_text(_extract_first_match(raw_card, r'data-qa="vacancy-serp__vacancy-employer-text"[^>]*>([\s\S]*?)</span>'))
            or "HH.ru employer"
        )
        location = _clean_text(_extract_first_match(raw_card, r'data-qa="vacancy-serp__vacancy-address"[^>]*>([\s\S]*?)</span>'))
        description = " ".join(part for part in [title, company, location] if part)
        if not _is_relevant_role_card(description, role):
            continue
        rows.append(
            Vacancy(
                external_id=f"HH-{_hh_id(source_url) or index}",
                source=HH_SOURCE,
                company=company,
                title=title,
                location=location,
                posted="",
                date_status=f"verified within 7 days from HH public search since {date_from.isoformat()}",
                language=infer_vacancy_language(description),
                fit_score=0,
                priority="Medium",
                submit_status=ApplicationStatus.DRAFT,
                next_action="Open HH.ru vacancy, verify status, then send tailored CV manually.",
                source_url=source_url,
                description_raw=description,
                vacancy_keywords=extract_vacancy_keywords(title, description),
                tailored_headline=role.headline,
                top_match_keywords="; ".join(role.keywords),
                gaps_risks="Verify HH.ru vacancy status, location, and application route before sending.",
                adaptation_strategy=role.strategy,
            )
        )
    return rows


def _hh_vacancy_snippets(page: str) -> list[str]:
    snippets: list[str] = []
    for match in re.finditer(r'<a[^>]+href="[^"]*hh\.ru/vacancy/\d+[^"]*"[\s\S]*?</a>', page, flags=re.IGNORECASE):
        start = match.start()
        end = min(len(page), match.end() + 2400)
        snippets.append(page[start:end])
    return snippets


def _is_relevant_role_card(text: str, role: RoleRecommendation) -> bool:
    normalized = text.lower()
    if role.title.lower() in normalized:
        return True
    role_keyword_hits = sum(1 for keyword in role.keywords if keyword.lower() in normalized)
    if role_keyword_hits >= 2:
        return True
    return any(term in normalized for term in DESIGN_SIGNAL_TERMS)


def _collect_linkedin_vacancies(role: RoleRecommendation, fetch_text: TextFetcher, per_role_limit: int) -> list[Vacancy]:
    query = " ".join([role.title, *role.keywords[:3]])
    params = urlencode({"keywords": query, "f_TPR": "r604800", "start": "0"})
    try:
        page = fetch_text(f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{params}")
    except Exception:
        return []
    return _parse_linkedin_cards(page, role)[:per_role_limit]


def _parse_linkedin_cards(page: str, role: RoleRecommendation) -> list[Vacancy]:
    cards: list[Vacancy] = []
    for raw_card in re.findall(r"<li[\s\S]*?</li>", page, flags=re.IGNORECASE):
        source_url = _clean_linkedin_url(_extract_attr(raw_card, "href"))
        if not source_url or "/jobs/view/" not in source_url:
            continue
        title = _clean_text(_extract_tag(raw_card, "h3")) or role.title
        company = _clean_text(_extract_tag(raw_card, "h4")) or "LinkedIn employer"
        location = _clean_text(_extract_first_match(raw_card, r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([\s\S]*?)</span>'))
        posted = _extract_attr(raw_card, "datetime")
        description = " ".join(part for part in [title, company, location] if part)
        cards.append(
            Vacancy(
                external_id=f"LI-{_linkedin_id(source_url) or _slug(title)}",
                source=LINKEDIN_SOURCE,
                company=company,
                title=title,
                location=location,
                posted=posted,
                date_status="verified within 7 days",
                language=infer_vacancy_language(description),
                fit_score=0,
                priority="Medium",
                submit_status=ApplicationStatus.DRAFT,
                next_action="Open LinkedIn vacancy, verify status, then send tailored CV manually.",
                source_url=source_url,
                description_raw=description,
                vacancy_keywords=extract_vacancy_keywords(title, description),
                tailored_headline=role.headline,
                top_match_keywords="; ".join(role.keywords),
                gaps_risks="Verify LinkedIn vacancy status, location, and application route before sending.",
                adaptation_strategy=role.strategy,
            )
        )
    return cards


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
    stopwords = {
        "and",
        "the",
        "with",
        "для",
        "или",
        "как",
        "что",
        "это",
        "designer",
        "design",
        "product",
        "lead",
        "senior",
        "head",
        "remote",
        "english",
    }
    return tuple(dict.fromkeys(token for token in tokens if token not in stopwords))[:80]


def _matches_keywords(text: str, keywords: tuple[str, ...]) -> bool:
    normalized = text.lower()
    has_profile_match = any(keyword in normalized for keyword in keywords)
    has_design_signal = any(term in normalized for term in DESIGN_SIGNAL_TERMS)
    return has_profile_match and has_design_signal


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


def _append_unique(rows: list[Vacancy], seen: set[str], vacancy: Vacancy) -> None:
    key = vacancy.source_url or f"{vacancy.source}:{vacancy.title}:{vacancy.company}"
    if key in seen:
        return
    seen.add(key)
    rows.append(vacancy)


def _rank_vacancies(
    profile: CandidateProfile,
    roles: tuple[RoleRecommendation, ...],
    vacancies: list[Vacancy],
    max_results: int,
) -> list[Vacancy]:
    ranked = sorted(vacancies, key=lambda vacancy: _relevance_score(profile, roles, vacancy), reverse=True)
    ranked = _keep_source_groups_visible(ranked)
    selected = ranked[:max_results] if max_results > 0 else ranked
    for index, vacancy in enumerate(selected, start=1):
        vacancy.rank = index
    return selected


def _keep_source_groups_visible(ranked: list[Vacancy]) -> list[Vacancy]:
    visible: list[Vacancy] = []
    visible_ids: set[int] = set()
    seen_groups: set[str] = set()

    for vacancy in ranked:
        group = _source_group(vacancy)
        if group in seen_groups:
            continue
        seen_groups.add(group)
        visible_ids.add(id(vacancy))
        visible.append(vacancy)

    for vacancy in ranked:
        if id(vacancy) in visible_ids:
            continue
        visible.append(vacancy)

    return visible


def _source_group(vacancy: Vacancy) -> str:
    if vacancy.source.startswith("Telegram"):
        return "Telegram"
    return vacancy.source or "Unknown"


def _relevance_score(profile: CandidateProfile, roles: tuple[RoleRecommendation, ...], vacancy: Vacancy) -> int:
    text = " ".join(
        [
            vacancy.title,
            vacancy.description_raw,
            vacancy.requirements,
            vacancy.responsibilities,
            vacancy.vacancy_keywords,
            vacancy.top_match_keywords,
        ]
    ).lower()
    score = 0
    profile_keywords = _profile_keywords(profile, roles)
    score += sum(2 for keyword in profile_keywords if keyword in text)
    score += max((_role_match_score(text, role) for role in roles[:12]), default=0)
    score += sum(3 for term in DESIGN_SIGNAL_TERMS if term in text)
    if vacancy.source.startswith("Telegram"):
        score += 8
    if vacancy.source == HH_SOURCE and "search link" not in vacancy.date_status:
        score += 10
    if "search link" in vacancy.date_status:
        score -= 12
    if vacancy.description_raw and "search link" not in vacancy.description_raw.lower():
        score += 12
    vacancy.fit_score = min(100, max(vacancy.fit_score, 55 + score))
    return score


def _role_match_score(text: str, role: RoleRecommendation) -> int:
    score = 0
    if role.title.lower() in text:
        score += 30
    score += sum(7 for keyword in role.keywords if keyword.lower() in text)
    return score


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
    request = Request(
        url,
        headers=_browser_headers(),
    )
    with urlopen(request, timeout=12) as response:
        return response.read().decode("utf-8", errors="replace")


def _fetch_hh_text_with_cookies(url: str) -> str:
    cookie_jar = http.cookiejar.CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookie_jar))
    opener.open(Request("https://hh.ru/", headers=_browser_headers()), timeout=12).read()
    with opener.open(Request(url, headers=_browser_headers()), timeout=12) as response:
        return response.read().decode("utf-8", errors="replace")


def _browser_headers() -> dict[str, str]:
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
    }


def _clean_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _extract_tag(fragment: str, tag: str) -> str:
    return _extract_first_match(fragment, rf"<{tag}[^>]*>([\s\S]*?)</{tag}>")


def _extract_attr(fragment: str, attr: str) -> str:
    return html.unescape(_extract_first_match(fragment, rf'{attr}="([^"]+)"'))


def _extract_first_match(fragment: str, pattern: str) -> str:
    match = re.search(pattern, fragment, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def _clean_linkedin_url(value: str) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    if value.startswith("/"):
        value = f"https://www.linkedin.com{value}"
    match = re.search(r"(https://www\.linkedin\.com/jobs/view/\d+)", value)
    return match.group(1) if match else value.split("?", 1)[0]


def _linkedin_id(value: str) -> str:
    match = re.search(r"/jobs/view/(\d+)", value)
    return match.group(1) if match else ""


def _clean_hh_url(value: str) -> str:
    if not value:
        return ""
    value = html.unescape(value)
    if value.startswith("/vacancy/"):
        value = f"https://hh.ru{value}"
    match = re.search(r"(https://hh\.ru/vacancy/\d+)", value)
    return match.group(1) if match else ""


def _hh_id(value: str) -> str:
    match = re.search(r"/vacancy/(\d+)", value)
    return match.group(1) if match else ""


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
