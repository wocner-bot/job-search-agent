from dataclasses import asdict, dataclass

from app.models import CandidateProfile
from app.services.recruiter import ROLE_RECOMMENDATIONS, RoleRecommendation


@dataclass(frozen=True)
class CandidateRoleMatch:
    rank: int
    title: str
    fit_score: int
    priority: str
    headline: str
    keywords: list[str]
    strategy: str


@dataclass(frozen=True)
class CandidateReview:
    source_cv: str
    improved_cv: str
    role_matches: list[CandidateRoleMatch]


def build_candidate_review(profile: CandidateProfile) -> dict:
    review = CandidateReview(
        source_cv=profile.raw_cv_text,
        improved_cv=_improved_cv(profile),
        role_matches=[
            _role_match(index, role)
            for index, role in enumerate(ROLE_RECOMMENDATIONS, start=1)
        ],
    )
    return asdict(review)


def _role_match(rank: int, role: RoleRecommendation) -> CandidateRoleMatch:
    return CandidateRoleMatch(
        rank=rank,
        title=role.title,
        fit_score=role.fit_score,
        priority=role.priority,
        headline=role.headline,
        keywords=list(role.keywords),
        strategy=role.strategy,
    )


def _improved_cv(profile: CandidateProfile) -> str:
    name = profile.name.strip() or "Aleksandr Grenkov"
    expertise = _expertise_tags(profile)
    return "\n\n".join(
        [
            name.upper(),
            "Lead Product Designer\nAI • Automotive UX • Voice UX • Design Systems • Product Strategy",
            "Email • LinkedIn • Portfolio • Telegram • Open to international and remote opportunities.",
            "EXECUTIVE SUMMARY\n"
            "Lead Product Designer with 10+ years of experience delivering digital products across Automotive, AI, "
            "Telecom, Enterprise SaaS, Mobility and Consumer applications.\n\n"
            "Expert in transforming complex technical systems into intuitive customer experiences through Product Strategy, "
            "UX Leadership, Design Systems and Human-Centered AI.\n\n"
            "Led end-to-end product design for voice assistants, automotive HMI, enterprise platforms and consumer products "
            "while partnering with Product Managers, Engineering, AI, Research and Executive Leadership.",
            "CORE EXPERTISE\n" + " • ".join(expertise),
            "SELECTED CAREER IMPACT\n"
            "• Led UX strategy for an in-vehicle voice assistant by defining conversational architecture, prompts, intents and multimodal interaction principles.\n"
            "• Established product UX logic for automotive HMI experiences by connecting customer journeys, interface architecture and engineering constraints.\n"
            "• Scaled design-system practices across B2B and B2C products by introducing reusable patterns, design reviews and governance principles.\n"
            "• Delivered enterprise UX solutions for smart city and transportation infrastructure by simplifying operator workflows for city-scale systems.",
            "EXPERIENCE\n"
            "Lead Product Designer\nATOM, Electric Vehicle Startup\n"
            "Automotive product design, Voice UX, HMI, AI interaction and sound experience for an electric vehicle.\n"
            "Key achievements\n"
            "• Led end-to-end product design of the in-vehicle voice assistant by defining conversational architecture, prompts, intents, tone of voice and multimodal UX logic.\n"
            "• Defined UX principles for electric-vehicle HMI scenarios by connecting customer journeys, product requirements and engineering constraints into a scalable interaction system.\n"
            "• Partnered with Engineering, AI, Product and Research teams to deliver multimodal user experiences combining visual, voice and audio interaction.\n\n"
            "Product Designer\nInformation Technology Factory\n"
            "Enterprise UX for smart city, transportation, parking systems, dashboards and operator interfaces.\n"
            "Key achievements\n"
            "• Delivered city-scale operator workflows by transforming complex transportation and parking processes into clear dashboards, mobile flows and monitoring interfaces.\n"
            "• Optimized the mobile parking experience by connecting user research, information architecture, UX flows and production-ready interface solutions.\n\n"
            "Lead Product Designer\nVEON / Beeline Russia\n"
            "B2B/B2C telecom products, design systems, UX research and product design team coordination.\n"
            "Key achievements\n"
            "• Scaled product design through design-system practices, reusable UI patterns, design reviews and close partnership with product and engineering teams.\n"
            "• Transformed ambiguous telecom requirements into clear user flows, prototypes and interface solutions for complex B2B and B2C products.",
            "TOOLS\nFigma • Miro • Jira • Confluence • Prototyping • Design Systems • UX Research • Information Architecture",
            "LANGUAGES\n" + (profile.languages or "Russian native; English B2"),
        ]
    )


def _expertise_tags(profile: CandidateProfile) -> list[str]:
    tags = [
        "Product Strategy",
        "UX Strategy",
        "Product Discovery",
        "User Research",
        "Interaction Design",
        "Information Architecture",
        "Design Systems",
        "Design Leadership",
        "Cross-functional Collaboration",
        "Figma",
        "Prototyping",
    ]
    text = " ".join([profile.raw_cv_text, profile.experience_areas, profile.target_titles]).lower()
    if any(term in text for term in ("ai", "voice", "prompt", "intent", "conversation")):
        tags.extend(["AI Product Design", "Voice UX", "Conversational Design", "Intent Design", "Multimodal Interfaces"])
    if any(term in text for term in ("automotive", "hmi", "vehicle", "avas")):
        tags.extend(["Automotive UX", "HMI", "IVI", "Infotainment", "AVAS", "Mobility"])
    if any(term in text for term in ("enterprise", "saas", "dashboard", "b2b", "workflow")):
        tags.extend(["Enterprise UX", "SaaS", "Dashboard Design", "Complex Systems", "Workflow Optimization"])
    if any(term in text for term in ("smart city", "transport", "parking")):
        tags.extend(["Smart City UX", "Transport Systems", "Operator UX"])
    return list(dict.fromkeys(tags))
