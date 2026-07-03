# CV Upload Design

## Goal

Update CV intake so the user can create a candidate profile either by pasting CV text or by uploading an external CV file.

## Supported Inputs

- Pasted plain text in the existing textarea.
- Uploaded `.txt`, `.pdf`, and `.docx` files.

Legacy binary `.doc` files are out of scope for this iteration. Supporting `.doc` reliably on Render would require an additional document conversion dependency such as LibreOffice, Tika, or antiword. If a `.doc` file is uploaded, the app should return a clear unsupported-format error and ask the user to convert it to `.docx` or `.pdf`.

## Backend Behavior

The existing `/api/candidate/text` endpoint remains unchanged.

The existing `/api/candidate/upload` endpoint will be used by the frontend. It already stores the uploaded file under the configured storage directory, sanitizes the filename, extracts text via `read_cv_text`, creates a `CandidateProfile`, and returns it.

Backend improvements for this feature:

- Add or keep tests proving `.txt` upload works through the API.
- Add parser-level tests for `.docx` and `.pdf` extraction.
- Add a test proving unsupported file types return a clear `400` response.
- Avoid broad dependency changes so Render deployment stays lightweight.

## Frontend Behavior

The `CV Intake` panel should expose two input paths:

- Text mode: paste text and click `Save CV`.
- File mode: choose a `.txt`, `.pdf`, or `.docx` file and click an upload/save action.

The frontend should send file uploads using `FormData` without manually setting `Content-Type`, so the browser can set the multipart boundary.

After either path succeeds, the app shows a success message and keeps the rest of the workflow unchanged. Running analysis still uses the latest saved candidate profile.

## Error Handling

- Empty pasted text should continue to show the backend validation error.
- Missing file selection should show a lightweight UI message before making a request.
- Unsupported upload types should surface the backend error in the UI.
- Network/backend failures should show a concise message instead of silently failing.

## Testing

Backend:

- API upload success for a text file.
- API upload rejection for unsupported file type.
- Parser extraction tests for `.docx` and `.pdf`.

Frontend:

- Smoke test confirms the CV panel renders text and file upload controls.
- API helper test or smoke coverage confirms upload wiring uses the expected UI labels and does not regress existing render.

## Non-Goals

- Automatic application submission.
- Browser-side PDF/DOCX parsing.
- Legacy `.doc` conversion.
- OCR for scanned PDFs.
