import { useMemo, useState } from "react";
import { api } from "./api.ts";
import { CvIntake } from "./components/CvIntake.tsx";
import { ExportBar } from "./components/ExportBar.tsx";
import { GlobalPreloader } from "./components/GlobalPreloader.tsx";
import { Layout } from "./components/Layout.tsx";
import { MetricsStrip } from "./components/MetricsStrip.tsx";
import { type Filters, VacancyFilters } from "./components/VacancyFilters.tsx";
import { VacancyDetail } from "./components/VacancyDetail.tsx";
import { VacancyTable } from "./components/VacancyTable.tsx";
import type { ApplicationMaterial, ApplicationStatus, Vacancy, VacancyDraft } from "./types.ts";

const emptyVacancyDraft: VacancyDraft = {
  external_id: "",
  source: "",
  company: "",
  title: "",
  location: "",
  language: "",
  source_url: "",
  description_raw: "",
  requirements: "",
  responsibilities: ""
};

export default function App() {
  const [cvText, setCvText] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [isMatching, setIsMatching] = useState(false);
  const [isAddingVacancy, setIsAddingVacancy] = useState(false);
  const [vacancyDraft, setVacancyDraft] = useState<VacancyDraft>(emptyVacancyDraft);
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

  async function matchVacancies() {
    if (!cvText.trim() && !cvFile) {
      setMessage("Добавьте CV текстом или файлом.");
      return;
    }
    setIsMatching(true);
    setMessage("Анализирую CV и подбираю 20 должностей...");
    try {
      if (cvFile) {
        await api.uploadCandidateCv(cvFile);
      } else {
        await api.createCandidateFromText(cvText);
      }
      const analyzed = await api.generateMatchesFromCv();
      await refresh();
      setMessage(`Готово: подобрано ${analyzed.generated} должностей, проанализировано ${analyzed.analyzed}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось подобрать вакансии.");
    } finally {
      setIsMatching(false);
    }
  }

  async function addVacancy() {
    if (!vacancyDraft.title.trim() || !vacancyDraft.company.trim()) {
      setMessage("Добавьте компанию и название вакансии.");
      return;
    }
    if (!vacancyDraft.description_raw.trim() && !vacancyDraft.requirements.trim() && !vacancyDraft.source_url.trim()) {
      setMessage("Добавьте ссылку, описание или требования вакансии.");
      return;
    }
    setIsAddingVacancy(true);
    setMessage("Добавляю вакансию и готовлю CV под неё...");
    try {
      await api.createVacancy({
        ...vacancyDraft,
        external_id: vacancyDraft.external_id || `MAN-${Date.now()}`
      });
      await api.runAnalysis();
      await refresh();
      setVacancyDraft(emptyVacancyDraft);
      setMessage("Вакансия добавлена: исходник сохранён, tailored CV привязан в таблице.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось добавить вакансию.");
    } finally {
      setIsAddingVacancy(false);
    }
  }

  async function updateStatus(status: ApplicationStatus) {
    if (!selected) return;
    const updated = await api.updateStatus(selected.id, status);
    setVacancies((rows) => rows.map((row) => (row.id === updated.id ? updated : row)));
    setSelected(updated);
  }

  const selectedMaterial = materials.find((material) => material.vacancy_id === selected?.id);
  const isProcessing = isMatching || isAddingVacancy;

  return (
    <Layout>
      {isProcessing && <GlobalPreloader label="Обрабатываю данные..." />}
      <header className="workspace-header">
        <div>
          <h1>Job Search Agent</h1>
          <p>CV-first workspace for matching vacancies and preparing ready-to-send materials.</p>
        </div>
      </header>
      {message && <div className="notice">{message}</div>}
      <CvIntake
        cvText={cvText}
        cvFileName={cvFile?.name ?? ""}
        isMatching={isMatching}
        onCvTextChange={setCvText}
        onCvFileChange={setCvFile}
        onMatch={matchVacancies}
        vacancyDraft={vacancyDraft}
        isAddingVacancy={isAddingVacancy}
        onVacancyDraftChange={setVacancyDraft}
        onAddVacancy={addVacancy}
      />
      <MetricsStrip vacancies={vacancies} />
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
