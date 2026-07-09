import { FileText, Upload, WandSparkles } from "lucide-react";
import type { ContactDetails, ContactKey } from "../App.tsx";

type CvIntakeProps = {
  cvText: string;
  cvFileName: string;
  contacts: ContactDetails;
  showContactFields: boolean;
  missingContactLabels: string[];
  isMatching: boolean;
  onCvTextChange: (value: string) => void;
  onCvFileChange: (file: File | null) => void;
  onContactChange: (key: ContactKey, value: string) => void;
  onMatch: () => void;
};

export function CvIntake({
  cvText,
  cvFileName,
  contacts,
  showContactFields,
  missingContactLabels,
  isMatching,
  onCvTextChange,
  onCvFileChange,
  onContactChange,
  onMatch
}: CvIntakeProps) {
  return (
    <section id="cv" className="panel match-panel">
      <div className="match-copy">
        <h1>Подбор вакансий по CV</h1>
        <p>Вставьте или загрузите CV. Агент как старший рекрутер подберёт 20 должностей и точные ключевые слова для каждой.</p>
      </div>
      <div className="cv-input-grid">
        <label className="field-block cv-field-box cv-text-block">
          <span>
            <FileText size={16} aria-hidden="true" /> Вставьте CV текстом
          </span>
          <textarea
            className="cv-textarea"
            value={cvText}
            onChange={(event) => onCvTextChange(event.target.value)}
            placeholder="Вставьте сюда CV, если не хотите загружать файл"
          />
        </label>
        <div className="upload-box cv-submit-box">
          <span>
            <Upload size={16} aria-hidden="true" /> CV файлом
          </span>
          <label className="file-picker-row">
            <span className="file-picker-button">Выбрать файл</span>
            <span className="file-picker-name">{cvFileName || "Файл не выбран"}</span>
            <input className="file-picker-input" type="file" accept=".txt,.pdf,.docx" onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)} />
          </label>
          <strong>PDF, DOCX или TXT</strong>
          <button className="primary-action match-button" type="button" onClick={onMatch} disabled={isMatching}>
            <WandSparkles size={18} aria-hidden="true" /> {isMatching ? "Подбираю..." : "Подобрать вакансии"}
          </button>
        </div>
      </div>
      {showContactFields && (
        <div className="contact-request">
          <div>
            <h2>Контакты для CV</h2>
            <p>Не нашёл в CV: {missingContactLabels.join(", ")}. Можно заполнить сейчас или продолжить поиск без контактов.</p>
          </div>
          <div className="contact-grid">
            <label>
              <span>Email</span>
              <input
                type="email"
                value={contacts.email}
                onChange={(event) => onContactChange("email", event.target.value)}
                placeholder="name@example.com"
              />
            </label>
            <label>
              <span>LinkedIn</span>
              <input
                type="url"
                value={contacts.linkedin}
                onChange={(event) => onContactChange("linkedin", event.target.value)}
                placeholder="https://www.linkedin.com/in/..."
              />
            </label>
            <label>
              <span>Portfolio</span>
              <input
                type="url"
                value={contacts.portfolio}
                onChange={(event) => onContactChange("portfolio", event.target.value)}
                placeholder="https://..."
              />
            </label>
            <label>
              <span>Telegram</span>
              <input
                value={contacts.telegram}
                onChange={(event) => onContactChange("telegram", event.target.value)}
                placeholder="@username"
              />
            </label>
          </div>
        </div>
      )}
    </section>
  );
}
