# Tailored CV Output Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each vacancy-specific DOCX show candidate contacts, vacancy-matched expertise tags, and clean experience headings without work dates.

**Architecture:** Keep the change inside the existing DOCX writer. Add small helpers for contact extraction and tag rendering, then reuse them from English and Russian tailored CV builders.

**Tech Stack:** FastAPI backend, SQLModel models, `python-docx`, pytest.

---

### Task 1: Tailored CV Regression Test

**Files:**
- Modify: `backend/tests/test_api.py`
- Test: `backend/tests/test_api.py`

- [x] **Step 1: Write the failing test**

Add an API test that creates a candidate profile with name and contacts, creates a vacancy with Automotive UX/HMI/Voice UX requirements, downloads `/api/vacancies/{id}/tailored-cv.docx`, and asserts:

```python
assert "ALEKSANDR GRENKOV" in text
assert "aleksandr@example.com" in text
assert "linkedin.com/in/aleksandr-grenkov" in text
assert "grenkov.design" in text
assert "@agrenkov" in text
assert "Open to international and remote opportunities." in text
assert core_tags.style.name != "List Bullet"
assert " • " in core_tags.text
assert "2023-2026" not in text
assert "2022-2023" not in text
```

- [x] **Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/test_api.py::test_tailored_cv_header_contacts_expertise_tags_and_no_work_dates -q
```

Expected: FAIL because the current header uses placeholder contact labels instead of parsed contact values.

### Task 2: DOCX Writer Update

**Files:**
- Modify: `backend/app/services/cv_writer.py`
- Test: `backend/tests/test_api.py`

- [ ] **Step 1: Add helper functions**

Add helpers that extract email, LinkedIn, portfolio URL, and Telegram handle from `CandidateProfile.raw_cv_text`; render the contact line; render expertise tags as a single paragraph; and keep fallback labels if a contact is missing.

- [ ] **Step 2: Update English and Russian tailored CV builders**

Pass the full `CandidateProfile` into `_add_title`, replace `_add_bullets(document, _core_expertise(...))` under expertise headings with a tag paragraph, and remove dates from experience headings returned by `_resume_experience_blocks`.

- [ ] **Step 3: Run focused test**

Run:

```bash
PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/test_api.py::test_tailored_cv_header_contacts_expertise_tags_and_no_work_dates -q
```

Expected: PASS.

### Task 3: Verification and Release

**Files:**
- Modify: `backend/app/services/cv_writer.py`
- Modify: `backend/tests/test_api.py`
- Create: `docs/superpowers/specs/2026-07-09-tailored-cv-output-design.md`
- Create: `docs/superpowers/plans/2026-07-09-tailored-cv-output.md`

- [ ] **Step 1: Run backend tests**

Run:

```bash
cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests -q
```

Expected: all tests pass.

- [ ] **Step 2: Review git diff**

Run:

```bash
git diff -- backend/app/services/cv_writer.py backend/tests/test_api.py docs/superpowers/specs/2026-07-09-tailored-cv-output-design.md docs/superpowers/plans/2026-07-09-tailored-cv-output.md
```

Expected: only tailored CV formatting, tests, and docs changed.

- [ ] **Step 3: Commit and push**

Run:

```bash
git add backend/app/services/cv_writer.py backend/tests/test_api.py docs/superpowers/specs/2026-07-09-tailored-cv-output-design.md docs/superpowers/plans/2026-07-09-tailored-cv-output.md
git commit -m "fix: format tailored CV contacts and expertise"
git push origin codex/job-search-agent-web-app
```
