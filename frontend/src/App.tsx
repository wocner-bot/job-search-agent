import { Layout } from "./components/Layout.tsx";

export default function App() {
  return (
    <Layout>
      <header className="workspace-header">
        <div>
          <h1>Vacancy Queue</h1>
          <p>Ready-to-send application workspace for tailored CVs and recruiter messages.</p>
        </div>
      </header>
      <section id="cv" className="panel">
        <h2>CV Intake</h2>
        <textarea placeholder="Paste master CV text here" />
      </section>
      <section id="queue" className="panel">
        <h2>Vacancy Queue</h2>
        <p>Import the current package or add vacancies manually.</p>
      </section>
    </Layout>
  );
}
