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
assert.match(html, /Ссылка на вакансию/);
assert.match(html, /Название, компания, регион, язык и исходный текст будут заполнены автоматически/);
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

assert.match(emptyIntake, /Ссылка на вакансию/);
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

console.log("App smoke test passed");
