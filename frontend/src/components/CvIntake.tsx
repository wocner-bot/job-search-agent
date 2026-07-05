import { BriefcaseBusiness, FileText, Sparkles, Upload } from "lucide-react";

type CvIntakeProps = {
  cvText: string;
  cvFileName: string;
  vacancyFileName: string;
  isMatching: boolean;
  onCvTextChange: (value: string) => void;
  onCvFileChange: (file: File | null) => void;
  onVacancyFileChange: (file: File | null) => void;
  onMatch: () => void;
};

export function CvIntake({
  cvText,
  cvFileName,
  vacancyFileName,
  isMatching,
  onCvTextChange,
  onCvFileChange,
  onVacancyFileChange,
  onMatch
}: CvIntakeProps) {
  return (
    <section id="cv" className="panel match-panel">
      <div className="match-copy">
        <h1>Подбор вакансий по CV</h1>
        <p>Загрузите CV и файл с вакансиями, чтобы получить ранжированный список и ready-to-send материалы.</p>
      </div>
      <label className="field-block">
        <span>
          <FileText size={16} aria-hidden="true" /> Вставьте CV текстом
        </span>
        <textarea
          value={cvText}
          onChange={(event) => onCvTextChange(event.target.value)}
          placeholder="Вставьте сюда CV, если не хотите загружать файл"
        />
      </label>
      <div className="upload-grid">
        <label className="upload-box">
          <span>
            <Upload size={16} aria-hidden="true" /> CV файлом
          </span>
          <input type="file" accept=".txt,.pdf,.docx" onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)} />
          <strong>{cvFileName || "PDF, DOCX или TXT"}</strong>
        </label>
        <label className="upload-box">
          <span>
            <BriefcaseBusiness size={16} aria-hidden="true" /> Файл с вакансиями
          </span>
          <input type="file" accept=".csv,.xlsx" onChange={(event) => onVacancyFileChange(event.target.files?.[0] ?? null)} />
          <strong>{vacancyFileName || "CSV или XLSX"}</strong>
        </label>
      </div>
      <button className="primary-action" type="button" onClick={onMatch} disabled={isMatching}>
        <Sparkles size={18} aria-hidden="true" /> {isMatching ? "Подбираю..." : "Подобрать вакансии"}
      </button>
    </section>
  );
}
