import { apiUrl } from "../api.ts";
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "../types";

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
    return <aside className="detail-panel">Select a vacancy to review ready-to-send materials.</aside>;
  }
  return (
    <aside className="detail-panel">
      <h2>{vacancy.company}</h2>
      <p className="muted">{vacancy.title}</p>
      <label>
        Status
        <select value={vacancy.submit_status} onChange={(event) => onStatusChange(event.target.value as ApplicationStatus)}>
          {statuses.map((status) => <option key={status}>{status}</option>)}
        </select>
      </label>
      <dl>
        <dt>Source</dt>
        <dd>{vacancy.source}</dd>
        <dt>Vacancy keywords</dt>
        <dd>{vacancy.vacancy_keywords}</dd>
        <dt>Headline</dt>
        <dd>{vacancy.tailored_headline}</dd>
        <dt>Keywords</dt>
        <dd>{vacancy.top_match_keywords}</dd>
        <dt>Risks</dt>
        <dd>{vacancy.gaps_risks}</dd>
        <dt>Strategy</dt>
        <dd>{vacancy.adaptation_strategy}</dd>
        <dt>Vacancy source text</dt>
        <dd>{vacancy.description_raw || "No source text saved yet."}</dd>
        <dt>Requirements</dt>
        <dd>{vacancy.requirements || "No requirements saved yet."}</dd>
        <dt>Responsibilities</dt>
        <dd>{vacancy.responsibilities || "No responsibilities saved yet."}</dd>
      </dl>
      {vacancy.source_url && <a href={vacancy.source_url} target="_blank" rel="noreferrer">Open vacancy</a>}
      {vacancy.cv_file_path && <a href={apiUrl(vacancy.cv_file_path)} target="_blank" rel="noreferrer">Open tailored CV</a>}
      {material && (
        <div className="messages">
          <h3>Ready-to-send</h3>
          <textarea readOnly value={material.short_note} />
          <textarea readOnly value={material.recruiter_dm} />
          <textarea readOnly value={material.email_cover_letter} />
        </div>
      )}
    </aside>
  );
}
