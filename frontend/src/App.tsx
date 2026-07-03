import { useEffect, useMemo, useState } from "react";
import { api } from "./api.ts";
import { CvIntake } from "./components/CvIntake.tsx";
import { ExportBar } from "./components/ExportBar.tsx";
import { ImportPanel } from "./components/ImportPanel.tsx";
import { Layout } from "./components/Layout.tsx";
import { MetricsStrip } from "./components/MetricsStrip.tsx";
import { type Filters, VacancyFilters } from "./components/VacancyFilters.tsx";
import { VacancyDetail } from "./components/VacancyDetail.tsx";
import { VacancyTable } from "./components/VacancyTable.tsx";
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "./types.ts";

export default function App() {
  const [cvText, setCvText] = useState("");
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [materials, setMaterials] = useState<ApplicationMaterial[]>([]);
  const [selected, setSelected] = useState<Vacancy | undefined>();
  const [filters, setFilters] = useState<Filters>({ priority: "", source: "", language: "" });
  const [message, setMessage] = useState("");

  async function refresh() {
    const [vacancyRows, materialRows] = await Promise.all([api.vacancies(), api.materials()]);
    setVacancies(vacancyRows);
    setMaterials(materialRows);
    setSelected((current) => vacancyRows.find((row) => row.id === current?.id) ?? vacancyRows[0]);
  }

  useEffect(() => {
    refresh().catch(() => setMessage("Backend is not connected yet."));
  }, []);

  const visibleVacancies = useMemo(
    () =>
      vacancies.filter((vacancy) => {
        return (
          (!filters.priority || vacancy.priority === filters.priority) &&
          (!filters.source || vacancy.source.toLowerCase().includes(filters.source.toLowerCase())) &&
          (!filters.language || vacancy.language.toLowerCase().includes(filters.language.toLowerCase()))
        );
      }),
    [filters, vacancies]
  );

  async function saveCv() {
    await api.createCandidateFromText(cvText);
    setMessage("CV profile saved.");
  }

  async function importPackage() {
    const result = await api.importCurrentPackage();
    setMessage(`Imported ${result.imported} vacancies.`);
    await refresh();
  }

  async function runAnalysis() {
    const result = await api.runAnalysis();
    setMessage(`Analyzed ${result.analyzed} vacancies.`);
    await refresh();
  }

  async function updateStatus(status: ApplicationStatus) {
    if (!selected) return;
    const updated = await api.updateStatus(selected.id, status);
    setVacancies((rows) => rows.map((row) => (row.id === updated.id ? updated : row)));
    setSelected(updated);
  }

  const selectedMaterial = materials.find((material) => material.vacancy_id === selected?.id);

  return (
    <Layout>
      <header className="workspace-header">
        <div>
          <h1>Vacancy Queue</h1>
          <p>Ready-to-send application workspace for tailored CVs and recruiter messages.</p>
        </div>
      </header>
      {message && <div className="notice">{message}</div>}
      <ImportPanel onImport={importPackage} onAnalyze={runAnalysis} />
      <MetricsStrip vacancies={vacancies} />
      <CvIntake value={cvText} onChange={setCvText} onSubmit={saveCv} />
      <section id="queue" className="queue-layout">
        <div className="panel">
          <div className="panel-header">
            <h2>Vacancy Queue</h2>
            <VacancyFilters filters={filters} onChange={setFilters} />
          </div>
          <VacancyTable vacancies={visibleVacancies} selectedId={selected?.id} onSelect={setSelected} />
        </div>
        <VacancyDetail vacancy={selected} material={selectedMaterial} onStatusChange={updateStatus} />
      </section>
      <ExportBar />
    </Layout>
  );
}
