# CV-First Vacancy Matching UI Design

## Goal

Replace the current operational dashboard-first screen with a simple CV-first flow that works on Render:

1. User provides a CV as pasted text or a file.
2. User uploads a vacancy source file.
3. User clicks `Подобрать вакансии`.
4. The app saves the candidate profile, imports vacancies, runs analysis, and shows ranked results.

## Supported Inputs

CV input:

- Pasted text.
- Uploaded `.txt`, `.pdf`, or `.docx`.

Vacancy input:

- Uploaded `.csv`.
- Uploaded `.xlsx` with an `Application Queue` sheet.

Legacy `.doc` CV files, scanned PDFs, and live job-board search are out of scope for this iteration.

## UX

The first screen should lead with one clear workflow panel:

- Title: `Подбор вакансий по CV`
- CV text area for pasted text.
- CV file picker for `.txt`, `.pdf`, `.docx`.
- Vacancy file picker for `.csv`, `.xlsx`.
- Primary button: `Подобрать вакансии`.

The old separate commands `Import Current Package`, `Run Analysis`, and `Save CV` should no longer be the main user path. They can be removed from the first screen for this iteration.

Below the workflow panel, keep the useful results workspace:

- Metrics strip.
- Vacancy table with filters.
- Vacancy details and ready-to-send materials.
- Export ZIP button.

When no vacancies are loaded, the results area should show an empty state rather than implying the app is broken.

## Backend

Keep existing endpoints:

- `POST /api/candidate/text`
- `POST /api/candidate/upload`
- `POST /api/analysis/run`
- `GET /api/vacancies`
- `GET /api/materials`

Add one Render-friendly vacancy upload endpoint:

- `POST /api/imports/vacancies/upload`

Endpoint behavior:

- Accept one uploaded file.
- Support `.csv` via existing `import_csv_rows`.
- Support `.xlsx` via existing `import_xlsx_sheet(path, "Application Queue")`.
- Normalize each row with `normalize_queue_row`.
- Insert imported vacancies into the database.
- Return `{ "imported": number }`.
- Reject unsupported file types with `400`.
- Reject blank or unreadable files with a clear `400`.

The existing `/api/imports/current-package` can remain for local testing, but the UI should use the upload endpoint.

## Frontend Data Flow

`Подобрать вакансии` should run these steps:

1. Validate that either CV text or CV file is present.
2. Validate that vacancy file is present.
3. Save CV:
   - If CV file is selected, call `POST /api/candidate/upload`.
   - Otherwise call `POST /api/candidate/text`.
4. Upload vacancies via `POST /api/imports/vacancies/upload`.
5. Run `POST /api/analysis/run`.
6. Refresh vacancies and materials.
7. Show a concise success message with imported and analyzed counts.

Use `FormData` for both file uploads. Do not set multipart `Content-Type` manually.

## Error Handling

- Missing CV input: show `Добавьте CV текстом или файлом.`
- Missing vacancy file: show `Загрузите файл с вакансиями.`
- Unsupported CV or vacancy format: show the backend error.
- Backend/API failure: show a concise visible message and keep existing inputs intact.

## Testing

Backend:

- Upload `.csv` vacancies and verify rows are imported.
- Upload `.xlsx` vacancies and verify `Application Queue` rows are imported.
- Reject unsupported vacancy upload formats.
- Keep existing candidate upload and analysis tests passing.

Frontend:

- Smoke test confirms the new Russian workflow text and `Подобрать вакансии` button render.
- API helper should support multipart vacancy upload.
- Existing build should pass for Render.

## Non-Goals

- Automatic applications to job boards.
- Live scraping/searching vacancies.
- Authentication.
- Full admin vacancy editor.
- Persistent storage of uploaded source files beyond processing.
