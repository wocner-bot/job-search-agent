import { apiUrl } from "../api.ts";
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
          <th>Rank</th>
          <th>Source</th>
          <th>Vacancy Link</th>
          <th>Source Text</th>
          <th>Work mode</th>
          <th>Region</th>
          <th>Company</th>
          <th>Vacancy</th>
          <th>Fit</th>
          <th>Priority</th>
          <th>Status</th>
          <th>Tailored CV</th>
        </tr>
      </thead>
      <tbody>
        {vacancies.map((vacancy) => (
          <tr key={vacancy.id} className={vacancy.id === selectedId ? "selected" : ""} onClick={() => onSelect(vacancy)}>
            <td>{vacancy.rank ?? ""}</td>
            <td>{vacancy.source || "Manual"}</td>
            <td>
              {vacancy.source_url ? (
                <a href={vacancy.source_url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                  Open source
                </a>
              ) : (
                ""
              )}
            </td>
            <td className="source-text" title={vacancy.description_raw || vacancy.requirements || vacancy.responsibilities || vacancy.source_url}>
              {sourceTextPreview(vacancy)}
            </td>
            <td>{workModeForVacancy(vacancy)}</td>
            <td>{vacancy.location || ""}</td>
            <td>{vacancy.company}</td>
            <td>{vacancy.title}</td>
            <td>{vacancy.fit_score}</td>
            <td>{vacancy.priority}</td>
            <td>{vacancy.submit_status}</td>
            <td>
              {vacancy.cv_file_path ? (
                <a href={apiUrl(vacancy.cv_file_path)} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                  Open CV
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
