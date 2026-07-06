import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../App.tsx";
import { apiUrl } from "../api.ts";
import { CvIntake } from "../components/CvIntake.tsx";
import { GlobalPreloader } from "../components/GlobalPreloader.tsx";
import type { Vacancy } from "../types.ts";
import { matchesRegion, workModeForVacancy } from "../vacancyFilters.ts";

const html = renderToStaticMarkup(<App />);
const styles = readFileSync(new URL("../styles.css", import.meta.url), "utf8");

assert.match(html, /Job Search Agent/);
assert.match(styles, /photo-1598376538586-c244746bfa1e/);
assert.match(styles, /w=3200&h=1800&q=85/);
assert.match(styles, /\.workspace\s*\{[^}]*background: transparent;/s);
assert.match(styles, /\.workspace\s*\{[^}]*border: 0;/s);
assert.doesNotMatch(html, /href="#cv"/);
assert.doesNotMatch(html, /href="#package"/);
assert.doesNotMatch(html, /href="#exports"/);
assert.doesNotMatch(html, /CV Intake/);
assert.doesNotMatch(html, /Ready-to-Send/);
assert.doesNotMatch(html, /Exports/);
assert.match(html, /Подбор вакансий по CV/);
assert.match(html, /Вставьте CV текстом/);
assert.doesNotMatch(html, /Файл с вакансиями/);
assert.match(html, /20 должностей/);
assert.match(html, /Подобрать вакансии/);
assert.match(html, /upload-actions/);
assert.match(html, /Vacancy Link/);
assert.match(html, /Source Text/);
assert.match(html, /Work mode/);
assert.match(html, /Region/);
assert.match(html, /All work modes/);
assert.match(html, /Remote/);
assert.match(html, /Office/);
assert.match(html, /Hybrid/);
assert.match(html, /Tailored CV/);
assert.match(html, /Master CV Template/);
assert.doesNotMatch(html, /Добавить реальную вакансию/);
assert.doesNotMatch(html, /Ссылка на вакансию/);
assert.doesNotMatch(html, /Название, компания, регион, язык и исходный текст будут заполнены автоматически/);
assert.doesNotMatch(html, /Исходник вакансии/);
assert.doesNotMatch(html, /Выберите источник/);

const emptyIntake = renderToStaticMarkup(
  <CvIntake
    cvText=""
    cvFileName=""
    isMatching={false}
    onCvTextChange={() => undefined}
    onCvFileChange={() => undefined}
    onMatch={() => undefined}
  />
);

assert.doesNotMatch(emptyIntake, /Ссылка на вакансию/);
assert.doesNotMatch(emptyIntake, /Выберите язык/);
assert.doesNotMatch(emptyIntake, /Requirements/);
assert.doesNotMatch(emptyIntake, /Responsibilities/);

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

console.log("App smoke test passed");
