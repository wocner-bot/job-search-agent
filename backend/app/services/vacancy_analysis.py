from __future__ import annotations


KEYWORD_MAP: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Product Design", ("product designer", "product design", "продуктовый дизайнер")),
    ("UX Strategy", ("ux strategy", "strategy", "стратег")),
    ("UX/UI", ("ux/ui", "ui/ux", "user interface", "interface")),
    ("Design Systems", ("design system", "design systems", "component", "components", "tokens", "governance", "дизайн-систем")),
    ("Automotive UX", ("automotive", "vehicle", "mobility", "in-car", "автом")),
    ("HMI", ("hmi", "human machine interface")),
    ("Voice UX", ("voice", "assistant", "tone of voice", "голос")),
    ("Conversational Design", ("conversation", "conversational", "dialogue", "prompt", "intent")),
    ("AI UX", ("ai", "llm", "agent", "ии", "нейро")),
    ("Enterprise UX", ("enterprise", "platform", "dashboard", "operator", "b2b")),
    ("Smart City", ("smart city", "traffic", "parking", "transport", "город", "парков")),
    ("Telecom", ("telecom", "telco", "мтс", "beeline", "t2")),
    ("Mobile UX", ("mobile", "ios", "android", "app", "мобиль")),
    ("Figma", ("figma",)),
    ("Research", ("research", "user research", "ux research", "исслед")),
    ("Prototyping", ("prototype", "prototyping", "прототип")),
    ("Leadership", ("lead", "head", "staff", "principal", "mentor", "руковод")),
    ("Component Governance", ("component governance", "governance", "library", "framework")),
)


def extract_vacancy_keywords(*parts: str) -> str:
    haystack = " ".join(part for part in parts if part).lower()
    matched: list[str] = []
    for label, terms in KEYWORD_MAP:
        if any(term in haystack for term in terms):
            matched.append(label)
    return "; ".join(matched[:12])


def infer_vacancy_language(text: str) -> str:
    cyrillic = sum(1 for char in text if "а" <= char.lower() <= "я" or char.lower() == "ё")
    latin = sum(1 for char in text if "a" <= char.lower() <= "z")
    if cyrillic > latin * 0.35:
        return "Russian"
    return "English"
