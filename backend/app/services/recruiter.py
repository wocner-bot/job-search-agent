from dataclasses import dataclass

from app.models import CandidateProfile, Vacancy
from app.status import ApplicationStatus


@dataclass(frozen=True)
class RoleRecommendation:
    title: str
    keywords: tuple[str, ...]
    headline: str
    strategy: str
    fit_score: int
    priority: str
    language: str = "English/Russian"


ROLE_RECOMMENDATIONS: tuple[RoleRecommendation, ...] = (
    RoleRecommendation(
        "Lead Product Designer",
        ("Product Design", "UX Strategy", "Design Leadership", "Design Systems", "B2B/B2C", "Cross-functional Collaboration"),
        "Lead Product Designer — product strategy, UX systems and complex digital products",
        "Lead with 10+ years of product design, design leadership, design systems, and complex B2B/B2C product experience.",
        96,
        "Very High",
    ),
    RoleRecommendation(
        "Senior Product Designer",
        ("Product Design", "UX/UI Design", "Mobile UX", "User Flows", "Prototyping", "Product Metrics"),
        "Senior Product Designer — end-to-end UX/UI for complex products",
        "Emphasize end-to-end product design across mobile, web, dashboards, and product discovery.",
        94,
        "Very High",
    ),
    RoleRecommendation(
        "Staff Product Designer",
        ("Staff-level IC", "UX Strategy", "Design Systems", "Complex Workflows", "Mentoring", "Product Architecture"),
        "Staff Product Designer — systems thinking, product architecture and senior IC leadership",
        "Position the candidate as a senior IC who structures ambiguous product problems and raises design quality across teams.",
        93,
        "Very High",
    ),
    RoleRecommendation(
        "Principal Product Designer",
        ("Principal IC", "Product Strategy", "Enterprise UX", "Design Governance", "Information Architecture", "Stakeholder Alignment"),
        "Principal Product Designer — enterprise UX, strategy and design governance",
        "Focus on strategic design ownership, enterprise workflows, information architecture, and cross-functional alignment.",
        91,
        "Very High",
    ),
    RoleRecommendation(
        "AI Product Designer",
        ("AI UX", "Voice Assistant", "Prompts", "Intents", "Conversational Design", "Interaction Logic"),
        "AI Product Designer — conversational UX, prompts, intents and AI interaction logic",
        "Lead with ATOM voice assistant work, prompt/intent design, tone of voice, and AI-related interaction patterns.",
        95,
        "Very High",
    ),
    RoleRecommendation(
        "Automotive UX Designer",
        ("Automotive UX", "HMI", "In-vehicle UX", "Voice UX", "AVAS", "Sound Design"),
        "Automotive UX Designer — HMI, in-vehicle UX, voice and sound interaction",
        "Put ATOM automotive HMI, in-car voice assistant, sound identity, AVAS, and multimodal UX first.",
        96,
        "Very High",
    ),
    RoleRecommendation(
        "HMI UX Designer",
        ("HMI", "In-car Interaction", "CJM", "Information Architecture", "Voice Control", "Multimodal UX"),
        "HMI UX Designer — in-car interaction, multimodal UX and system logic",
        "Frame the profile around automotive human-machine interfaces, navigation logic, CJM, and interaction patterns.",
        94,
        "Very High",
    ),
    RoleRecommendation(
        "Voice UX Designer",
        ("Voice UX", "Voice Assistant", "Tone of Voice", "Prompts", "Intents", "Conversational Flows"),
        "Voice UX Designer — voice assistant scenarios, prompts and tone of voice",
        "Emphasize voice assistant scenarios, prompts, intents, tone of voice, and conversational logic.",
        94,
        "Very High",
    ),
    RoleRecommendation(
        "Conversation Designer",
        ("Conversational Design", "Prompt Writing", "Intent Design", "Dialogue Flows", "Assistant UX", "Tone of Voice"),
        "Conversation Designer — prompts, intents, dialogue flows and assistant UX",
        "Translate ATOM assistant experience into conversation design language: intents, prompts, flows, and tone.",
        92,
        "Very High",
    ),
    RoleRecommendation(
        "Design Systems Lead",
        ("Design Systems", "Components", "Governance", "UX Consistency", "DesignOps", "Reusable Patterns"),
        "Design Systems Lead — component governance, consistency and scalable product UX",
        "Use VEON/Beeline design systems and cross-team governance as the main proof point.",
        93,
        "Very High",
    ),
    RoleRecommendation(
        "UX Lead",
        ("UX Strategy", "Research", "Information Architecture", "Design Review", "Mentoring", "Cross-functional Delivery"),
        "UX Lead — UX strategy, research-informed flows and design quality",
        "Position around UX leadership, design review, research, IA, mentoring, and delivery with product and engineering.",
        90,
        "Very High",
    ),
    RoleRecommendation(
        "Head of Product Design",
        ("Design Leadership", "UX Strategy", "DesignOps", "Mentoring", "Product Vision", "Stakeholder Management"),
        "Head of Product Design — design leadership, strategy and team-level quality",
        "Show leadership through strategy, design process, mentoring, design systems, and cross-functional product delivery.",
        88,
        "High",
    ),
    RoleRecommendation(
        "Product Design Manager",
        ("Design Leadership", "Process", "Mentoring", "Design Systems", "Research", "Product Delivery"),
        "Product Design Manager — product delivery, design process and mentoring",
        "Emphasize design leadership and process ownership without inventing unconfirmed team-size or budget claims.",
        86,
        "High",
    ),
    RoleRecommendation(
        "Enterprise UX Designer",
        ("Enterprise UX", "Dashboards", "Operator Interfaces", "Complex Workflows", "B2B", "Platform UX"),
        "Enterprise UX Designer — dashboards, operator tools and complex workflows",
        "Lead with smart city dashboards, operator interfaces, telecom B2B, and enterprise workflow simplification.",
        89,
        "High",
    ),
    RoleRecommendation(
        "B2B Product Designer",
        ("B2B", "Enterprise", "Dashboards", "Platform UX", "Telecom Products", "Workflow Design"),
        "B2B Product Designer — enterprise platforms, dashboards and workflow UX",
        "Focus on VEON/Beeline B2B products, dashboards, reusable patterns, and stakeholder-heavy product work.",
        86,
        "High",
    ),
    RoleRecommendation(
        "Mobile Product Designer",
        ("Mobile UX", "iOS", "Android", "Parking Apps", "User Flows", "Product Design"),
        "Mobile Product Designer — iOS/Android flows and product UX",
        "Use parking apps, telecom/e-commerce mobile experience, and end-to-end mobile flow design.",
        84,
        "High",
    ),
    RoleRecommendation(
        "Smart City UX Designer",
        ("Smart City UX", "Transport Systems", "Traffic Control", "Parking Management", "Dashboards", "Operator UX"),
        "Smart City UX Designer — transport systems, dashboards and city-scale UX",
        "Put IT Factory smart city, transport, traffic control, parking, and operator dashboards first.",
        90,
        "Very High",
    ),
    RoleRecommendation(
        "Mobility UX Designer",
        ("Mobility UX", "Transport", "Automotive UX", "Parking", "Navigation", "City Services"),
        "Mobility UX Designer — transport, parking, automotive and navigation UX",
        "Connect automotive UX from ATOM with mobility and transport systems from IT Factory.",
        87,
        "High",
    ),
    RoleRecommendation(
        "Telecom Product Designer",
        ("Telecom Products", "B2B/B2C", "Design Systems", "UX Research", "Digital Products", "Customer Journeys"),
        "Telecom Product Designer — B2B/B2C telecom products and design systems",
        "Use VEON/Beeline as the main domain match: telecom products, research, design systems, and external team coordination.",
        86,
        "High",
    ),
    RoleRecommendation(
        "UX/UI Product Designer",
        ("UX/UI Design", "Product Design", "Figma", "Prototyping", "Visual Design", "User Flows"),
        "UX/UI Product Designer — product interfaces, prototyping and visual systems",
        "Use broad product UX/UI experience while keeping the CV senior and product-oriented rather than purely visual.",
        82,
        "High",
    ),
)


def generate_role_recommendations(profile: CandidateProfile) -> list[Vacancy]:
    profile_text = " ".join([profile.raw_cv_text, profile.target_titles, profile.experience_areas])
    rows: list[Vacancy] = []
    for index, role in enumerate(ROLE_RECOMMENDATIONS, start=1):
        rows.append(
            Vacancy(
                external_id=f"CVR-{index:02d}",
                rank=index,
                source="CV Recruiter Match",
                company="Target role",
                title=role.title,
                location="Remote / international search",
                posted="generated",
                date_status="generated from CV, not a live vacancy",
                language=role.language,
                fit_score=role.fit_score,
                priority=role.priority,
                submit_status=ApplicationStatus.DRAFT,
                next_action="Search live vacancies using these exact keywords, then verify date and source.",
                source_url=_search_url(role.title, role.keywords),
                tailored_headline=role.headline,
                top_match_keywords="; ".join(role.keywords),
                gaps_risks=_risk_note(profile_text),
                adaptation_strategy=role.strategy,
            )
        )
    return rows


def _search_url(title: str, keywords: tuple[str, ...]) -> str:
    query = "+".join([title, *keywords[:3]]).replace(" ", "+")
    return f"https://www.linkedin.com/jobs/search/?keywords={query}"


def _risk_note(profile_text: str) -> str:
    if "c1" in profile_text.lower() or "c2" in profile_text.lower():
        return "Verify language level from CV; do not inflate claims beyond confirmed evidence."
    return "English B2; verify live vacancy status, location, visa, and portfolio proof before sending."
