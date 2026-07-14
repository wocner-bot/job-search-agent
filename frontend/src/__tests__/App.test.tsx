import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import App, { candidateTextWithContacts, missingOptionalContactInputs, type ContactDetails } from "../App.tsx";
import { apiUrl } from "../api.ts";
import { CvIntake } from "../components/CvIntake.tsx";
import { GlobalPreloader } from "../components/GlobalPreloader.tsx";
import { MetricsStrip } from "../components/MetricsStrip.tsx";
import { VacancyDetail } from "../components/VacancyDetail.tsx";
import { VacancyTable } from "../components/VacancyTable.tsx";
import { applicationStatusLabel, priorityLabel, workModeLabel } from "../labels.ts";
import type { Vacancy } from "../types.ts";
import { matchesRegion, workModeForVacancy } from "../vacancyFilters.ts";

const html = renderToStaticMarkup(<App />);
const styles = readFileSync(new URL("../styles.css", import.meta.url), "utf8");
const indexHtml = readFileSync(new URL("../../index.html", import.meta.url), "utf8");

assert.match(html, /Агент поиска работы/);
assert.match(html, /Рабочее пространство для подбора вакансий/);
assert.match(indexHtml, /<html lang="ru">/);
assert.match(indexHtml, /<title>Агент поиска работы<\/title>/);
assert.match(styles, /--earth-night-bg:/);
assert.match(styles, /svs\.gsfc\.nasa\.gov\/vis\/a030000\/a030800\/a030878\/BlackMarble_2016_rotate\.png/);
assert.match(styles, /--space-section: 20px;/);
assert.match(styles, /--space-panel: 20px;/);
assert.match(styles, /\.workspace\s*\{[^}]*display: grid;[^}]*gap: var\(--space-section\);/s);
assert.match(styles, /\.panel\s*\{[^}]*padding: var\(--space-panel\);[^}]*margin-bottom: 0;/s);
assert.match(styles, /\.metrics\s*\{[^}]*gap: var\(--space-section\);[^}]*margin-bottom: 0;/s);
assert.match(styles, /\.queue-layout > \.panel\s*\{[^}]*overflow-x: auto;/s);
assert.match(styles, /\.queue-table\s*\{[^}]*min-width: 1680px;/s);
assert.match(styles, /\.queue-table \.source-text\s*\{[^}]*min-width: 240px;/s);
assert.match(styles, /\.queue-table th,\s*\.queue-table td\s*\{[^}]*padding: 14px 16px;/s);
assert.match(styles, /\.workspace\s*\{[^}]*background: transparent;/s);
assert.match(styles, /\.workspace\s*\{[^}]*border: 0;/s);
assert.doesNotMatch(html, /href="#cv"/);
assert.doesNotMatch(html, /href="#package"/);
assert.doesNotMatch(html, /href="#exports"/);
assert.doesNotMatch(html, /Job Search Agent/);
assert.doesNotMatch(html, /CV-first workspace/);
assert.doesNotMatch(html, /CV Intake/);
assert.doesNotMatch(html, /Ready-to-Send/);
assert.doesNotMatch(html, /Exports/);
assert.doesNotMatch(html, /Vacancy Queue/);
assert.doesNotMatch(html, /Select a vacancy/);
assert.match(html, /Подбор вакансий по CV/);
assert.match(html, /Вставьте CV текстом/);
assert.doesNotMatch(html, /Файл с вакансиями/);
assert.match(html, /20 должностей/);
assert.match(html, /Подобрать вакансии/);
assert.match(html, /lucide-wand-sparkles/);
assert.match(styles, /\.primary-action\s*\{[^}]*linear-gradient/s);
assert.match(styles, /\.file-picker-button\s*\{[^}]*background: #050708;/s);
assert.match(html, /cv-input-grid/);
assert.match(html, /cv-field-box/);
assert.match(html, /cv-submit-box/);
assert.doesNotMatch(html, /Контакты для CV/);
assert.doesNotMatch(html, /upload-actions/);
assert.match(styles, /\.cv-input-grid\s*\{[^}]*grid-template-columns: repeat\(2, minmax\(0, 1fr\)\);/s);
assert.match(styles, /\.cv-field-box,\s*\.upload-box\s*\{[^}]*border: 1px solid var\(--line\);/s);
assert.match(styles, /\.cv-text-block\s*\{[^}]*grid-template-rows: auto 1fr;/s);
assert.match(styles, /\.cv-submit-box\s*\{[^}]*grid-template-rows: auto auto auto 1fr;/s);
assert.match(styles, /\.contact-request\s*\{[^}]*border: 1px solid rgba\(201, 220, 40, 0\.38\);/s);
assert.match(styles, /\.contact-grid\s*\{[^}]*grid-template-columns: repeat\(4, minmax\(0, 1fr\)\);/s);
assert.match(styles, /@media \(max-width: 760px\)[\s\S]*?\.cv-input-grid\s*\{[^}]*grid-template-columns: 1fr;/);
assert.doesNotMatch(html, /Анализ исходного CV/);
assert.doesNotMatch(html, /Senior recruiter review/);
assert.doesNotMatch(html, /Исходное CV/);
assert.doesNotMatch(html, /Улучшенная версия CV/);
assert.match(html, /Очередь вакансий/);
assert.match(html, /Ссылка на вакансию/);
assert.match(html, /Исходный текст/);
assert.match(html, /Формат работы/);
assert.match(html, /Регион/);
assert.match(html, /Все форматы/);
assert.match(html, /Удалённо/);
assert.match(html, /Офис/);
assert.match(html, /Гибрид/);
assert.match(html, /Адаптированное CV/);
assert.match(html, /Мастер-шаблон CV/);
assert.match(html, /Выберите вакансию/);
assert.doesNotMatch(html, /Добавить реальную вакансию/);
assert.doesNotMatch(html, /Название, компания, регион, язык и исходный текст будут заполнены автоматически/);
assert.doesNotMatch(html, /Исходник вакансии/);
assert.doesNotMatch(html, /Выберите источник/);

const emptyContacts: ContactDetails = { email: "", linkedin: "", portfolio: "", telegram: "" };
const emptyIntake = renderToStaticMarkup(
  <CvIntake
    cvText=""
    cvFileName=""
    contacts={emptyContacts}
    showContactFields={false}
    missingContactLabels={[]}
    isMatching={false}
    onCvTextChange={() => undefined}
    onCvFileChange={() => undefined}
    onContactChange={() => undefined}
    onMatch={() => undefined}
  />
);

assert.doesNotMatch(emptyIntake, /Ссылка на вакансию/);
assert.doesNotMatch(emptyIntake, /Выберите язык/);
assert.doesNotMatch(emptyIntake, /Requirements/);
assert.doesNotMatch(emptyIntake, /Responsibilities/);
assert.match(emptyIntake, /Выбрать файл/);

const contactIntake = renderToStaticMarkup(
  <CvIntake
    cvText="Aleksandr Grenkov Lead Product Designer"
    cvFileName=""
    contacts={emptyContacts}
    showContactFields
    missingContactLabels={["Email", "LinkedIn", "Portfolio", "Telegram"]}
    isMatching={false}
    onCvTextChange={() => undefined}
    onCvFileChange={() => undefined}
    onContactChange={() => undefined}
    onMatch={() => undefined}
  />
);
assert.match(contactIntake, /Контакты для CV/);
assert.match(contactIntake, /Можно заполнить сейчас или продолжить поиск без контактов/);
assert.match(contactIntake, /name@example\.com/);
assert.match(contactIntake, /https:\/\/www\.linkedin\.com\/in\/\.\.\./);
assert.match(contactIntake, /@username/);

assert.deepEqual(
  missingOptionalContactInputs("Aleksandr Grenkov Lead Product Designer", false, {
    email: "aleksandr@example.com",
    linkedin: "",
    portfolio: "",
    telegram: ""
  }),
  ["linkedin", "portfolio", "telegram"]
);
assert.equal(
  missingOptionalContactInputs(
    "aleksandr@example.com https://www.linkedin.com/in/aleksandr-grenkov https://grenkov.design @agrenkov",
    false,
    emptyContacts
  ).length,
  0
);
assert.match(
  candidateTextWithContacts("Aleksandr Grenkov", {
    email: "aleksandr@example.com",
    linkedin: "https://www.linkedin.com/in/aleksandr-grenkov",
    portfolio: "https://grenkov.design",
    telegram: "@agrenkov"
  }),
  /Contact details:\nEmail: aleksandr@example\.com\nLinkedIn: https:\/\/www\.linkedin\.com\/in\/aleksandr-grenkov\nPortfolio: https:\/\/grenkov\.design\nTelegram: @agrenkov/
);

const preloader = renderToStaticMarkup(<GlobalPreloader label="Обрабатываю данные..." />);
assert.match(preloader, /global-preloader/);
assert.match(preloader, /Обрабатываю данные/);

assert.equal(
  apiUrl("/api/vacancies/21/tailored-cv.docx", "https://job-search-agent-api-v7n6.onrender.com"),
  "https://job-search-agent-api-v7n6.onrender.com/api/vacancies/21/tailored-cv.docx"
);
assert.equal(apiUrl("https://example.com/job"), "https://example.com/job");

const vacancy = (location: string, description = "") =>
  ({
    location,
    description_raw: description,
    title: "Product Designer",
    requirements: "",
    responsibilities: ""
  }) as Vacancy;

assert.equal(workModeForVacancy(vacancy("Remote / Europe")), "Remote");
assert.equal(workModeForVacancy(vacancy("Москва", "гибридный формат")), "Hybrid");
assert.equal(workModeForVacancy(vacancy("Berlin")), "Office");
assert.equal(matchesRegion(vacancy("Remote / Europe"), "europe"), true);
assert.equal(matchesRegion(vacancy("Remote / Europe"), "moscow"), false);
assert.equal(workModeLabel("Remote"), "Удалённо");
assert.equal(workModeLabel("Hybrid"), "Гибрид");
assert.equal(workModeLabel("Office"), "Офис");
assert.equal(priorityLabel("Very High"), "Очень высокий");
assert.equal(applicationStatusLabel("Ready to send"), "Готово к отправке");

const sampleVacancy = {
  id: 1,
  external_id: "R01",
  rank: 1,
  source: "LinkedIn",
  company: "Example",
  title: "Product Designer",
  location: "Remote / Europe",
  posted: "",
  date_status: "",
  language: "English",
  fit_score: 97,
  priority: "Very High",
  submit_status: "Ready to send",
  next_action: "",
  cv_file_path: "/api/vacancies/1/tailored-cv.docx",
  pdf_file_path: "",
  png_preview_path: "",
  source_url: "https://example.com/job",
  description_raw: "Design systems and product UX",
  requirements: "",
  responsibilities: "",
  vacancy_keywords: "Design Systems",
  tailored_headline: "Lead Product Designer",
  top_match_keywords: "Product Strategy",
  gaps_risks: "",
  adaptation_strategy: ""
} as Vacancy;

const tableHtml = renderToStaticMarkup(<VacancyTable vacancies={[sampleVacancy]} selectedId={1} onSelect={() => undefined} />);
assert.match(tableHtml, /Открыть источник/);
assert.match(tableHtml, /Открыть CV/);
assert.match(tableHtml, /Очень высокий/);
assert.match(tableHtml, /Готово к отправке/);
assert.match(tableHtml, /Удалённо/);
assert.doesNotMatch(tableHtml, /Open source/);
assert.doesNotMatch(tableHtml, /Open CV/);
assert.doesNotMatch(tableHtml, /Very High/);
assert.doesNotMatch(tableHtml, /Ready to send/);

const detailHtml = renderToStaticMarkup(
  <VacancyDetail vacancy={sampleVacancy} material={undefined} onStatusChange={() => undefined} />
);
assert.match(detailHtml, /Статус/);
assert.match(detailHtml, /Источник/);
assert.match(detailHtml, /Ключевые слова вакансии/);
assert.match(detailHtml, /Открыть вакансию/);
assert.match(detailHtml, /Открыть адаптированное CV/);
assert.doesNotMatch(detailHtml, /Status/);
assert.doesNotMatch(detailHtml, /Vacancy keywords/);

const metricsHtml = renderToStaticMarkup(<MetricsStrip vacancies={[sampleVacancy]} />);
assert.match(metricsHtml, /Всего/);
assert.match(metricsHtml, /Очень высокий/);
assert.match(metricsHtml, /Готово/);
assert.match(metricsHtml, /Отправлено/);

console.log("App smoke test passed");
