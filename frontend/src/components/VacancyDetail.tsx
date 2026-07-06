import { apiUrl } from "../api.ts";
import { applicationStatusLabel, workModeLabel } from "../labels.ts";
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "../types";
import { workModeForVacancy } from "../vacancyFilters.ts";

const statuses: ApplicationStatus[] = ["Draft", "Ready to send", "Sent", "Follow-up", "Rejected", "Archived"];

export function VacancyDetail({
  vacancy,
  material,
  onStatusChange
}: {
  vacancy?: Vacancy;
  material?: ApplicationMaterial;
  onStatusChange: (status: ApplicationStatus) => void;
}) {
  if (!vacancy) {
    return <aside className="detail-panel">Выберите вакансию, чтобы посмотреть материалы для отправки.</aside>;
  }
  return (
    <aside className="detail-panel">
      <h2>{vacancy.company}</h2>
      <p className="muted">{vacancy.title}</p>
      <label>
        Статус
        <select value={vacancy.submit_status} onChange={(event) => onStatusChange(event.target.value as ApplicationStatus)}>
          {statuses.map((status) => <option key={status} value={status}>{applicationStatusLabel(status)}</option>)}
        </select>
      </label>
      <dl>
        <dt>Источник</dt>
        <dd>{vacancy.source}</dd>
        <dt>Формат работы</dt>
        <dd>{workModeLabel(workModeForVacancy(vacancy))}</dd>
        <dt>Регион</dt>
        <dd>{vacancy.location || "Регион пока не сохранён."}</dd>
        <dt>Ключевые слова вакансии</dt>
        <dd>{vacancy.vacancy_keywords}</dd>
        <dt>Заголовок CV</dt>
        <dd>{vacancy.tailored_headline}</dd>
        <dt>Ключевые слова</dt>
        <dd>{vacancy.top_match_keywords}</dd>
        <dt>Риски</dt>
        <dd>{vacancy.gaps_risks}</dd>
        <dt>Стратегия</dt>
        <dd>{vacancy.adaptation_strategy}</dd>
        <dt>Исходный текст вакансии</dt>
        <dd>{vacancy.description_raw || "Исходный текст пока не сохранён."}</dd>
        <dt>Требования</dt>
        <dd>{vacancy.requirements || "Требования пока не сохранены."}</dd>
        <dt>Обязанности</dt>
        <dd>{vacancy.responsibilities || "Обязанности пока не сохранены."}</dd>
      </dl>
      {vacancy.source_url && <a href={vacancy.source_url} target="_blank" rel="noreferrer">Открыть вакансию</a>}
      {vacancy.cv_file_path && <a href={apiUrl(vacancy.cv_file_path)} target="_blank" rel="noreferrer">Открыть адаптированное CV</a>}
      {material && (
        <div className="messages">
          <h3>Материалы для отправки</h3>
          <textarea readOnly value={material.short_note} />
          <textarea readOnly value={material.recruiter_dm} />
          <textarea readOnly value={material.email_cover_letter} />
        </div>
      )}
    </aside>
  );
}
