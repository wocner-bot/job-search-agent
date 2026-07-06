import type { ApplicationStatus } from "./types.ts";
import type { WorkMode } from "./vacancyFilters.ts";

const statusLabels: Record<ApplicationStatus, string> = {
  Draft: "Черновик",
  "Ready to send": "Готово к отправке",
  Sent: "Отправлено",
  "Follow-up": "Нужен follow-up",
  Rejected: "Отказ",
  Archived: "Архив"
};

const priorityLabels: Record<string, string> = {
  "Very High": "Очень высокий",
  High: "Высокий",
  Medium: "Средний",
  Low: "Низкий"
};

const workModeLabels: Record<WorkMode, string> = {
  Remote: "Удалённо",
  Hybrid: "Гибрид",
  Office: "Офис"
};

export function applicationStatusLabel(status: ApplicationStatus | string): string {
  return statusLabels[status as ApplicationStatus] ?? status;
}

export function priorityLabel(priority: string): string {
  return priorityLabels[priority] ?? priority;
}

export function workModeLabel(mode: WorkMode | string): string {
  return workModeLabels[mode as WorkMode] ?? mode;
}
