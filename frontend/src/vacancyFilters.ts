import type { Vacancy } from "./types";

export type WorkMode = "Remote" | "Hybrid" | "Office";

export function workModeForVacancy(vacancy: Vacancy): WorkMode {
  const text = [
    vacancy.location,
    vacancy.title,
    vacancy.description_raw,
    vacancy.requirements,
    vacancy.responsibilities,
  ].join(" ").toLowerCase();
  if (/\bhybrid\b|гибрид/.test(text)) {
    return "Hybrid";
  }
  if (/\bremote\b|fully remote|удален|удалён|на удаленке|на удалёнке/.test(text)) {
    return "Remote";
  }
  return "Office";
}

export function matchesRegion(vacancy: Vacancy, region: string): boolean {
  const query = region.trim().toLowerCase();
  if (!query) return true;
  return vacancy.location.toLowerCase().includes(query);
}
