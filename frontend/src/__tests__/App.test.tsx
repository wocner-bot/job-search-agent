import assert from "node:assert/strict";
import { renderToStaticMarkup } from "react-dom/server";
import App from "../App.tsx";

const html = renderToStaticMarkup(<App />);

assert.match(html, /Job Search Agent/);
assert.match(html, /Import Current Package/);
assert.match(html, /Run Analysis/);
assert.match(html, /Paste master CV text/);

console.log("App smoke test passed");
