# CV-First Vacancy Upload UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Render-friendly flow where the user uploads or pastes a CV, uploads a vacancy file, clicks `Подобрать вакансии`, and sees ranked results.

**Architecture:** Add a backend vacancy upload endpoint that reuses existing CSV/XLSX import and vacancy normalization services. Replace the current command-first frontend panel with a focused matching form that orchestrates CV save, vacancy import, analysis, and refresh.

**Tech Stack:** FastAPI, SQLModel, openpyxl, React, TypeScript, Vite, plain CSS, pytest, existing smoke test.

---

## File Structure

- `backend/app/api/routes.py`: add `POST /api/imports/vacancies/upload` and small import helpers.
- `backend/tests/test_api.py`: add API tests for CSV vacancy upload and unsupported format rejection.
- `backend/tests/test_importer.py`: keep existing parser tests; no new importer service is needed unless route logic grows.
- `frontend/src/api.ts`: add multipart helpers for CV upload and vacancy upload.
- `frontend/src/components/CvIntake.tsx`: replace save-only CV panel with the CV-first matching form.
- `frontend/src/App.tsx`: replace separate import/analyze/save handlers with one `matchVacancies` orchestration handler.
- `frontend/src/components/ImportPanel.tsx`: no longer used by `App`; leave in repo unless cleanup is requested.
- `frontend/src/__tests__/App.test.tsx`: update smoke assertions to new Russian workflow.
- `frontend/src/styles.css`: add compact form styling for file inputs, helper text, and primary action.

---

### Task 1: Backend Vacancy Upload Endpoint

**Files:**
- Modify: `backend/tests/test_api.py`
- Modify: `backend/app/api/routes.py`

- [ ] **Step 1: Write the failing CSV upload API test**

Add this test to `backend/tests/test_api.py`:

```python
def test_upload_vacancy_file_imports_csv_rows():
    reset_database()
    csv_bytes = (
        "Rank,ID,Source,Company,Vacancy,Location,Posted,Date Status,Language,Fit,Priority,Submit Status,Next Action,CV File Path,Source URL,Tailored Headline,Top Match Keywords,Gaps / Risks,Adaptation Strategy\n"
        "1,L08,LinkedIn,42dot,Lead Brand / UI Designer - Automotive,Remote,2 days ago,verified,English,96,Very High,Ready to submit manually,Submit manually,Tailored_CVs/08.docx,https://example.com/42dot,Lead Product Designer,Automotive; HMI,US location risk,Lead with ATOM\n"
        "2,L04,LinkedIn,ZOE,Lead Product Designer - Design System,Remote,4 days ago,verified,English,95,Very High,Ready to submit manually,Submit manually,Tailored_CVs/04.docx,https://example.com/zoe,Design Systems Lead,Design systems,Need token examples,Lead with systems\n"
    ).encode("utf-8")
    with TestClient(app) as client:
        response = client.post(
            "/api/imports/vacancies/upload",
            files={"file": ("vacancies.csv", csv_bytes, "text/csv")},
        )
        assert response.status_code == 200
        assert response.json() == {"imported": 2}

        vacancies_response = client.get("/api/vacancies")
        assert vacancies_response.status_code == 200
        rows = vacancies_response.json()
        assert [row["company"] for row in rows] == ["42dot", "ZOE"]
        assert rows[0]["source_url"] == "https://example.com/42dot"
```

- [ ] **Step 2: Write the failing unsupported format test**

Add this test to `backend/tests/test_api.py`:

```python
def test_upload_vacancy_file_rejects_unsupported_format():
    reset_database()
    with TestClient(app) as client:
        response = client.post(
            "/api/imports/vacancies/upload",
            files={"file": ("vacancies.json", b"{}", "application/json")},
        )
        assert response.status_code == 400
        assert "Unsupported vacancy file type" in response.json()["detail"]
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_api.py::test_upload_vacancy_file_imports_csv_rows tests/test_api.py::test_upload_vacancy_file_rejects_unsupported_format -q
```

Expected: both tests fail with `404 Not Found` because the endpoint does not exist.

- [ ] **Step 4: Implement the endpoint**

In `backend/app/api/routes.py`, update imports:

```python
from app.services.importer import import_csv_rows, import_xlsx_sheet, normalize_queue_row
```

Add this route after `import_current_package`:

```python
@router.post("/imports/vacancies/upload")
async def import_uploaded_vacancies(file: UploadFile = File(...), session: Session = Depends(get_session)) -> dict[str, int]:
    settings = get_settings()
    upload_dir = settings.storage_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(file.filename or "vacancies.csv").name
    path = upload_dir / filename
    path.write_bytes(await file.read())

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            rows = import_csv_rows(path)
        elif suffix == ".xlsx":
            rows = import_xlsx_sheet(path, "Application Queue")
        else:
            raise ValueError("Unsupported vacancy file type. Use .csv or .xlsx.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not rows:
        raise HTTPException(status_code=400, detail="Vacancy file does not contain any rows.")

    count = 0
    for row in rows:
        session.add(normalize_queue_row(row, path.parent))
        count += 1
    session.commit()
    return {"imported": count}
```

- [ ] **Step 5: Run backend tests**

Run:

```bash
cd backend
. .venv/bin/activate
pytest tests/test_api.py::test_upload_vacancy_file_imports_csv_rows tests/test_api.py::test_upload_vacancy_file_rejects_unsupported_format -q
pytest -q
```

Expected: targeted tests pass, then full backend test suite passes.

- [ ] **Step 6: Commit backend upload endpoint**

Run:

```bash
git add backend/app/api/routes.py backend/tests/test_api.py
git commit -m "feat: upload vacancy source files"
```

---

### Task 2: Frontend API Multipart Helpers

**Files:**
- Modify: `frontend/src/api.ts`

- [ ] **Step 1: Update API helpers**

In `frontend/src/api.ts`, add a multipart helper below `request`:

```ts
async function upload<T>(path: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || response.statusText);
  }
  return response.json() as Promise<T>;
}
```

Add these methods to `api`:

```ts
uploadCandidateCv: (file: File) => upload("/api/candidate/upload", file),
uploadVacancyFile: (file: File) => upload<{ imported: number }>("/api/imports/vacancies/upload", file),
```

- [ ] **Step 2: Run frontend smoke test**

Run:

```bash
cd frontend
npm test
```

Expected: existing smoke test still passes until UI text changes in Task 3.

---

### Task 3: CV-First Matching Form

**Files:**
- Modify: `frontend/src/components/CvIntake.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/__tests__/App.test.tsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Write failing frontend smoke assertions**

Replace `frontend/src/__tests__/App.test.tsx` assertions with:

```ts
assert.match(html, /Job Search Agent/);
assert.match(html, /Подбор вакансий по CV/);
assert.match(html, /Вставьте CV текстом/);
assert.match(html, /Файл с вакансиями/);
assert.match(html, /Подобрать вакансии/);
```

- [ ] **Step 2: Run frontend test to verify failure**

Run:

```bash
cd frontend
npm test
```

Expected: fails because the new Russian UI labels are not rendered yet.

- [ ] **Step 3: Replace `CvIntake` props and markup**

Replace `frontend/src/components/CvIntake.tsx` with:

```tsx
import { BriefcaseBusiness, FileText, Sparkles, Upload } from "lucide-react";

type CvIntakeProps = {
  cvText: string;
  cvFileName: string;
  vacancyFileName: string;
  isMatching: boolean;
  onCvTextChange: (value: string) => void;
  onCvFileChange: (file: File | null) => void;
  onVacancyFileChange: (file: File | null) => void;
  onMatch: () => void;
};

export function CvIntake({
  cvText,
  cvFileName,
  vacancyFileName,
  isMatching,
  onCvTextChange,
  onCvFileChange,
  onVacancyFileChange,
  onMatch
}: CvIntakeProps) {
  return (
    <section id="cv" className="panel match-panel">
      <div className="match-copy">
        <h1>Подбор вакансий по CV</h1>
        <p>Загрузите CV и файл с вакансиями, чтобы получить ранжированный список и ready-to-send материалы.</p>
      </div>
      <label className="field-block">
        <span>
          <FileText size={16} aria-hidden="true" /> Вставьте CV текстом
        </span>
        <textarea
          value={cvText}
          onChange={(event) => onCvTextChange(event.target.value)}
          placeholder="Вставьте сюда CV, если не хотите загружать файл"
        />
      </label>
      <div className="upload-grid">
        <label className="upload-box">
          <span>
            <Upload size={16} aria-hidden="true" /> CV файлом
          </span>
          <input type="file" accept=".txt,.pdf,.docx" onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)} />
          <strong>{cvFileName || "PDF, DOCX или TXT"}</strong>
        </label>
        <label className="upload-box">
          <span>
            <BriefcaseBusiness size={16} aria-hidden="true" /> Файл с вакансиями
          </span>
          <input type="file" accept=".csv,.xlsx" onChange={(event) => onVacancyFileChange(event.target.files?.[0] ?? null)} />
          <strong>{vacancyFileName || "CSV или XLSX"}</strong>
        </label>
      </div>
      <button className="primary-action" type="button" onClick={onMatch} disabled={isMatching}>
        <Sparkles size={18} aria-hidden="true" /> {isMatching ? "Подбираю..." : "Подобрать вакансии"}
      </button>
    </section>
  );
}
```

- [ ] **Step 4: Update `App` orchestration**

In `frontend/src/App.tsx`, remove `ImportPanel` import/use. Add state:

```ts
const [cvFile, setCvFile] = useState<File | null>(null);
const [vacancyFile, setVacancyFile] = useState<File | null>(null);
const [isMatching, setIsMatching] = useState(false);
```

Replace `saveCv`, `importPackage`, and `runAnalysis` with:

```ts
async function matchVacancies() {
  if (!cvText.trim() && !cvFile) {
    setMessage("Добавьте CV текстом или файлом.");
    return;
  }
  if (!vacancyFile) {
    setMessage("Загрузите файл с вакансиями.");
    return;
  }
  setIsMatching(true);
  setMessage("Подбираю вакансии...");
  try {
    if (cvFile) {
      await api.uploadCandidateCv(cvFile);
    } else {
      await api.createCandidateFromText(cvText);
    }
    const imported = await api.uploadVacancyFile(vacancyFile);
    const analyzed = await api.runAnalysis();
    await refresh();
    setMessage(`Готово: импортировано ${imported.imported}, проанализировано ${analyzed.analyzed}.`);
  } catch (error) {
    setMessage(error instanceof Error ? error.message : "Не удалось подобрать вакансии.");
  } finally {
    setIsMatching(false);
  }
}
```

Render `CvIntake` like this:

```tsx
<CvIntake
  cvText={cvText}
  cvFileName={cvFile?.name ?? ""}
  vacancyFileName={vacancyFile?.name ?? ""}
  isMatching={isMatching}
  onCvTextChange={setCvText}
  onCvFileChange={setCvFile}
  onVacancyFileChange={setVacancyFile}
  onMatch={matchVacancies}
/>
```

- [ ] **Step 5: Add CSS**

Append to `frontend/src/styles.css`:

```css
.match-panel {
  display: grid;
  gap: 16px;
}

.match-copy h1 {
  margin: 0;
  font-size: 28px;
}

.match-copy p {
  margin: 6px 0 0;
  color: #5d6b7a;
}

.field-block,
.upload-box {
  display: grid;
  gap: 8px;
}

.field-block span,
.upload-box span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
}

.upload-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.upload-box {
  border: 1px solid #c7d0da;
  border-radius: 8px;
  padding: 14px;
  background: #f8fafc;
}

.upload-box input {
  max-width: 100%;
}

.upload-box strong {
  color: #5d6b7a;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.primary-action {
  justify-content: center;
  background: #17202a;
  color: #ffffff;
  border-color: #17202a;
  min-height: 44px;
  font-weight: 700;
}

.primary-action:disabled {
  cursor: wait;
  opacity: 0.72;
}

@media (max-width: 760px) {
  .upload-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 6: Run frontend test and build**

Run:

```bash
cd frontend
npm test
npm run build
```

Expected: smoke test and production build pass.

- [ ] **Step 7: Commit frontend workflow**

Run:

```bash
git add frontend/src/App.tsx frontend/src/api.ts frontend/src/components/CvIntake.tsx frontend/src/__tests__/App.test.tsx frontend/src/styles.css
git commit -m "feat: add CV-first vacancy matching flow"
```

---

### Task 4: End-to-End Verification and Deploy Push

**Files:**
- No source changes expected unless verification finds a bug.

- [ ] **Step 1: Run all verification**

Run:

```bash
cd backend
. .venv/bin/activate
pytest -q
cd ../frontend
npm test
npm run build
```

Expected: backend tests, frontend smoke test, and frontend build all pass.

- [ ] **Step 2: Start local services and verify UI manually**

Run backend if not already running:

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run frontend:

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173/`. Verify the first panel shows `Подбор вакансий по CV`, both file inputs, and `Подобрать вакансии`.

- [ ] **Step 3: Push to GitHub**

Run:

```bash
git push
```

Expected: Render auto-deploys the updated branch `codex/job-search-agent-web-app`.

---

## Self-Review

- Spec coverage: CV text/file input, vacancy file upload, one matching button, results workspace, backend upload endpoint, FormData uploads, and Render build are all covered.
- Placeholder scan: no TBD/TODO placeholders are present.
- Type consistency: frontend API methods use `File`, backend endpoint returns `{ imported: number }`, and `App` orchestration expects the same shape.
