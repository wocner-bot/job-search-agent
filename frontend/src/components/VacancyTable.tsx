import { apiUrl } from "../api.ts";
import { applicationStatusLabel, priorityLabel, workModeLabel } from "../labels.ts";
import type { Vacancy } from "../types";
import { workModeForVacancy } from "../vacancyFilters.ts";

function sourceTextPreview(vacancy: Vacancy): string {
  const sourceText = vacancy.description_raw || vacancy.requirements || vacancy.responsibilities || vacancy.source_url;
  if (!sourceText) return "";
  return sourceText.length > 120 ? `${sourceText.slice(0, 117)}...` : sourceText;
}

export function VacancyTable({ vacancies, selectedId, onSelect }: { vacancies: Vacancy[]; selectedId?: number; onSelect: (vacancy: Vacancy) => void }) {
  return (
    <table className="queue-table">
      <thead>
        <tr>
          <th>№</th>
          <th>Источник</th>
          <th>Ссылка на вакансию</th>
          <th>Исходный текст</th>
          <th>Формат работы</th>
          <th>Регион</th>
          <th>Компания</th>
          <th>Вакансия</th>
          <th>Совпадение</th>
          <th>Приоритет</th>
          <th>Статус</th>
          <th>Адаптированное CV</th>
        </tr>
      </thead>
      <tbody>
        {vacancies.map((vacancy) => (
          <tr key={vacancy.id} className={vacancy.id === selectedId ? "selected" : ""} onClick={() => onSelect(vacancy)}>
            <td>{vacancy.rank ?? ""}</td>
            <td>{vacancy.source || "Вручную"}</td>
            <td>
              {vacancy.source_url ? (
                <a href={vacancy.source_url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                  Открыть источник
                </a>
              ) : (
                ""
              )}
            </td>
            <td className="source-text" title={vacancy.description_raw || vacancy.requirements || vacancy.responsibilities || vacancy.source_url}>
              {sourceTextPreview(vacancy)}
            </td>
            <td>{workModeLabel(workModeForVacancy(vacancy))}</td>
            <td>{vacancy.location || ""}</td>
            <td>{vacancy.company}</td>
            <td>{vacancy.title}</td>
            <td>{vacancy.fit_score}</td>
            <td>{priorityLabel(vacancy.priority)}</td>
            <td>{applicationStatusLabel(vacancy.submit_status)}</td>
            <td>
              {vacancy.cv_file_path ? (
                <a href={apiUrl(vacancy.cv_file_path)} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                  Открыть CV
                </a>
              ) : (
                ""
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
