# CV-Only Recruiter Matching Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CV-only matching flow that generates 20 senior-recruiter target roles and keywords without requiring a vacancy file.

**Architecture:** Add a deterministic recruiter service in the backend, expose it via `POST /api/analysis/from-cv`, and update the React CV intake panel to call that endpoint after CV save/upload. Existing scoring, materials, vacancy table, detail panel, and exports remain in use.

**Tech Stack:** FastAPI, SQLModel, pytest, React, TypeScript, Vite.

---

### Task 1: Backend Recruiter Generation

**Files:**
- Create: `backend/app/services/recruiter.py`
- Modify: `backend/app/api/routes.py`
- Test: `backend/tests/test_api.py`

- [ ] Write failing tests for `POST /api/analysis/from-cv`: it must require a candidate and generate exactly 20 `CV Recruiter Match` rows with role titles and keyword strings.
- [ ] Implement `generate_role_recommendations(profile)` with 20 deterministic role definitions.
- [ ] Implement `POST /api/analysis/from-cv`, replacing existing vacancies/materials and generating ready-to-send materials.
- [ ] Run backend tests and keep all green.

### Task 2: Frontend CV-Only Flow

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/api.ts`
- Modify: `frontend/src/components/CvIntake.tsx`
- Modify: `frontend/src/__tests__/App.test.tsx`

- [ ] Write/update smoke test so it expects no `Файл с вакансиями` text.
- [ ] Remove vacancy file state and props from `App.tsx` and `CvIntake.tsx`.
- [ ] Add `api.generateMatchesFromCv()` calling `POST /api/analysis/from-cv`.
- [ ] Update success message to report generated/analyzed count.
- [ ] Run frontend build.

### Task 3: Verification and Deploy

**Files:**
- Modify: `backend/.render-deploy`
- Modify: `frontend/.render-deploy`

- [ ] Run backend tests.
- [ ] Run frontend build.
- [ ] Commit and push to `origin codex/job-search-agent-web-app`.
- [ ] Verify Render API health and deployed UI.
