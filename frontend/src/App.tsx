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
import type { ApplicationMaterial, ApplicationStatus, Vacancy } from "./types.ts";
import { matchesRegion, workModeForVacancy } from "./vacancyFilters.ts";

export default function App() {
  const [cvText, setCvText] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [isMatching, setIsMatching] = useState(false);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [materials, setMaterials] = useState<ApplicationMaterial[]>([]);
  const [selected, setSelected] = useState<Vacancy | undefined>();
  const [filters, setFilters] = useState<Filters>({ priority: "", source: "", language: "", workMode: "", region: "" });
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
          (!filters.workMode || workModeForVacancy(vacancy) === filters.workMode) &&
          matchesRegion(vacancy, filters.region) &&
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
    setMessage("Анализирую CV и ищу конкретные вакансии в LinkedIn, HH.ru и Telegram...");
    try {
      if (cvFile) {
        await api.uploadCandidateCv(cvFile);
      } else {
        await api.createCandidateFromText(cvText);
      }
      const analyzed = await api.collectMatchesFromSources();
      await refresh();
      setMessage(
        analyzed.generated > 0
          ? `Готово: найдено ${analyzed.generated} вакансий из источников, проанализировано ${analyzed.analyzed}.`
          : "Живые источники сейчас не вернули конкретных вакансий. Поисковые ссылки в таблицу не добавлены."
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Не удалось подобрать вакансии.");
    } finally {
      setIsMatching(false);
    }
  }

  async function updateStatus(status: ApplicationStatus) {
    if (!selected) return;
    const updated = await api.updateStatus(selected.id, status);
    setVacancies((rows) => rows.map((row) => (row.id === updated.id ? updated : row)));
    setSelected(updated);
  }

  const selectedMaterial = materials.find((material) => material.vacancy_id === selected?.id);
  const isProcessing = isMatching;

  return (
    <Layout>
      {isProcessing && <GlobalPreloader label="Обрабатываю данные..." />}
      <header className="workspace-header">
        <div>
          <h1>Агент поиска работы</h1>
          <p>Рабочее пространство для подбора вакансий по CV и подготовки материалов к отправке.</p>
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
      />
      <MetricsStrip vacancies={vacancies} />
      <section id="queue" className="queue-layout">
        <div className="panel">
          <div className="panel-header">
            <h2>Очередь вакансий</h2>
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
