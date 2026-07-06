import { Download } from "lucide-react";
import { apiUrl } from "../api.ts";

export function ExportBar() {
  return (
    <section id="exports" className="panel compact">
      <a className="button-link" href={apiUrl("/api/candidate/master-cv.docx")}>
        <Download size={16} aria-hidden="true" /> Мастер-шаблон CV
      </a>
      <a className="button-link" href={apiUrl("/api/exports/zip")}>
        <Download size={16} aria-hidden="true" /> Скачать ZIP-пакет
      </a>
    </section>
  );
}
