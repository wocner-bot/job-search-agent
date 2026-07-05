from io import BytesIO

from docx import Document
from docx.shared import Inches, Pt

from app.models import CandidateProfile, Vacancy


SAFE_ACTION_VERBS = ("Led", "Defined", "Established", "Structured", "Simplified", "Partnered", "Standardized")


def build_master_cv_document(profile: CandidateProfile) -> BytesIO:
    document = _base_document()
    _add_title(document, "ALEKSANDR GRENKOV", "ATS-OPTIMIZED MASTER CV TEMPLATE")
    document.add_heading("Contact", level=2)
    document.add_paragraph("Email | LinkedIn | Portfolio | Telegram | Location/relocation: [TARGET LOCATION]")
    document.add_heading("Target Title", level=2)
    document.add_paragraph("[TARGET ROLE] / [ROLE] at [COMPANY]")
    document.add_heading("Professional Summary", level=2)
    document.add_paragraph(
        "Lead Product Designer with 10+ years across product design, UX strategy, design systems, "
        "telecom, e-commerce, automotive UX, smart city systems, enterprise interfaces, voice UX, "
        "sound design, and AI-related interaction design. Adapt this summary with [DOMAIN KEYWORDS] "
        "and [VACANCY KEYWORDS] while keeping all claims evidence-based."
    )
    document.add_heading("Target Keywords", level=2)
    document.add_paragraph(
        "[VACANCY KEYWORDS]; [DOMAIN KEYWORDS]; Product Design; UX Strategy; UX/UI Design; "
        "Design Systems; Voice UX; Conversational Design; Automotive UX; HMI; Enterprise UX; "
        "B2B; B2C; Mobile UX; Design Leadership"
    )
    document.add_heading("Core Skills", level=2)
    document.add_paragraph(
        "Product Design; UX Strategy; Information Architecture; User Flows; Prototyping; "
        "Design Systems; Design Review; UX Research; CJM; Mobile UX; Dashboard UX; "
        "Cross-functional Collaboration; Mentoring"
    )
    document.add_heading("Domain Expertise", level=2)
    document.add_paragraph(
        "Automotive UX; HMI; In-vehicle UX; Voice Assistant UX; Sound Identity; AVAS; "
        "Smart City UX; Transport Systems; Parking Management; Telecom Products; "
        "Enterprise Platforms; B2B/B2C Digital Products"
    )
    document.add_heading("Google XYZ Bullet Formula", level=2)
    document.add_paragraph("Use: Accomplished [X], as measured by [Y], by doing [Z].")
    document.add_paragraph("If [Y] is not verified, do not invent metrics. Use truthful impact-oriented wording.")
    document.add_heading("Professional Experience", level=2)
    _add_experience_template(
        document,
        "Lead Product Designer — ATOM, Electric Vehicle Startup | 2023-2026",
        [
            "Established a scalable voice interaction framework by defining intents, prompts, tone of voice, and multimodal patterns for in-car assistant scenarios.",
            "Structured in-vehicle UX logic by mapping customer journeys, information architecture, and reusable interaction patterns for HMI scenarios.",
            "Defined product UX for sound identity, AVAS, and internal sound indication systems by partnering with engineering and research teams.",
        ],
    )
    _add_experience_template(
        document,
        "Product Designer — Information Technology Factory | 2022-2023",
        [
            "Simplified city-scale operator workflows by designing dashboards, parking apps, and transport-system interfaces for monitoring and control scenarios.",
            "Created mobile parking app experiences by translating research, user flows, and information architecture into Android and iOS interfaces.",
        ],
    )
    _add_experience_template(
        document,
        "Lead Product Designer — VEON / Beeline Russia",
        [
            "Standardized complex product interfaces by developing design-system practices, reusable UI patterns, and cross-functional design review rituals.",
            "Partnered with product, engineering, research, and external design teams to translate ambiguous requirements into clear user flows and production-ready interfaces.",
        ],
    )
    _add_experience_template(
        document,
        "Product Designer — ABBYY Software House",
        [
            "Designed UI/UX for international software products by structuring product flows and interface patterns for Lingvo and PDF Transformer scenarios.",
        ],
    )
    document.add_heading("Selected Projects", level=2)
    _add_bullets(
        document,
        [
            "In-car voice assistant and HMI interaction logic — adapt with [VACANCY KEYWORDS] for automotive, AI, voice, or HMI roles.",
            "Smart city and transport dashboards — adapt with [DOMAIN KEYWORDS] for enterprise, mobility, transport, or operator UX roles.",
            "Telecom B2B/B2C product and design-system work — adapt for design systems, platform UX, and complex product roles.",
        ],
    )
    document.add_heading("Education", level=2)
    document.add_paragraph("[EDUCATION] — keep factual, short, and ATS-readable.")
    document.add_heading("Languages", level=2)
    document.add_paragraph("Russian: native; English B2")
    document.add_heading("Tools", level=2)
    document.add_paragraph("Figma; Prototyping; Design Systems; UX Research; Information Architecture; CJM; Jira; Confluence; Adobe tools")
    document.add_heading("Red Flag Guardrails", level=2)
    _add_bullets(
        document,
        [
            "English level: English B2. Keep language claims at the verified level.",
            "Do not invent conversion, revenue, launch, budget, or team-size metrics.",
            "Do not claim ML engineering ownership; describe AI work as product, UX, prompts, intents, and interaction design.",
            "Replace weak phrasing with specific action verbs: " + ", ".join(SAFE_ACTION_VERBS) + ".",
        ],
    )
    document.add_heading("Source CV Constraints", level=2)
    document.add_paragraph(profile.constraints)
    return _save(document)


def build_tailored_cv_document(profile: CandidateProfile, vacancy: Vacancy) -> BytesIO:
    document = _base_document()
    _add_title(document, "ALEKSANDR GRENKOV", vacancy.tailored_headline or vacancy.title)
    document.add_paragraph(f"Tailored for: {vacancy.company} — {vacancy.title}")
    document.add_paragraph(f"Fit: {vacancy.fit_score} / {vacancy.priority}")
    document.add_heading("Profile", level=2)
    document.add_paragraph(
        f"Lead Product Designer aligned to {vacancy.title}, with 10+ years across product design, "
        "UX strategy, design systems, automotive UX, voice UX, smart city systems, enterprise interfaces, "
        "telecom, B2B/B2C products, and mobile UX. English B2."
    )
    document.add_heading("Exact Match Keywords", level=2)
    _add_bullets(document, _split_keywords(vacancy.top_match_keywords or vacancy.vacancy_keywords))
    if vacancy.requirements:
        document.add_heading("Vacancy Requirements Mirrored", level=2)
        _add_bullets(document, _split_keywords(vacancy.requirements))
    if vacancy.responsibilities:
        document.add_heading("Vacancy Responsibilities Mirrored", level=2)
        _add_bullets(document, _split_keywords(vacancy.responsibilities))
    document.add_heading("Google XYZ Tailored Bullets", level=2)
    _add_bullets(document, _tailored_bullets(vacancy))
    document.add_heading("Selected Experience", level=2)
    for heading, bullets in _experience_blocks(vacancy):
        paragraph = document.add_paragraph()
        paragraph.add_run(heading).bold = True
        _add_bullets(document, bullets)
    document.add_heading("Adaptation Strategy", level=2)
    document.add_paragraph(vacancy.adaptation_strategy)
    document.add_heading("Recruiter-Safe Notes", level=2)
    document.add_paragraph(vacancy.gaps_risks)
    document.add_paragraph("No unverified metrics, no inflated language claim, no engineering claim outside product/UX ownership, no application-sent claim.")
    document.add_heading("Vacancy Source", level=2)
    document.add_paragraph(f"Source: {vacancy.source or 'Manual'}")
    document.add_paragraph(f"URL: {vacancy.source_url or 'Generated target role; verify a live vacancy before sending.'}")
    if vacancy.description_raw:
        document.add_paragraph(f"Source text excerpt: {vacancy.description_raw[:1200]}")
    document.add_heading("Vacancy Link", level=2)
    document.add_paragraph(vacancy.source_url or "Generated target role; verify a live vacancy before sending.")
    return _save(document)


def _base_document() -> Document:
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)
    document.styles["Normal"].font.name = "Arial"
    document.styles["Normal"].font.size = Pt(9.5)
    return document


def _add_title(document: Document, name: str, headline: str) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run(name)
    run.bold = True
    run.font.size = Pt(16)
    subtitle = document.add_paragraph()
    subtitle.add_run(headline).bold = True
    document.add_paragraph("Email • LinkedIn • Portfolio • Telegram • Open to international and remote opportunities")


def _add_bullets(document: Document, items: list[str]) -> None:
    for item in items:
        if item.strip():
            paragraph = document.add_paragraph(style="List Bullet")
            paragraph.add_run(item.strip())


def _add_experience_template(document: Document, heading: str, bullets: list[str]) -> None:
    paragraph = document.add_paragraph()
    paragraph.add_run(heading).bold = True
    _add_bullets(document, bullets)


def _split_keywords(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def _tailored_bullets(vacancy: Vacancy) -> list[str]:
    keywords = " ".join(
        [
            vacancy.top_match_keywords,
            vacancy.vacancy_keywords,
            vacancy.description_raw,
            vacancy.requirements,
            vacancy.responsibilities,
        ]
    ).lower()
    bullets = [
        f"Established a tailored {vacancy.title} positioning by mapping the role keywords to verified product design, UX strategy, and design-system experience.",
        "Structured complex user journeys by translating product, engineering, and research inputs into information architecture, prototypes, and reusable interaction patterns.",
    ]
    if "automotive" in keywords or "hmi" in keywords or "vehicle" in keywords:
        bullets.append("Defined in-vehicle UX patterns by designing voice assistant logic, HMI scenarios, sound identity, AVAS, prompts, intents, and tone of voice.")
    if "voice" in keywords or "conversation" in keywords or "prompt" in keywords or "intent" in keywords:
        bullets.append("Established conversational UX flows by defining prompts, intents, assistant behavior, tone of voice, and multimodal interaction logic.")
    if "design systems" in keywords or "components" in keywords or "governance" in keywords:
        bullets.append("Standardized product experience by shaping reusable design-system patterns, governance practices, and cross-team design review.")
    if "smart city" in keywords or "transport" in keywords or "operator" in keywords:
        bullets.append("Simplified city-scale operational workflows by designing dashboards, transport systems, parking apps, and operator control interfaces.")
    if "telecom" in keywords or "b2b" in keywords or "b2c" in keywords:
        bullets.append("Partnered across telecom product teams by designing B2B/B2C digital products, research-informed flows, and scalable interface systems.")
    return bullets[:6]


def _experience_blocks(vacancy: Vacancy) -> list[tuple[str, list[str]]]:
    return [
        (
            "Lead Product Designer — ATOM, Electric Vehicle Startup | 2023–2026",
            [
                "Led product design for an in-car voice assistant: conversational architecture, prompts, intents, tone of voice, and multimodal UX.",
                "Defined UX logic for vehicle sound identity, AVAS, and internal sound indication systems with engineering and research teams.",
            ],
        ),
        (
            "Product Designer — Information Technology Factory | 2022–2023",
            [
                "Designed UX/UI for traffic control, speed monitoring, parking management, city dashboards, and operator interfaces.",
                "Created Android and iOS parking app experiences from research and information architecture to visual design.",
            ],
        ),
        (
            "Lead Product Designer — VEON / Beeline Russia",
            [
                "Led design for B2B/B2C telecom products, design systems, UX research, and external design team coordination.",
            ],
        ),
        (
            "Product Designer — ABBYY Software House",
            [
                "Designed UI/UX for international software products, including Lingvo and PDF Transformer.",
            ],
        ),
    ]


def _save(document: Document) -> BytesIO:
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer
