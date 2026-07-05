# CV-Only Recruiter Matching Design

## Goal

Make the app work from CV input alone. The primary flow is:

1. User pastes CV text or uploads `.txt`, `.pdf`, or `.docx`.
2. User clicks `Подобрать вакансии`.
3. The app acts as a senior recruiter and generates 20 best-fit target roles.
4. Each generated row contains a role title, exact matching keywords, fit score, priority, risks, adaptation strategy, and ready-to-send text.
5. Each generated row links to a role-specific tailored CV document.
6. The candidate can download a recruiter-safe master CV template for fast future adaptation.

## Senior Recruiter Rule

The matching logic must follow this instruction:

> Действуй как старший рекрутер, на основе моего резюме перечисли 20 должностей для которых я больше всего подхожу, и точные ключевые слова которые соответствуют каждой из них.

The MVP implementation is deterministic and reputation-safe. It does not claim that live LinkedIn, HH.ru, or Telegram vacancies were found unless a future authenticated/search integration verifies them.

## UX Changes

- Remove the vacancy file upload control from the first panel.
- Keep CV textarea and CV file upload.
- Keep one primary button: `Подобрать вакансии`.
- The button saves the CV and calls a CV-only matching endpoint.
- Success message should say that 20 roles were generated from the CV.

## Backend Changes

Add a recruiter service that:

- Accepts a `CandidateProfile`.
- Produces exactly 20 role recommendations.
- Uses the candidate's known strengths from the MD project context: product design, UX strategy, design systems, automotive UX, HMI, voice UX, conversational design, smart city/transport systems, enterprise UX, telecom, B2B/B2C, mobile UX, design leadership.
- Keeps English level at B2.
- Creates `Vacancy` rows with source `CV Recruiter Match`.
- Sets company to `Target role`.
- Sets `date_status` to `generated from CV, not a live vacancy`.
- Generates materials through the existing material service.
- Sets `cv_file_path` to a per-row DOCX endpoint.
- Provides a master CV template endpoint using Google XYZ bullets and red-flag guardrails.

Add `POST /api/analysis/from-cv`:

- Requires a saved candidate profile.
- Replaces current vacancies/materials with 20 CV-derived recommendations.
- Scores and materializes every generated row.
- Returns `{ "generated": 20, "analyzed": 20 }`.

## Non-Goals

- No live scraping/search in this change.
- No automatic applications.
- No claims that generated rows are active vacancies.
- No unverified metrics, inflated language levels, unsupported team-size/budget claims, or ML engineering claims in generated CV documents.
