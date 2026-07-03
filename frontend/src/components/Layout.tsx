import type { ReactNode } from "react";
import { BriefcaseBusiness } from "lucide-react";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <BriefcaseBusiness aria-hidden="true" size={22} />
          <span>Job Search Agent</span>
        </div>
        <nav className="nav">
          <a href="#cv">CV Intake</a>
          <a href="#queue">Vacancy Queue</a>
          <a href="#package">Ready-to-Send</a>
          <a href="#exports">Exports</a>
        </nav>
      </aside>
      <section className="workspace">{children}</section>
    </main>
  );
}
