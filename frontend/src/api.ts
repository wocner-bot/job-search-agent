import type { ApplicationMaterial, ApplicationStatus, CandidateReview, Vacancy, VacancyDraft } from "./types";

const rawApiBase = import.meta.env?.VITE_API_BASE ?? "";
const API_BASE = rawApiBase && !rawApiBase.startsWith("http") ? `https://${rawApiBase}` : rawApiBase;

export function apiUrl(path: string, base = API_BASE): string {
  if (!path || path.startsWith("http")) {
    return path;
  }
  if (!base) {
    return path;
  }
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || response.statusText);
  }
  return response.json() as Promise<T>;
}

async function upload<T>(path: string, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(apiUrl(path), {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; service: string }>("/api/health"),
  vacancies: () => request<Vacancy[]>("/api/vacancies"),
  createVacancy: (payload: VacancyDraft) =>
    request<Vacancy>("/api/vacancies", { method: "POST", body: JSON.stringify(payload) }),
  updateStatus: (id: number, status: ApplicationStatus) =>
    request<Vacancy>(`/api/vacancies/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    }),
  importCurrentPackage: () => request<{ imported: number }>("/api/imports/current-package", { method: "POST" }),
  createCandidateFromText: (text: string) => request("/api/candidate/text", { method: "POST", body: JSON.stringify({ text }) }),
  uploadCandidateCv: (file: File) => upload("/api/candidate/upload", file),
  updateCandidateContacts: (contacts: Record<string, string>) =>
    request("/api/candidate/contacts", { method: "POST", body: JSON.stringify(contacts) }),
  reviewCandidate: () => request<CandidateReview>("/api/candidate/review"),
  uploadVacancyFile: (file: File) => upload<{ imported: number }>("/api/imports/vacancies/upload", file),
  generateMatchesFromCv: () => request<{ generated: number; analyzed: number }>("/api/analysis/from-cv", { method: "POST" }),
  collectMatchesFromSources: () =>
    request<{ generated: number; analyzed: number; fallback: boolean }>("/api/analysis/from-sources", { method: "POST" }),
  runAnalysis: () => request<{ analyzed: number }>("/api/analysis/run", { method: "POST" }),
  materials: () => request<ApplicationMaterial[]>("/api/materials")
};
