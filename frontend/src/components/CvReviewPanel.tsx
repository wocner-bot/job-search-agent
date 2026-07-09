import type { CandidateReview } from "../types";

export function CvReviewPanel({ review }: { review: CandidateReview | null }) {
  if (!review) return null;
  return (
    <section className="panel cv-review-panel">
      <div className="panel-header">
        <div>
          <h2>Анализ исходного CV</h2>
          <p>Рекрутерская версия CV и 20 должностей, для которых профиль подходит лучше всего.</p>
        </div>
      </div>
      <div className="cv-review-grid">
        <label>
          <span>Исходное CV</span>
          <textarea readOnly value={review.source_cv} />
        </label>
        <label>
          <span>Улучшенная версия CV</span>
          <textarea readOnly value={review.improved_cv} />
        </label>
      </div>
      <div className="role-match-section">
        <h2>20 подходящих должностей и ключевые слова</h2>
        <div className="role-match-grid">
          {review.role_matches.map((role) => (
            <article className="role-match-card" key={`${role.rank}-${role.title}`}>
              <div>
                <span>#{role.rank}</span>
                <strong>{role.title}</strong>
              </div>
              <p>{role.headline}</p>
              <small>{role.keywords.join(" • ")}</small>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
