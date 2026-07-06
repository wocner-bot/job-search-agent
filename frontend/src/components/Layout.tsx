import type { ReactNode } from "react";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <main className="app-shell">
      <section className="workspace">{children}</section>
    </main>
  );
}
