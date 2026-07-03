import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options
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
  createVacancy: (payload: { external_id: string; company: string; title: string; source?: string; source_url?: string }) =>
    request<Vacancy>("/api/vacancies", { method: "POST", body: JSON.stringify(payload) }),
  updateStatus: (id: number, status: ApplicationStatus) =>
    request<Vacancy>(`/api/vacancies/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    }),
  importCurrentPackage: () => request<{ imported: number }>("/api/imports/current-package", { method: "POST" }),
  createCandidateFromText: (text: string) => request("/api/candidate/text", { method: "POST", body: JSON.stringify({ text }) }),
  runAnalysis: () => request<{ analyzed: number }>("/api/analysis/run", { method: "POST" }),
  materials: () => request<ApplicationMaterial[]>("/api/materials")
};
