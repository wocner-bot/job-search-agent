# Tailored CV Output Design

## Goal

Each vacancy-specific DOCX must read like a finished human CV, not an agent worksheet. It should use the vacancy language, present the candidate identity clearly, and adapt the expertise section to the vacancy requirements.

## Output Rules

- Use the candidate name parsed from the uploaded or pasted CV in the document header.
- Add a contact line under the headline with Email, LinkedIn, Portfolio, Telegram, and the phrase `Open to international and remote opportunities.`
- Keep the CV language aligned with the vacancy text language.
- Render `CORE EXPERTISE` / `КЛЮЧЕВАЯ ЭКСПЕРТИЗА` as ATS-readable tags separated by bullets, not as a bullet list.
- Prioritize vacancy-specific skills and keywords from requirements, responsibilities, source description, and match keywords.
- Remove employment dates from experience headings.
- Do not include vacancy source/link blocks, agent instructions, adaptation strategy notes, recruiter-safe notes, or placeholders in tailored CVs.

## Testing

Backend tests must verify that a generated tailored CV contains the candidate name, contact data, vacancy-relevant skill tags, and no work dates or agent-facing sections.
