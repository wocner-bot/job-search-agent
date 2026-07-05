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
    assert any(vacancy.source_url.startswith("https://www.linkedin.com/jobs/search/") for vacancy in vacancies)
    assert any(vacancy.source_url == "https://hh.ru/vacancy/123" for vacancy in vacancies)
    assert any(vacancy.source_url == "https://t.me/wantapply_design/77" for vacancy in vacancies)
    assert all("7 days" in vacancy.date_status for vacancy in vacancies)
    assert all(vacancy.cv_file_path == "" for vacancy in vacancies)


def test_collect_live_vacancies_adds_hh_search_link_when_api_is_blocked():
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

    assert [vacancy.source for vacancy in vacancies] == ["LinkedIn", "HH.ru"]
    hh_vacancy = vacancies[1]
    assert hh_vacancy.company == "HH.ru search"
    assert hh_vacancy.source_url.startswith("https://hh.ru/search/vacancy?")
    assert hh_vacancy.date_status == "source search link for last 7 days; verify live vacancy before sending"


def test_collect_live_vacancies_keeps_multiple_telegram_channels_visible():
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
        fetch_text=fake_text,
        today=date(2026, 7, 6),
        telegram_channels=("wantapply_design", "zapwork"),
        per_role_limit=0,
        max_results=20,
    )

    assert any(vacancy.source == "Telegram @wantapply_design" for vacancy in vacancies)
    assert any(vacancy.source == "Telegram @zapwork" for vacancy in vacancies)
    assert sum(1 for vacancy in vacancies if vacancy.source == "Telegram @wantapply_design") <= 3


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
        fetch_text=fake_text,
        today=date(2026, 7, 6),
        telegram_channels=("jobs",),
        per_role_limit=0,
        max_results=10,
    )

    telegram_titles = [vacancy.title for vacancy in vacancies if vacancy.source.startswith("Telegram")]
    assert telegram_titles == ["Senior UX/UI Designer Figma design systems"]
