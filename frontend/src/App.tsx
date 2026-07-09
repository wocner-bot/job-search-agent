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

export type ContactKey = "email" | "linkedin" | "portfolio" | "telegram";
export type ContactDetails = Record<ContactKey, string>;

const EMPTY_CONTACTS: ContactDetails = {
  email: "",
  linkedin: "",
  portfolio: "",
  telegram: ""
};

const CONTACT_LABELS: Record<ContactKey, string> = {
  email: "Email",
  linkedin: "LinkedIn",
  portfolio: "Portfolio",
  telegram: "Telegram"
};

export default function App() {
  const [cvText, setCvText] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [contacts, setContacts] = useState<ContactDetails>(EMPTY_CONTACTS);
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

  const missingContactKeys = missingCvContactKeys(cvText, Boolean(cvFile));
  const showContactFields = (Boolean(cvText.trim()) || Boolean(cvFile)) && missingContactKeys.length > 0;
  const missingContactLabels = missingContactKeys.map((key) => CONTACT_LABELS[key]);

  async function matchVacancies() {
    if (!cvText.trim() && !cvFile) {
      setMessage("Добавьте CV текстом или файлом.");
      return;
    }
    const missingInputs = missingRequiredContactInputs(cvText, Boolean(cvFile), contacts);
    if (missingInputs.length > 0) {
      setMessage(`Добавьте контакты для CV: ${missingInputs.map((key) => CONTACT_LABELS[key]).join(", ")}.`);
      return;
    }
    setIsMatching(true);
    setMessage("Анализирую CV и ищу конкретные вакансии в LinkedIn, HH.ru и Telegram...");
    try {
      if (cvFile) {
        await api.uploadCandidateCv(cvFile);
        if (hasEnteredContacts(contacts)) {
          await api.updateCandidateContacts(contacts);
        }
      } else {
        await api.createCandidateFromText(candidateTextWithContacts(cvText, contacts));
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
        contacts={contacts}
        showContactFields={showContactFields}
        missingContactLabels={missingContactLabels}
        onContactChange={(key, value) => setContacts((current) => ({ ...current, [key]: value }))}
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

export function missingCvContactKeys(cvText: string, hasCvFile: boolean): ContactKey[] {
  if (!cvText.trim() && !hasCvFile) return [];
  const text = cvText.toLowerCase();
  return (Object.keys(CONTACT_LABELS) as ContactKey[]).filter((key) => {
    if (hasCvFile && !cvText.trim()) return true;
    if (key === "email") return !/[\w.+-]+@[\w.-]+\.[a-z]{2,}/i.test(cvText);
    if (key === "linkedin") return !text.includes("linkedin.com/");
    if (key === "portfolio") return !/https?:\/\/(?![^/]*linkedin\.com)(?![^/]*t\.me)(?![^/]*hh\.ru)[^\s,)>\]]+/i.test(cvText);
    return !/(^|[\s:])@[a-z0-9_]{4,}\b/i.test(cvText) && !text.includes("t.me/");
  });
}

export function missingRequiredContactInputs(cvText: string, hasCvFile: boolean, contacts: ContactDetails): ContactKey[] {
  return missingCvContactKeys(cvText, hasCvFile).filter((key) => !contacts[key].trim());
}

export function candidateTextWithContacts(cvText: string, contacts: ContactDetails): string {
  if (!hasEnteredContacts(contacts)) return cvText;
  const lines = (Object.keys(CONTACT_LABELS) as ContactKey[])
    .map((key) => [CONTACT_LABELS[key], contacts[key].trim()])
    .filter(([, value]) => value)
    .map(([label, value]) => `${label}: ${value}`);
  return `${cvText.trim()}\n\nContact details:\n${lines.join("\n")}`.trim();
}

function hasEnteredContacts(contacts: ContactDetails): boolean {
  return Object.values(contacts).some((value) => value.trim());
}
