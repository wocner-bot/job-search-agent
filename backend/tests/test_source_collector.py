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

    assert {vacancy.source for vacancy in vacancies} == {"HH.ru", "Telegram @wantapply_design"}
    assert any(vacancy.source_url == "https://hh.ru/vacancy/123" for vacancy in vacancies)
    assert any(vacancy.source_url == "https://t.me/wantapply_design/77" for vacancy in vacancies)
    assert all(vacancy.date_status == "verified within 7 days" for vacancy in vacancies)
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

    assert len(vacancies) == 1
    assert vacancies[0].source == "HH.ru"
    assert vacancies[0].company == "HH.ru search"
    assert vacancies[0].source_url.startswith("https://hh.ru/search/vacancy?")
    assert vacancies[0].date_status == "source search link; verify live vacancy before sending"
