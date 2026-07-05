import assert from "node:assert/strict";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../App.tsx";
import { apiUrl } from "../api.ts";
import { CvIntake } from "../components/CvIntake.tsx";
import { GlobalPreloader } from "../components/GlobalPreloader.tsx";

const html = renderToStaticMarkup(<App />);

assert.match(html, /Job Search Agent/);
assert.match(html, /Подбор вакансий по CV/);
assert.match(html, /Вставьте CV текстом/);
assert.doesNotMatch(html, /Файл с вакансиями/);
assert.match(html, /20 должностей/);
assert.match(html, /Подобрать вакансии/);
assert.match(html, /upload-actions/);
assert.match(html, /Vacancy Link/);
assert.match(html, /Source Text/);
assert.match(html, /Tailored CV/);
assert.match(html, /Master CV Template/);
assert.match(html, /Добавить реальную вакансию/);
assert.match(html, /Исходник вакансии/);
assert.match(html, /LinkedIn/);

const emptyIntake = renderToStaticMarkup(
  <CvIntake
    cvText=""
    cvFileName=""
    isMatching={false}
    onCvTextChange={() => undefined}
    onCvFileChange={() => undefined}
    onMatch={() => undefined}
    vacancyDraft={{
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
    }}
    isAddingVacancy={false}
    onVacancyDraftChange={() => undefined}
    onAddVacancy={() => undefined}
  />
);

assert.match(emptyIntake, /Выберите источник/);
assert.match(emptyIntake, /Выберите язык/);
[
  "https://hh.ru/",
  "Telegram @wantapply_design",
  "Telegram @young_relocate",
  "Telegram @vdhl_good",
  "Telegram @moskovskayarabota",
  "Telegram @professionalsjob",
  "Telegram @naudalenkebro",
  "Telegram @zapwork"
].forEach((source) => assert.match(emptyIntake, new RegExp(source.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))));
assert.doesNotMatch(emptyIntake, /<option selected="">LinkedIn<\/option>/);
assert.doesNotMatch(emptyIntake, /<option selected="">English<\/option>/);

const preloader = renderToStaticMarkup(<GlobalPreloader label="Обрабатываю данные..." />);
assert.match(preloader, /global-preloader/);
assert.match(preloader, /Обрабатываю данные/);

assert.equal(
  apiUrl("/api/vacancies/21/tailored-cv.docx", "https://job-search-agent-api-v7n6.onrender.com"),
  "https://job-search-agent-api-v7n6.onrender.com/api/vacancies/21/tailored-cv.docx"
);
assert.equal(apiUrl("https://example.com/job"), "https://example.com/job");

console.log("App smoke test passed");
