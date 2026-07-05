import { FileText, Sparkles, Upload } from "lucide-react";
import type { VacancyDraft } from "../types";

const sourcePresets = [
  "LinkedIn",
  "HH.ru",
  "Telegram @wantapply_design",
  "Telegram @young_relocate",
  "Telegram @vdhl_good",
  "Telegram @professionalsjob",
  "Company ATS",
  "Greenhouse",
  "Lever",
  "Ashby",
  "Workable",
  "Wellfound",
  "Y Combinator Work at a Startup",
  "Welcome to the Jungle",
  "Otta",
  "Habr Career",
  "Indeed",
  "Glassdoor",
  "Manual"
];

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
      <div className="upload-grid single-upload">
        <label className="upload-box">
          <span>
            <Upload size={16} aria-hidden="true" /> CV файлом
          </span>
          <input type="file" accept=".txt,.pdf,.docx" onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)} />
          <strong>{cvFileName || "PDF, DOCX или TXT"}</strong>
        </label>
      </div>
      <button className="primary-action" type="button" onClick={onMatch} disabled={isMatching}>
        <Sparkles size={18} aria-hidden="true" /> {isMatching ? "Подбираю..." : "Подобрать вакансии"}
      </button>
      <div className="vacancy-source-form">
        <div className="match-copy">
          <h2>Добавить реальную вакансию</h2>
          <p>Вставьте исходник вакансии: ссылка, описание, требования и responsibilities. CV будет адаптирован под эту конкретную строку.</p>
        </div>
        <div className="form-grid">
          <label>
            Источник
            <select value={vacancyDraft.source} onChange={(event) => updateVacancyDraft("source", event.target.value)}>
              {sourcePresets.map((source) => (
                <option key={source}>{source}</option>
              ))}
            </select>
          </label>
          <label>
            Компания
            <input value={vacancyDraft.company} onChange={(event) => updateVacancyDraft("company", event.target.value)} placeholder="Rivian" />
          </label>
          <label>
            Название вакансии
            <input
              value={vacancyDraft.title}
              onChange={(event) => updateVacancyDraft("title", event.target.value)}
              placeholder="Sr. Lead Product Designer - Design System Frameworks"
            />
          </label>
          <label>
            Язык
            <select value={vacancyDraft.language} onChange={(event) => updateVacancyDraft("language", event.target.value)}>
              <option>English</option>
              <option>Russian</option>
              <option>English/Russian</option>
              <option>Other</option>
            </select>
          </label>
          <label>
            Локация
            <input value={vacancyDraft.location} onChange={(event) => updateVacancyDraft("location", event.target.value)} placeholder="Remote / Europe" />
          </label>
          <label>
            Ссылка на вакансию
            <input value={vacancyDraft.source_url} onChange={(event) => updateVacancyDraft("source_url", event.target.value)} placeholder="https://..." />
          </label>
        </div>
        <label className="field-block">
          <span>Исходник вакансии</span>
          <textarea
            value={vacancyDraft.description_raw}
            onChange={(event) => updateVacancyDraft("description_raw", event.target.value)}
            placeholder="Вставьте полный текст вакансии"
          />
        </label>
        <label className="field-block">
          <span>Requirements</span>
          <textarea value={vacancyDraft.requirements} onChange={(event) => updateVacancyDraft("requirements", event.target.value)} />
        </label>
        <label className="field-block">
          <span>Responsibilities</span>
          <textarea value={vacancyDraft.responsibilities} onChange={(event) => updateVacancyDraft("responsibilities", event.target.value)} />
        </label>
        <button className="primary-action secondary-action" type="button" onClick={onAddVacancy} disabled={isAddingVacancy}>
          {isAddingVacancy ? "Добавляю..." : "Добавить вакансию и CV"}
        </button>
      </div>
    </section>
  );
}
