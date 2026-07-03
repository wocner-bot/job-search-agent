import type { Vacancy } from "../types";

export function VacancyTable({ vacancies, selectedId, onSelect }: { vacancies: Vacancy[]; selectedId?: number; onSelect: (vacancy: Vacancy) => void }) {
  return (
    <table className="queue-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Company</th>
          <th>Vacancy</th>
          <th>Fit</th>
          <th>Priority</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {vacancies.map((vacancy) => (
          <tr key={vacancy.id} className={vacancy.id === selectedId ? "selected" : ""} onClick={() => onSelect(vacancy)}>
            <td>{vacancy.rank ?? ""}</td>
            <td>{vacancy.company}</td>
            <td>{vacancy.title}</td>
            <td>{vacancy.fit_score}</td>
            <td>{vacancy.priority}</td>
            <td>{vacancy.submit_status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
