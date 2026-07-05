import assert from "node:assert/strict";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../App.tsx";

const html = renderToStaticMarkup(<App />);

assert.match(html, /Job Search Agent/);
assert.match(html, /Подбор вакансий по CV/);
assert.match(html, /Вставьте CV текстом/);
assert.doesNotMatch(html, /Файл с вакансиями/);
assert.match(html, /20 должностей/);
assert.match(html, /Подобрать вакансии/);
assert.match(html, /Tailored CV/);
assert.match(html, /Master CV Template/);

console.log("App smoke test passed");
