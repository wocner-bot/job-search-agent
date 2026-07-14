# Job Search Agent - Project Rebuild Blueprint

Last consolidated: 2026-07-14  
Repository: `wocner-bot/job-search-agent`  
Current branch used during implementation: `codex/job-search-agent-web-app`  
Primary local project path: `/Users/r0nni/Documents/#ronni/##PORTFOLIO/Job search Agent`

This document is the single source of truth for rebuilding the project from scratch. It consolidates the chat requirements, existing Markdown specifications, operating rules from the tailored CV package, implementation details from the current codebase, Render deployment settings, and current product constraints.

## 1. Product Goal

Build a Render-deployable web application that helps Aleksandr Grenkov turn a CV into a recruiter-grade job search workspace:

1. Accept a CV as pasted text or uploaded `.txt`, `.pdf`, or `.docx`.
2. Parse the candidate profile from the CV.
3. Review and improve the source CV in an ATS/recruiter-safe format.
4. As a senior recruiter, derive 20 best-fit role directions and exact keywords as internal matching/search criteria.
5. Search relevant vacancies from live/public sources when possible.
6. Score and rank vacancies against the candidate profile.
7. Generate one tailored CV per vacancy in the same language as the vacancy.
8. Generate short platform notes, recruiter/Telegram DMs, and email cover letters.
9. Track application status manually.
10. Export a ready-to-send package.

The app prepares applications. It must not submit applications automatically.

## 2. Candidate Baseline

Candidate: Aleksandr Grenkov  
Primary positioning: Lead Product Designer with 10+ years across product design, UX strategy, design systems, automotive UX, HMI, voice UX, conversational design, smart city systems, enterprise UX, telecom, B2B/B2C, mobile UX, and design leadership.

Baseline target titles:

- Lead Product Designer
- Senior Product Designer
- Staff Product Designer
- Principal Product Designer
- AI Product Designer
- Automotive UX Designer
- HMI UX Designer
- Voice UX Designer
- Conversation Designer
- Design Systems Lead
- UX Lead
- Head of Product Design
- Product Design Manager
- Enterprise UX Designer
- B2B Product Designer
- Mobile Product Designer
- Smart City UX Designer
- Mobility UX Designer
- Telecom Product Designer
- UX/UI Product Designer

Known experience anchors:

- ATOM: lead product design for electric vehicle voice assistant, HMI, sound identity, AVAS, prompts, intents, multimodal UX.
- Information Technology Factory: smart city, transport systems, parking platforms, mobile parking apps, dashboards, operator interfaces.
- VEON / Beeline Russia: B2B/B2C telecom products, design systems, UX research, external design coordination.
- ABBYY: UI/UX for international software products including Lingvo and PDF Transformer.

Language constraints:

- Russian: native.
- English: B2.
- Do not inflate English to C1/C2 unless explicitly confirmed by the user.

Reputation-safe constraints:

- Do not invent metrics.
- Do not invent team size, budget ownership, global launch claims, conversion improvements, or ML engineering ownership.
- AI work should be framed as product/UX/prompt/intent/conversational interaction design unless ML engineering is explicitly proven.
- Applications remain prepared only until the user manually marks them sent.

## 3. Current User-Approved Workflow

The first screen is CV-first:

1. User pastes CV text or uploads CV file.
2. Optional contact fields appear if Email, LinkedIn, Portfolio, or Telegram are missing.
3. Contacts are optional and must not block vacancy search.
4. User clicks `Подобрать вакансии`.
5. App saves the candidate profile.
6. App searches concrete vacancies from sources.
7. App displays one final ranked vacancy list in a horizontally scrollable table.
8. Each row shows source, match score, priority, matched keywords, source link, and adapted CV link.
9. Each vacancy row links to a vacancy-specific tailored CV via `/api/vacancies/{id}/tailored-cv.docx`.
10. User manually opens the vacancy source, verifies details, and sends materials outside the app.

Important current override:

- Earlier docs said missing contacts should be requested before matching. The current active rule is: show the optional contact block, but never block matching because contacts are missing.

## 4. Vacancy Sources

The app should prefer concrete, source-linked vacancies over synthetic search links.

Required sources:

- LinkedIn public jobs.
- HH.ru.
- WantApply: `https://wantapply.com`.
- Telegram public channels:
  - `@wantapply_design`
  - `@young_relocate`
  - `@vdhl_good`
  - `@moskovskayarabota`
  - `@professionalsjob`
  - `@naudalenkebro`
  - `@zapwork`

Source rules:

- Do not impose arbitrary source caps that hide relevant sources.
- Ranking should be based on fit to CV and role criteria.
- Keep source groups visible so LinkedIn, HH.ru, WantApply, and Telegram do not disappear just because one source produces many high-scoring rows.
- Show the real source in the `Source` field: `LinkedIn`, `HH.ru`, `WantApply`, or `Telegram @channel`.
- Do not show `CV Recruiter Match` as a real source in the UI.
- Show the vacancy source URL as the specific vacancy/post URL whenever available.
- Generated LinkedIn search URLs are acceptable only for CV-derived role recommendations, not as live vacancy claims.
- HH.ru public access may fail or return blocked pages. If dates/status cannot be fully verified, mark the row as requiring manual verification.
- LinkedIn and Telegram public pages should be treated as source discovery; user must verify vacancy availability before applying.

Freshness rule:

- Prefer vacancies published within the last 7 days when the source provides a reliable date.
- If date cannot be verified, retain the row only with a clear `date_status`/risk note.

## 5. CV And Resume Rules

### Master/Improved CV

After CV processing, the app must show an improved ATS/recruiter-safe CV version.

Header rules:

- Header must contain the first and last name from the source CV.
- Never output `Candidate` as the displayed name if a real name can be parsed.
- Contact line should include Email, LinkedIn, Portfolio, Telegram, and `Open to international and remote opportunities.`
- Contacts are optional in the UI; if missing, placeholders can remain in the master/improved view.

Content rules:

- Do not write a biography. Write value.
- Use an executive summary that positions the candidate as senior product design talent.
- Use broad but truthful ATS keywords.
- Use Google XYZ-style bullets where possible: accomplished X, measured by Y, by doing Z.
- If no metric is verified, do not invent one.
- Use strong verbs such as `Led`, `Owned`, `Established`, `Defined`, `Delivered`, `Improved`, `Optimized`, `Reduced`, `Accelerated`, `Scaled`, `Transformed`, `Introduced`, `Directed`, `Partnered`, `Built`, `Launched`, `Enabled`.
- Avoid weak phrasing: `Worked on`, `Responsible for`, `Participated in`, `Helped`, generic `Created`, generic `Designed`, generic `Developed`.

### Tailored CV Per Vacancy

Each vacancy-specific CV must:

- Be written in the language of the vacancy.
- Be individually adapted to that vacancy.
- Use the candidate name from the uploaded/pasted CV.
- Include contact line: Email, LinkedIn, Portfolio, Telegram, open to remote/international opportunities.
- Show vacancy-matched skills.
- Render `CORE EXPERTISE` / `КЛЮЧЕВАЯ ЭКСПЕРТИЗА` as ATS-readable tags separated by bullets, not as a bullet list.
- Remove work dates from experience headings.
- Keep experience sections in a consistent format:
  - Role
  - Company
  - one-line context
  - `Key achievements`
  - strong achievement bullets
- Avoid agent-facing sections and instructions.
- Exclude `Vacancy Source` and `Vacancy Link` blocks from the CV itself.
- Exclude `Exact Match Keywords`, `Google XYZ Tailored Bullets`, `Selected Experience`, `Adaptation Strategy`, and `Recruiter-Safe Notes` as visible section titles in final tailored CVs.

Current replacement rules:

- `Exact Match Keywords` -> `Keywords` when a keyword section is needed.
- `Google XYZ Tailored Bullets` -> `Skills` when applicable.
- `Selected Experience` -> `Experience`.
- `Adaptation Strategy` -> `general`.
- `Recruiter-Safe Notes` belongs inside `general`, not as a separate section.

## 6. UI Requirements

Language:

- UI labels should be in Russian.

Layout:

- No left menu.
- Main first block: `Подбор вакансий по CV`.
- CV text and CV file upload live side by side on desktop.
- Upload and `Подобрать вакансии` button are in the same block.
- Text and upload blocks should have equal visual weight.
- `Подобрать вакансии` button uses a magic wand icon and gradient styling.
- `Choose file` / file picker button is black.
- Contacts block is optional and must not block search.
- Do not show a separate `Анализ исходного CV` / recruiter-review block.
- The vacancy table is the single final result list and must show source, match score, keywords, source link, and tailored CV link.
- Result table should have horizontal scrolling and not squeeze columns too tightly.
- `Source Text` column should be wide, roughly similar to `Company`.
- Table must show actual source in `Source`.
- Table must show source/vacancy link.
- No separate vacancy file upload in the primary flow.
- Remove the old "real vacancy block" from details.
- Filters:
  - work mode: remote / office / hybrid,
  - region text filter,
  - source filter,
  - priority filter,
  - language filter.

Visual style:

- Background: high-resolution Earth at night image using NASA Black Marble URL in CSS.
- Keep blocks aligned with consistent spacing.
- No landing page. The app opens directly into the usable workspace.
- Operational, dense, ATS/recruiting-workspace feeling rather than marketing.

## 7. Backend Architecture

Stack:

- FastAPI.
- SQLModel.
- SQLite locally.
- PostgreSQL on Render via `psycopg[binary]`.
- `python-docx` for DOCX generation and parsing.
- `pypdf` for PDF CV extraction.
- `openpyxl` for XLSX import/export.
- `python-multipart` for uploads.

Core models:

- `CandidateProfile`
  - `name`
  - `raw_cv_text`
  - `target_titles`
  - `experience_areas`
  - `languages`
  - `constraints`
- `Vacancy`
  - source, company, title, location, posted, date status, language
  - fit score, priority, status
  - source URL
  - description, requirements, responsibilities
  - vacancy keywords, top match keywords, gaps/risks, adaptation strategy
  - CV/PDF/PNG paths
- `ApplicationMaterial`
  - short note
  - recruiter/Telegram DM
  - email cover letter
  - fit summary
- `StatusEvent`
  - audit trail for manual status changes.

Statuses:

- Draft
- Ready to send
- Sent
- Follow-up
- Rejected
- Archived

Only the user can mark an application as `Sent`.

## 8. Backend Endpoints

Root and health:

- `GET /` -> JSON service entrypoint.
- `GET /api/health` -> health check.

Candidate:

- `POST /api/candidate/text`
  - payload: `{ "text": "..." }`
  - creates candidate profile from pasted CV.
- `POST /api/candidate/upload`
  - multipart `file`
  - supports `.txt`, `.pdf`, `.docx`.
  - rejects unsupported formats.
- `POST /api/candidate/contacts`
  - optional contact supplement.
  - appends `Contact details` block to latest profile.
  - must not be required for search.
- `GET /api/candidate/review`
  - returns source CV, improved CV, and 20 role matches used as recruiter guidance/search criteria.
  - UI must not present those role matches as final vacancies.
  - UI must present one final vacancy list based on `/api/vacancies`.
- `GET /api/candidate/master-cv.docx`
  - downloads recruiter-safe ATS master CV template.

Vacancies:

- `GET /api/vacancies`
- `POST /api/vacancies`
  - accepts manual vacancy fields or source URL.
  - extracts fields from URL when possible.
- `PATCH /api/vacancies/{id}/status`
  - manual status update.
- `GET /api/vacancies/{id}/tailored-cv.docx`
  - downloads vacancy-specific CV.

Imports:

- `POST /api/imports/current-package`
  - imports the local historical tailored CV package.
- `POST /api/imports/vacancies/upload`
  - imports `.csv` or `.xlsx` Application Queue files.

Analysis:

- `POST /api/analysis/run`
  - scores existing vacancies against latest candidate.
- `POST /api/analysis/from-cv`
  - creates 20 CV-derived role recommendations.
- `POST /api/analysis/from-sources`
  - collects live/public vacancies from LinkedIn, HH.ru, WantApply, Telegram channels and scores them.

Materials:

- `GET /api/materials`

Exports:

- `GET /api/exports/zip`
- `POST /api/exports/zip`

## 9. Scoring And Ranking

Deterministic scoring categories:

- Automotive.
- AI / Voice.
- Design Systems.
- Enterprise.
- Leadership.

Priority thresholds:

- `Very High`: score >= 90.
- `High`: score >= 82.
- `Medium`: score >= 70.
- `Low`: below 70.

Ranking rules:

- Score by matched title, role keywords, profile keywords, design-signal terms, source quality, and presence of actual source text.
- Penalize search-link-only rows.
- Keep source groups visible so a single source does not crowd out LinkedIn/HH.ru/Telegram/WantApply.

Risk flags to preserve:

- English level mismatch.
- Location/region/work mode mismatch.
- Hybrid/on-site mismatch.
- Visa/work authorization uncertainty.
- Date not verified.
- Source page blocked or partially parsed.
- Vacancy may be expired.
- Portfolio proof gap.
- Domain gap.

## 10. 20 Role Recommendations

The deterministic senior recruiter role list must contain exactly 20 recommendations:

1. Lead Product Designer
2. Senior Product Designer
3. Staff Product Designer
4. Principal Product Designer
5. AI Product Designer
6. Automotive UX Designer
7. HMI UX Designer
8. Voice UX Designer
9. Conversation Designer
10. Design Systems Lead
11. UX Lead
12. Head of Product Design
13. Product Design Manager
14. Enterprise UX Designer
15. B2B Product Designer
16. Mobile Product Designer
17. Smart City UX Designer
18. Mobility UX Designer
19. Telecom Product Designer
20. UX/UI Product Designer

Each role must include:

- title,
- fit score,
- priority,
- tailored headline,
- exact keywords,
- adaptation strategy.

These 20 role recommendations are search and matching criteria. They must not be shown as a competing vacancy list in the UI. The user-facing result list is the final vacancy list from `/api/vacancies`, with clickable source links and adapted CV links.

## 11. Data Import And Historical Artifacts

Historical package:

- `tailored_cv_package_with_PROJECT_MD/CODEX_PROJECT.md`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/PROJECT.md`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/application_queue_with_tailored_cv_links.xlsx`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/Tailored_CVs/`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/_batch_pdf/`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/_batch_png/`

Historical workbook columns:

- Rank
- ID
- Source
- Company
- Vacancy
- Location
- Posted
- Date Status
- Language
- Fit
- Priority
- Submit Status
- Next Action
- Tailored CV Link
- CV File Path
- Vacancy Link
- Source URL
- Tailored Headline
- Top Match Keywords
- Gaps / Risks
- Adaptation Strategy

Historical 2026-07-05 run:

- Search window: 2026-06-28 through 2026-07-05.
- Candidate focus: Lead/Senior/Staff/Principal Product Designer, AI Product Designer, Automotive UX/HMI, Voice/Conversation UX, Design Systems Lead, UX Lead.
- Source coverage in report:
  - LinkedIn: 7 rows.
  - Telegram: 27 rows.
  - HH.ru: 9 rows.
- Telegram parsed public pages for `@wantapply_design`, `@young_relocate`, `@vdhl_good`, and `@professionalsjob`.
- HH.ru API returned 403 in that run; HH rows required manual date verification.
- Applications were not sent.

Generated output artifacts may be kept for examples and regression reference, but they are not required to rebuild the app.

## 12. Frontend Architecture

Stack:

- React 18.
- TypeScript.
- Vite.
- Plain CSS.
- `lucide-react` icons.

Important files:

- `frontend/src/App.tsx`: orchestration and state.
- `frontend/src/api.ts`: API client and `apiUrl`.
- `frontend/src/types.ts`: frontend DTOs.
- `frontend/src/components/CvIntake.tsx`: CV text/file/contact/match button.
- `frontend/src/components/VacancyTable.tsx`: result table with source and CV links.
- `frontend/src/components/VacancyDetail.tsx`: detail/status/materials panel.
- `frontend/src/components/VacancyFilters.tsx`: priority/source/language/work-mode/region filters.
- `frontend/src/components/ExportBar.tsx`: master CV download.
- `frontend/src/vacancyFilters.ts`: remote/hybrid/office and region matching.
- `frontend/src/labels.ts`: Russian labels.

Frontend data flow for `Подобрать вакансии`:

1. Validate that CV text or CV file exists.
2. Save CV via `/api/candidate/text` or `/api/candidate/upload`.
3. If optional contacts were entered for a file upload, call `/api/candidate/contacts`.
4. Call `/api/analysis/from-sources`.
5. Refresh `/api/vacancies` and `/api/materials`.
6. Display message with found/analyzed counts.

If sources return no concrete vacancies, the UI says live sources did not return concrete vacancies and does not add search links as vacancies.

## 13. Local Rebuild From Scratch

### 13.1 Clone And Branch

```bash
git clone https://github.com/wocner-bot/job-search-agent.git
cd job-search-agent
git checkout codex/job-search-agent-web-app
```

If rebuilding into a new repository, copy these top-level items:

```text
README.md
render.yaml
backend/
frontend/
docs/
tailored_cv_package_with_PROJECT_MD/   # optional historical seed package
outputs/                               # optional historical run artifacts
```

### 13.2 Backend Setup

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=. .venv/bin/python -m pytest tests -q
uvicorn app.main:app --reload
```

Expected local backend:

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/api/health`
- Docs: `http://127.0.0.1:8000/docs`

### 13.3 Frontend Setup

```bash
cd frontend
npm ci
npm test
npm run build
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

Local path caveat:

- The original workspace path contains `#`.
- Vite dev transforms can be unreliable in paths with `#`.
- Current `npm run dev` builds first and serves preview to avoid that issue.
- `npm run dev:vite` is safe only in a path without `#`.

### 13.4 Environment Variables

Backend defaults:

- `APP_ENV=local`
- `DATABASE_URL=sqlite:///./storage/job_search_agent.db`
- `STORAGE_DIR=./storage`
- `CORS_ORIGINS=http://localhost:5173`

Production variables:

- `APP_ENV=production`
- `DATABASE_URL`
- `STORAGE_DIR`
- `CORS_ORIGINS`
- `VITE_API_BASE`
- optional future `OPENAI_API_KEY`

## 14. Render Deployment

Use `render.yaml` Blueprint.

Services:

- `job-search-agent-api`
  - type: web
  - runtime: Python
  - plan: free
  - rootDir: `backend`
  - build: `pip install -r requirements.txt`
  - start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - health: `/api/health`
- `job-search-agent-web`
  - type: static web service
  - rootDir: `frontend`
  - build: `npm ci && npm run build`
  - publish: `dist`
  - rewrite all routes to `/index.html`
- `job-search-agent-db`
  - PostgreSQL
  - free plan in current blueprint

Render notes:

- Free Render Postgres expires after 30 days. Use a paid plan for persistent production data.
- `VITE_API_BASE` is wired from API service external hostname.
- `CORS_ORIGINS` is wired from web service external hostname.
- `DATABASE_URL` from Render Postgres may use `postgres://` or `postgresql://`; backend normalizes to `postgresql+psycopg://`.
- `STORAGE_DIR` currently uses `/tmp/job-search-agent-storage` on Render. This is not persistent; use a disk or object storage for durable generated assets.

## 15. Verification Commands

Backend:

```bash
cd backend
PYTHONPATH=. .venv/bin/python -m pytest tests -q
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

Expected current test counts as of this consolidation:

- backend: 63 tests passing.
- frontend: smoke test passing.

## 16. Current Known Non-Goals

- No automatic application submission.
- No login-protected scraping.
- No bypassing anti-bot systems.
- No recruiter messaging from user accounts without explicit authorization.
- No account creation.
- No false `Sent` claims.
- No legacy `.doc` support.
- No OCR for scanned PDFs.
- No browser-side PDF/DOCX parsing.
- No hard dependency on LLM APIs.

## 17. Markdown Source Inventory

Core project Markdown:

```text
README.md
backend/README.md
docs/superpowers/specs/2026-07-03-cv-upload-design.md
docs/superpowers/specs/2026-07-03-job-search-agent-design.md
docs/superpowers/specs/2026-07-05-cv-first-vacancy-upload-ui-design.md
docs/superpowers/specs/2026-07-05-cv-only-recruiter-matching-design.md
docs/superpowers/specs/2026-07-09-tailored-cv-output-design.md
docs/superpowers/plans/2026-07-03-job-search-agent-web-app.md
docs/superpowers/plans/2026-07-05-cv-first-vacancy-upload-ui.md
docs/superpowers/plans/2026-07-05-cv-only-recruiter-matching.md
docs/superpowers/plans/2026-07-09-tailored-cv-output.md
tailored_cv_package_with_PROJECT_MD/CODEX_PROJECT.md
tailored_cv_package_with_PROJECT_MD/tailored_cv_package/PROJECT.md
outputs/2026-07-05-job-search-run/README_REPORT.md
```

Historical generated Markdown CV examples:

```text
outputs/2026-07-05-job-search-run/tailored_resumes_md/R01_Rivian_Sr._Lead_Product_Designer_-_Design_System_Frameworks.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R02_Tricura_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R03_Infomedije_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R04_nove8_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R05_N26_Product_Designer_-_RegTech.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R06_Zeta_Global_Senior_Product_Designer_Design_System.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R07_ООО_Либрам_Product_Designer_Urban_Tech_Smart_City_Transport_Systems.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R08_Bloomberg_Product_Designer_Design_Systems.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R09_Tangem_Head_of_Design_Art_Director.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R10_Company_Senior_Product_Designer_Dil_Mil.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R11_Bark_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R12_Capital.com_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R13_Constructor_Product_Designer_Customer_Activation.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R14_Cubic_Games_Lead_UIUX_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R15_Finom_Senior_Product_Designer_Core_Product.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R16_Infomediji_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R17_OneTwoTrip_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R18_Readymag_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R19_Social_Discovery_Group_Senior_UIUX_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R20_TaxDome_SeniorStaff_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R21_The_Open_Platform_Product_Designer_Mira.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R22_Salesforce_Product_Design_Lead_-_AI_Platform.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R23_T2._IT_и_Digital_Продуктовый_дизайнер.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R24_Checkr_Staff_Product_Designer_Growth.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R25_Company_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R26_Company_Product_Designer_Mira.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R27_GRAI_Staff_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R28_Hoodies_Senior_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R29_ООО_Дип_Диджитал_Дизайнер_дизайн-системы.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R30_ООО_МАРЧ_AI_Creator_ИИ_дизайнер_Нейродизайнер.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R31_Сравни_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R32_Pixel_Gun_2_Lead_UIUX_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R33_LionAdverts_Продуктовый_дизайнер_Middle.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R34_Free_VPN_Planet_UXUI_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R35_Muse_Group_Product_Designer_Growth.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R36_UNIS_AI_UI_UX_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R37_Figma_Product_Designer_Growth_Monetization.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R38_Company_Product_Designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R39_МТС_Дизайн_UXUI_дизайнер.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R40_ООО_ИК_СИБИНТЕК_Продуктовый_UXUI_дизайнер.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R41_ООО_ЧУБАККА_Product_UXUI_designer.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R42_Helio_Games_UXUI_Designer_Gamedev.md
outputs/2026-07-05-job-search-run/tailored_resumes_md/R43_Scorewarrior_UIUX_Designer_GamePlay.md
```

These historical generated CV Markdown files are examples of previous output format. They should not override the current tailored CV rules in this blueprint.

## 18. Rebuild Checklist

Use this checklist when rebuilding in a new environment:

- [ ] Clone repository or copy `backend`, `frontend`, `docs`, `render.yaml`, `README.md`.
- [ ] Install backend dependencies from `backend/requirements-dev.txt`.
- [ ] Run backend tests.
- [ ] Install frontend dependencies with `npm ci`.
- [ ] Run frontend smoke test.
- [ ] Run frontend build.
- [ ] Start backend and frontend locally.
- [ ] Paste or upload a CV.
- [ ] Optionally enter contacts.
- [ ] Click `Подобрать вакансии`.
- [ ] Confirm `Анализ исходного CV` does not appear.
- [ ] Confirm the single vacancy table shows source, source link, region, work mode, source text, match score, priority, and adapted CV link.
- [ ] Download at least one tailored CV and confirm language/name/contact/skills rules.
- [ ] Deploy via Render Blueprint.
- [ ] Check `/api/health`.
- [ ] Open deployed frontend and run the CV flow.
