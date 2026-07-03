import { FileSpreadsheet, Wand2 } from "lucide-react";

export function ImportPanel({ onImport, onAnalyze }: { onImport: () => void; onAnalyze: () => void }) {
  return (
    <section className="toolbar">
      <button type="button" onClick={onImport}>
        <FileSpreadsheet size={16} aria-hidden="true" /> Import Current Package
      </button>
      <button type="button" onClick={onAnalyze}>
        <Wand2 size={16} aria-hidden="true" /> Run Analysis
      </button>
    </section>
  );
}
