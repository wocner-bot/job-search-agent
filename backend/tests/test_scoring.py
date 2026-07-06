from app.models import CandidateProfile, Vacancy
from app.services.materials import generate_materials
from app.services.scoring import score_vacancy
from app.status import ApplicationStatus


def test_score_is_bounded_and_explainable():
    profile = CandidateProfile(
        target_titles="Lead Product Designer / AI Product Designer",
        experience_areas="Automotive UX; Voice UX; Design Systems; Enterprise UX",
        languages="Russian native; English B2",
    )
    vacancy = Vacancy(
        external_id="L08",
        company="42dot",
        title="Lead Brand / UI Designer - Automotive",
        language="English",
        top_match_keywords="Automotive; HMI; Design Systems",
    )
    result = score_vacancy(profile, vacancy)
    assert 0 <= result.fit_score <= 100
    assert result.priority in {"Very High", "High", "Medium", "Low"}
    assert "Automotive" in result.matched_keywords
    assert result.explanation


def test_score_does_not_inherit_candidate_keywords_for_irrelevant_vacancy():
    profile = CandidateProfile(
        target_titles="Lead Product Designer / AI Product Designer",
        experience_areas="Automotive UX; Voice UX; Design Systems; Enterprise UX",
        languages="Russian native; English B2",
    )
    vacancy = Vacancy(
        external_id="HH-134738517",
        company="ADB",
        title="OPERATIONAL ASSISTANT (ADB)",
        language="English",
        description_raw=(
            "Support routine processing requirements, prepare documentation, maintain client database, "
            "coordinate office administration, translate short documents and arrange meetings."
        ),
        source_url="https://hh.ru/vacancy/134738517",
    )

    result = score_vacancy(profile, vacancy)

    assert result.priority == "Low"
    assert result.fit_score < 70
    assert "Automotive" not in result.matched_keywords
    assert "Design Systems" not in result.matched_keywords


def test_generate_materials_does_not_mark_sent():
    profile = CandidateProfile(name="Aleksandr Grenkov", target_titles="Lead Product Designer")
    vacancy = Vacancy(
        id=1,
        external_id="L08",
        company="42dot",
        title="Lead Brand / UI Designer - Automotive",
        language="English",
        fit_score=96,
        priority="Very High",
        tailored_headline="Lead Product Designer - Automotive UX",
        submit_status=ApplicationStatus.DRAFT,
    )
    material = generate_materials(profile, vacancy)
    assert material.vacancy_id == 1
    assert "42dot" in material.short_note
    assert vacancy.submit_status == ApplicationStatus.DRAFT
