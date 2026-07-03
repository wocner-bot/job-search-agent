import assert from "node:assert/strict";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../App.tsx";

const html = renderToStaticMarkup(<App />);

assert.match(html, /Job Search Agent/);
assert.match(html, /CV Intake/);
assert.match(html, /Vacancy Queue/);

console.log("App smoke test passed");
