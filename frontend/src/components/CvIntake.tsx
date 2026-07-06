import { FileText, Upload, WandSparkles } from "lucide-react";

type CvIntakeProps = {
  cvText: string;
  cvFileName: string;
  isMatching: boolean;
  onCvTextChange: (value: string) => void;
  onCvFileChange: (file: File | null) => void;
  onMatch: () => void;
};

export function CvIntake({
  cvText,
  cvFileName,
  isMatching,
  onCvTextChange,
  onCvFileChange,
  onMatch
}: CvIntakeProps) {
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
          <span className="file-picker-row">
            <span className="file-picker-button">Выбрать файл</span>
            <span className="file-picker-name">{cvFileName || "Файл не выбран"}</span>
          </span>
          <input className="file-picker-input" type="file" accept=".txt,.pdf,.docx" onChange={(event) => onCvFileChange(event.target.files?.[0] ?? null)} />
          <strong>PDF, DOCX или TXT</strong>
        </label>
        <button className="primary-action match-button" type="button" onClick={onMatch} disabled={isMatching}>
          <WandSparkles size={18} aria-hidden="true" /> {isMatching ? "Подбираю..." : "Подобрать вакансии"}
        </button>
      </div>
    </section>
  );
}
