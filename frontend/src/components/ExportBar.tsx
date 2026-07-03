import { Download } from "lucide-react";

export function ExportBar() {
  return (
    <section id="exports" className="panel compact">
      <a className="button-link" href="/api/exports/zip">
        <Download size={16} aria-hidden="true" /> Export ZIP Package
      </a>
    </section>
  );
}
