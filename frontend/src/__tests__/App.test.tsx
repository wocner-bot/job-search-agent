import assert from "node:assert/strict";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../App.tsx";
import { apiUrl } from "../api.ts";

const html = renderToStaticMarkup(<App />);

assert.match(html, /Job Search Agent/);
assert.match(html, /Подбор вакансий по CV/);
assert.match(html, /Вставьте CV текстом/);
assert.doesNotMatch(html, /Файл с вакансиями/);
assert.match(html, /20 должностей/);
assert.match(html, /Подобрать вакансии/);
assert.match(html, /Tailored CV/);
assert.match(html, /Master CV Template/);
assert.match(html, /Добавить реальную вакансию/);
assert.match(html, /Исходник вакансии/);
assert.match(html, /LinkedIn/);

assert.equal(
  apiUrl("/api/vacancies/21/tailored-cv.docx", "https://job-search-agent-api-v7n6.onrender.com"),
  "https://job-search-agent-api-v7n6.onrender.com/api/vacancies/21/tailored-cv.docx"
);
assert.equal(apiUrl("https://example.com/job"), "https://example.com/job");

console.log("App smoke test passed");
