import { FileText, Sparkles, Upload } from "lucide-react";
import type { VacancyDraft } from "../types";

type CvIntakeProps = {
  cvText: string;
  cvFileName: string;
  isMatching: boolean;
  onCvTextChange: (value: string) => void;
  onCvFileChange: (file: File | null) => void;
  onMatch: () => void;
  vacancyDraft: VacancyDraft;
  isAddingVacancy: boolean;
  onVacancyDraftChange: (draft: VacancyDraft) => void;
  onAddVacancy: () => void;
};

export function CvIntake({
  cvText,
  cvFileName,
  isMatching,
  onCvTextChange,
  onCvFileChange,
  onMatch,
  vacancyDraft,
  isAddingVacancy,
  onVacancyDraftChange,
  onAddVacancy
}: CvIntakeProps) {
  const updateVacancyDraft = (field: keyof VacancyDraft, value: string) => {
    onVacancyDraftChange({ ...vacancyDraft, [field]: value });
  };

  return (
    <section id="cv" className="panel match-panel">
      <div className="match-copy">
        <h1>Подбор вакансий по CV</h1>
        <p>Вставьте или загрузите CV. Агент как старший рекрутер подберёт 20 должностей и точные ключевые слова для каждой.</p>
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
      <div className="upload-actions">
        <label className="upload-box">
          <span>
            <Upload size={16} aria-hidden="true" /> CV файлом
          </span>
          <input type="file" accept=".txt,.pdf,.docx" onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)} />
          <strong>{cvFileName || "PDF, DOCX или TXT"}</strong>
        </label>
        <button className="primary-action match-button" type="button" onClick={onMatch} disabled={isMatching}>
          <Sparkles size={18} aria-hidden="true" /> {isMatching ? "Подбираю..." : "Подобрать вакансии"}
        </button>
      </div>
      <div className="vacancy-source-form">
        <div className="match-copy">
          <h2>Добавить реальную вакансию</h2>
          <p>Вставьте ссылку на вакансию. Название, компания, регион, язык и исходный текст будут заполнены автоматически.</p>
        </div>
        <div className="form-grid">
          <label>
            Ссылка на вакансию
            <input value={vacancyDraft.source_url} onChange={(event) => updateVacancyDraft("source_url", event.target.value)} placeholder="https://..." />
          </label>
        </div>
        <button className="primary-action secondary-action" type="button" onClick={onAddVacancy} disabled={isAddingVacancy}>
          {isAddingVacancy ? "Добавляю..." : "Добавить вакансию и CV"}
        </button>
      </div>
    </section>
  );
}
