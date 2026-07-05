from dataclasses import dataclass

from app.models import CandidateProfile, Vacancy


@dataclass(frozen=True)
class ScoreResult:
    fit_score: int
    priority: str
    matched_keywords: str
    gaps_risks: str
    adaptation_strategy: str
    explanation: str


KEYWORDS = {
    "Automotive": ["automotive", "hmi", "vehicle", "mobility", "in-car"],
    "AI / Voice": ["ai", "voice", "assistant", "agent", "conversational", "prompt", "intent"],
    "Design Systems": ["design system", "tokens", "components", "governance"],
    "Enterprise": ["enterprise", "b2b", "dashboard", "operator", "platform"],
    "Leadership": ["lead", "staff", "principal", "head", "mentor", "strategy"],
}


def priority_for_score(score: int) -> str:
    if score >= 90:
        return "Very High"
    if score >= 82:
        return "High"
    if score >= 70:
        return "Medium"
    return "Low"


def score_vacancy(profile: CandidateProfile, vacancy: Vacancy) -> ScoreResult:
    haystack = " ".join(
        [
            profile.target_titles,
            profile.experience_areas,
            vacancy.title,
            vacancy.description_raw,
            vacancy.requirements,
            vacancy.responsibilities,
            vacancy.vacancy_keywords,
            vacancy.top_match_keywords,
            vacancy.tailored_headline,
            vacancy.adaptation_strategy,
        ]
    ).lower()
    matched_categories: list[str] = []
    raw_score = 55
    for category, terms in KEYWORDS.items():
        if any(term in haystack for term in terms):
            matched_categories.append(category)
            raw_score += 8
    if "lead" in vacancy.title.lower() or "staff" in vacancy.title.lower():
        raw_score += 5
    if vacancy.language and "english" in vacancy.language.lower() and "English B2" in profile.languages:
        raw_score += 3
    score = min(100, max(0, raw_score))
    matched_parts = matched_categories[:]
    if vacancy.vacancy_keywords:
        matched_parts.extend(keyword.strip() for keyword in vacancy.vacancy_keywords.split(";") if keyword.strip())
    matched = "; ".join(dict.fromkeys(matched_parts))
    gaps = vacancy.gaps_risks or "Verify live vacancy status and add true metrics before sending."
    strategy = vacancy.adaptation_strategy or f"Adapt CV to {vacancy.title}: mirror {matched or 'Product Design'} keywords, use vacancy language, and keep claims factual."
    return ScoreResult(
        fit_score=score,
        priority=priority_for_score(score),
        matched_keywords=matched,
        gaps_risks=gaps,
        adaptation_strategy=strategy,
        explanation=f"Score combines title seniority, language fit, and matched categories: {matched or 'none'}.",
    )
