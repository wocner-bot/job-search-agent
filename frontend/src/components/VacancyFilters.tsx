export interface Filters {
  priority: string;
  source: string;
  language: string;
}

export function VacancyFilters({ filters, onChange }: { filters: Filters; onChange: (filters: Filters) => void }) {
  return (
    <div className="filters">
      <select value={filters.priority} onChange={(event) => onChange({ ...filters, priority: event.target.value })} aria-label="Priority">
        <option value="">All priorities</option>
        <option>Very High</option>
        <option>High</option>
        <option>Medium</option>
        <option>Low</option>
      </select>
      <input value={filters.source} onChange={(event) => onChange({ ...filters, source: event.target.value })} placeholder="Source" />
      <input value={filters.language} onChange={(event) => onChange({ ...filters, language: event.target.value })} placeholder="Language" />
    </div>
  );
}
