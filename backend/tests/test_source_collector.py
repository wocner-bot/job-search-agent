from datetime import date

from app.models import CandidateProfile
from app.services.recruiter import ROLE_RECOMMENDATIONS
from app.services.source_collector import collect_live_vacancies


def test_collect_live_vacancies_reads_hh_and_telegram_sources():
    profile = CandidateProfile(
        raw_cv_text="Lead Product Designer Automotive UX HMI Design Systems English B2",
        target_titles="Lead Product Designer / Automotive UX Designer",
        experience_areas="Automotive UX; HMI; Design Systems",
    )

    def fake_json(url: str, params: dict[str, str]) -> dict:
        assert url == "https://api.hh.ru/vacancies"
        assert params["date_from"] == "2026-06-29"
        return {
            "items": [
                {
                    "id": "123",
                    "name": "Lead Product Designer HMI",
                    "alternate_url": "https://hh.ru/vacancy/123",
                    "published_at": "2026-07-04T10:00:00+0300",
                    "employer": {"name": "AutoTech"},
                    "area": {"name": "Remote"},
                    "snippet": {
                        "requirement": "Design systems, HMI, automotive UX",
                        "responsibility": "Lead vehicle interface design",
                    },
                }
            ]
        }

    def fake_text(url: str) -> str:
        if "linkedin.com/jobs-guest" in url:
            return """
            <li>
              <a class="base-card__full-link" href="https://www.linkedin.com/jobs/view/456?trackingId=abc"></a>
              <h3 class="base-search-card__title">Lead Product Designer HMI</h3>
              <h4 class="base-search-card__subtitle">VehicleCo</h4>
              <span class="job-search-card__location">Remote</span>
              <time datetime="2026-07-04"></time>
            </li>
            """
        assert "t.me/s/wantapply_design" in url
        return """
        <div class="tgme_widget_message" data-post="wantapply_design/77">
          <time datetime="2026-07-03T09:00:00+00:00"></time>
          <div class="tgme_widget_message_text js-message_text">
            Senior Product Designer<br/>Remote<br/>Design systems and automotive dashboard UX
          </div>
        </div>
        """

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=fake_json,
        fetch_text=fake_text,
        today=date(2026, 7, 6),
        telegram_channels=("wantapply_design",),
        per_role_limit=1,
        max_results=10,
    )

    assert {vacancy.source for vacancy in vacancies} == {"LinkedIn", "HH.ru", "Telegram @wantapply_design"}
    assert any(vacancy.source_url == "https://www.linkedin.com/jobs/view/456" for vacancy in vacancies)
    assert any(vacancy.source_url == "https://hh.ru/vacancy/123" for vacancy in vacancies)
    assert any(vacancy.source_url == "https://t.me/wantapply_design/77" for vacancy in vacancies)
    assert all("7 days" in vacancy.date_status for vacancy in vacancies)
    assert all("search/" not in vacancy.source_url for vacancy in vacancies)
    assert all(vacancy.cv_file_path == "" for vacancy in vacancies)


def test_collect_live_vacancies_reads_hh_public_page_when_api_is_blocked():
    profile = CandidateProfile(raw_cv_text="Lead Product Designer", target_titles="Lead Product Designer")

    def blocked_json(_url: str, _params: dict[str, str]) -> dict:
        raise PermissionError("403")

    def fake_text(url: str) -> str:
        if "hh.ru/search/vacancy" in url:
            return """
            <div class="vacancy-serp-item">
              <a data-qa="serp-item__title" href="https://hh.ru/vacancy/987?from=vacancy_search_list">
                Ведущий продуктовый дизайнер
              </a>
              <a data-qa="vacancy-serp__vacancy-employer" href="/employer/22">Design Team</a>
              <span data-qa="vacancy-serp__vacancy-address">Москва</span>
            </div>
            """
        return ""

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=blocked_json,
        fetch_text=fake_text,
        today=date(2026, 7, 6),
        telegram_channels=(),
        per_role_limit=1,
        max_results=10,
    )

    assert len(vacancies) == 1
    assert vacancies[0].source == "HH.ru"
    assert vacancies[0].source_url == "https://hh.ru/vacancy/987"
    assert vacancies[0].company == "Design Team"
    assert vacancies[0].language == "Russian"
    assert "search/" not in vacancies[0].source_url


def test_collect_live_vacancies_does_not_add_search_link_placeholders_when_sources_are_blocked():
    profile = CandidateProfile(raw_cv_text="Lead Product Designer", target_titles="Lead Product Designer")

    def blocked_json(_url: str, _params: dict[str, str]) -> dict:
        raise PermissionError("403")

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=blocked_json,
        fetch_text=lambda _url: "",
        today=date(2026, 7, 6),
        telegram_channels=(),
        per_role_limit=1,
        max_results=10,
    )

    assert vacancies == []


def test_collect_live_vacancies_does_not_limit_relevant_posts_per_channel():
    profile = CandidateProfile(raw_cv_text="Product Designer Design Systems", target_titles="Product Designer")

    def fake_text(url: str) -> str:
        channel = url.rsplit("/", 1)[-1]
        return "".join(
            f"""
            <div class="tgme_widget_message" data-post="{channel}/{index}">
              <time datetime="2026-07-03T09:00:00+00:00"></time>
              <div class="tgme_widget_message_text js-message_text">Product Designer Design Systems post {index}</div>
            </div>
            """
            for index in range(1, 6)
        )

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=lambda _url, _params: {"items": []},
        fetch_text=lambda url: "" if "linkedin.com/jobs-guest" in url else fake_text(url),
        today=date(2026, 7, 6),
        telegram_channels=("wantapply_design", "zapwork"),
        per_role_limit=0,
        max_results=20,
    )

    assert sum(1 for vacancy in vacancies if vacancy.source == "Telegram @wantapply_design") == 5
    assert sum(1 for vacancy in vacancies if vacancy.source == "Telegram @zapwork") == 5


def test_collect_live_vacancies_ranks_by_cv_match_not_source_order():
    profile = CandidateProfile(
        raw_cv_text="Lead Product Designer Automotive UX HMI Design Systems Figma English B2",
        target_titles="Lead Product Designer / Automotive UX Designer",
        experience_areas="Automotive UX; HMI; Design Systems; Figma",
    )

    def fake_text(_url: str) -> str:
        return """
        <div class="tgme_widget_message" data-post="jobs/1">
          <time datetime="2026-07-03T09:00:00+00:00"></time>
          <div class="tgme_widget_message_text js-message_text">Visual UI Designer brand layouts figma</div>
        </div>
        <div class="tgme_widget_message" data-post="jobs/2">
          <time datetime="2026-07-03T09:00:00+00:00"></time>
          <div class="tgme_widget_message_text js-message_text">Lead Product Designer Automotive UX HMI design systems Figma vehicle dashboards</div>
        </div>
        """

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=lambda _url, _params: {"items": []},
        fetch_text=lambda url: "" if "linkedin.com/jobs-guest" in url else fake_text(url),
        today=date(2026, 7, 6),
        telegram_channels=("jobs",),
        per_role_limit=0,
        max_results=3,
    )

    assert vacancies[0].title == "Lead Product Designer Automotive UX HMI design systems Figma vehicle dashboards"
    assert vacancies[0].rank == 1


def test_collect_live_vacancies_skips_irrelevant_telegram_posts():
    profile = CandidateProfile(raw_cv_text="Lead Product Designer Design Systems", target_titles="Lead Product Designer")

    def fake_text(_url: str) -> str:
        return """
        <div class="tgme_widget_message" data-post="jobs/1">
          <time datetime="2026-07-03T09:00:00+00:00"></time>
          <div class="tgme_widget_message_text js-message_text">Head of Marketing remote SaaS company</div>
        </div>
        <div class="tgme_widget_message" data-post="jobs/2">
          <time datetime="2026-07-03T09:00:00+00:00"></time>
          <div class="tgme_widget_message_text js-message_text">Senior UX/UI Designer Figma design systems</div>
        </div>
        """

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=lambda _url, _params: {"items": []},
        fetch_text=lambda url: "" if "linkedin.com/jobs-guest" in url else fake_text(url),
        today=date(2026, 7, 6),
        telegram_channels=("jobs",),
        per_role_limit=0,
        max_results=10,
    )

    telegram_titles = [vacancy.title for vacancy in vacancies if vacancy.source.startswith("Telegram")]
    assert telegram_titles == ["Senior UX/UI Designer Figma design systems"]


def test_collect_live_vacancies_has_no_default_global_limit():
    profile = CandidateProfile(raw_cv_text="Product Designer Design Systems", target_titles="Product Designer")

    def fake_text(_url: str) -> str:
        return "".join(
            f"""
            <div class="tgme_widget_message" data-post="jobs/{index}">
              <time datetime="2026-07-03T09:00:00+00:00"></time>
              <div class="tgme_widget_message_text js-message_text">Product Designer Design Systems Figma post {index}</div>
            </div>
            """
            for index in range(1, 35)
        )

    vacancies = collect_live_vacancies(
        profile,
        roles=ROLE_RECOMMENDATIONS[:1],
        fetch_json=lambda _url, _params: {"items": []},
        fetch_text=lambda url: "" if "linkedin.com/jobs-guest" in url else fake_text(url),
        today=date(2026, 7, 6),
        telegram_channels=("jobs",),
        per_role_limit=0,
    )

    assert len(vacancies) > 30
