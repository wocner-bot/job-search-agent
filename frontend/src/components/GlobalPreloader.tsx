export function GlobalPreloader({ label }: { label: string }) {
  return (
    <div className="global-preloader" role="status" aria-live="polite" aria-busy="true">
      <div className="preloader-spinner" aria-hidden="true" />
      <strong>{label}</strong>
    </div>
  );
}
