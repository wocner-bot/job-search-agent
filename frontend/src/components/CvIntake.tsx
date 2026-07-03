import { Save } from "lucide-react";

export function CvIntake({ value, onChange, onSubmit }: { value: string; onChange: (value: string) => void; onSubmit: () => void }) {
  return (
    <section id="cv" className="panel">
      <div className="panel-header">
        <h2>CV Intake</h2>
        <button type="button" onClick={onSubmit}>
          <Save size={16} aria-hidden="true" /> Save CV
        </button>
      </div>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} placeholder="Paste master CV text here" />
    </section>
  );
}
