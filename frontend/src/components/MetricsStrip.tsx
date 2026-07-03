import type { Vacancy } from "../types";

export function MetricsStrip({ vacancies }: { vacancies: Vacancy[] }) {
  const veryHigh = vacancies.filter((vacancy) => vacancy.priority === "Very High").length;
  const ready = vacancies.filter((vacancy) => vacancy.submit_status === "Ready to send").length;
  const sent = vacancies.filter((vacancy) => vacancy.submit_status === "Sent").length;
  return (
    <section className="metrics">
      <div><span>Total</span><strong>{vacancies.length}</strong></div>
      <div><span>Very High</span><strong>{veryHigh}</strong></div>
      <div><span>Ready</span><strong>{ready}</strong></div>
      <div><span>Sent</span><strong>{sent}</strong></div>
    </section>
  );
}
