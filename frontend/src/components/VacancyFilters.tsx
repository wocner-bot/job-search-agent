export interface Filters {
  priority: string;
  source: string;
  language: string;
  workMode: string;
  region: string;
}

export function VacancyFilters({ filters, onChange }: { filters: Filters; onChange: (filters: Filters) => void }) {
  return (
    <div className="filters">
      <select value={filters.priority} onChange={(event) => onChange({ ...filters, priority: event.target.value })} aria-label="Приоритет">
        <option value="">Все приоритеты</option>
        <option value="Very High">Очень высокий</option>
        <option value="High">Высокий</option>
        <option value="Medium">Средний</option>
        <option value="Low">Низкий</option>
      </select>
      <select value={filters.workMode} onChange={(event) => onChange({ ...filters, workMode: event.target.value })} aria-label="Формат работы">
        <option value="">Все форматы</option>
        <option value="Remote">Удалённо</option>
        <option value="Office">Офис</option>
        <option value="Hybrid">Гибрид</option>
      </select>
      <input value={filters.region} onChange={(event) => onChange({ ...filters, region: event.target.value })} placeholder="Регион" aria-label="Регион" />
      <input value={filters.source} onChange={(event) => onChange({ ...filters, source: event.target.value })} placeholder="Источник" />
      <input value={filters.language} onChange={(event) => onChange({ ...filters, language: event.target.value })} placeholder="Язык" />
    </div>
  );
}
