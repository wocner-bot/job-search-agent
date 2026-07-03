# Job Search Agent Web App Design

Date: 2026-07-03
Owner: Aleksandr Grenkov
Status: Approved MVP direction, pending implementation plan

## Purpose

Build a web application that turns a candidate CV and a vacancy queue into a ready-to-send job application workspace. The app does not submit applications automatically in the MVP. It prepares relevant tailored materials and leaves final submission to the user.

The initial dataset comes from the existing tailored CV package in this project folder:

- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/application_queue_with_tailored_cv_links.xlsx`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/Tailored_CVs/`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/_batch_pdf/`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/_batch_png/`
- `tailored_cv_package_with_PROJECT_MD/tailored_cv_package/cv_links_index.html`

## MVP Scope

The MVP supports this workflow:

1. User uploads or pastes a master CV.
2. The app extracts a candidate profile from the CV.
3. The app imports vacancy data from the existing Excel workbook or a compatible CSV.
4. User can manually add or edit vacancies.
5. The app scores each vacancy against the candidate profile.
6. The app creates ready-to-send materials:
   - tailored headline
   - fit summary
   - matched keywords
   - gaps and risks
   - adaptation strategy
   - short platform note
   - recruiter or Telegram DM
   - email cover letter
   - links to tailored CV assets when available
7. User tracks each opportunity through manual statuses.
8. User exports the application queue and prepared package.

Out of scope for the MVP:

- Automated submission to LinkedIn, HH.ru, Telegram, or email.
- Scraping logged-in job platforms.
- Browser automation for applications.
- Claims that an application was sent unless the user manually marks it as sent.

## Product Structure

### CV Intake

The CV intake screen accepts pasted text and uploaded files. For MVP, supported uploads should prioritize `.txt`, `.pdf`, and `.docx`. The backend extracts text and stores a normalized candidate profile with role focus, experience areas, languages, recent roles, and constraints.

The existing candidate baseline must be preserved:

- Aleksandr Grenkov
- Lead Product Designer / AI Product Designer / Automotive UX Designer / Voice UX Designer / Design Systems Lead
- Russian native
- English B2

The system must not inflate language level, metrics, titles, or submission status.

### Vacancy Queue

The queue screen imports rows from the current workbook and supports CSV import with the same logical fields. It also supports manual vacancy creation.

Core vacancy fields:

- rank
- id
- source
- company
- vacancy title
- location
- posted
- date status
- language
- fit
- priority
- submit status
- next action
- CV file path
- source URL
- tailored headline
- top match keywords
- gaps / risks
- adaptation strategy

The app should generate clickable UI links from `CV File Path` and `Source URL`. The current workbook has empty `Tailored CV Link` and `Vacancy Link` columns, so those columns must not be treated as the source of truth.

### Analysis Engine

The backend compares the candidate profile with each vacancy and produces:

- `fit_score` from 0 to 100
- `priority` as Very High, High, Medium, or Low
- matched keywords
- missing or weak signals
- risks
- adaptation strategy
- recommended tailored headline

The MVP can begin with deterministic scoring plus optional LLM assistance. The score should be explainable from stored signals, not just a black-box number.

### Ready-To-Send Package

For each vacancy, the app prepares:

- short platform note
- recruiter / Telegram DM
- email cover letter
- recommended CV asset link
- optional generated tailored CV draft

The package remains `Ready to send` until the user manually changes status.

### Manual Submission Board

Statuses:

- Draft
- Ready to send
- Sent
- Follow-up
- Rejected
- Archived

Only the user can mark an item as `Sent` in the MVP.

### Exports

MVP exports:

- CSV application queue
- XLSX application queue
- HTML index with CV and vacancy links
- ZIP package with selected ready-to-send materials

## Technical Architecture

Use a React + FastAPI architecture.

### Frontend

Use React with Vite. The frontend is responsible for:

- dashboard layout
- queue table and filters
- vacancy detail panel
- CV intake form
- import screens
- ready-to-send message previews
- status updates
- export actions

The UI should be operational and dense, closer to a recruiting/ATS workspace than a marketing page.

### Backend

Use FastAPI. The backend is responsible for:

- CV text extraction
- Excel/CSV import
- data validation and normalization
- vacancy scoring
- LLM prompt orchestration when enabled
- document/package export
- file serving for generated and imported assets

### Database

Use SQLite for local development and PostgreSQL on Render.

Core entities:

- candidate_profiles
- vacancies
- application_materials
- asset_files
- status_events
- imports

### Storage

Use local `storage/` for development. On Render MVP, use a Render persistent disk. Later versions can move assets to S3-compatible storage such as Cloudflare R2.

### Deployment

Render deployment should support:

- backend FastAPI web service
- frontend static site or web service
- PostgreSQL database
- persistent disk for uploaded/generated assets
- environment variables:
  - `DATABASE_URL`
  - `OPENAI_API_KEY`
  - `STORAGE_DIR`
  - `CORS_ORIGINS`
  - `APP_ENV`

Include `render.yaml` so the app can be deployed reproducibly.

## Data Migration From Current Package

The importer should read `Application Queue`, `CV Index`, `Tailored Messages`, and `Operating Rules` from the current workbook.

Observed current dataset:

- 26 vacancies
- 7 Very High, 12 High, 7 Medium
- sources include LinkedIn, Telegram, HH.ru, and mixed sources
- all current submit statuses are `Ready to submit manually`
- all 26 DOCX files have matching PDF and PNG preview files

The import should preserve source URLs, file paths, priority, fit, language, and prepared messages.

## Error Handling

The app should handle:

- unsupported CV file type
- failed text extraction
- invalid spreadsheet format
- missing CV/PDF/PNG asset
- missing source URL
- LLM failure or timeout
- export failure

Failures should be visible per vacancy where possible, so one bad row does not block the whole queue.

## Testing

Backend tests:

- import current workbook
- normalize vacancy rows
- verify all expected current assets exist
- scoring returns bounded explainable values
- statuses cannot become `Sent` through automated generation
- export creates valid CSV/XLSX/HTML package

Frontend tests:

- queue renders imported rows
- filters by priority, source, language, and status
- vacancy detail shows generated materials
- manual status changes work
- CV intake handles pasted text and upload states

Integration smoke test:

- import the current package
- show 26 vacancies
- open one vacancy detail
- generate or display ready-to-send materials
- export queue

## Implementation Notes

Start with the imported current package as seed data. Do not build automated job search in the first version. Keep the architecture open for future job-source integrations, but make the first release excellent at turning known vacancies into a ready-to-send application board.
