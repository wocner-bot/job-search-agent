import { apiUrl } from "../api.ts";
import { priorityLabel } from "../labels.ts";
import type { CandidateReview, Vacancy } from "../types";

function keywordsForVacancy(vacancy: Vacancy): string {
  return vacancy.top_match_keywords || vacancy.vacancy_keywords || "Ключевые слова будут уточнены после анализа.";
}

export function CvReviewPanel({ review, vacancies }: { review: CandidateReview | null; vacancies: Vacancy[] }) {
  if (!review) return null;
  return (
    <section className="panel cv-review-panel">
      <div className="panel-header">
        <div>
          <div className="cv-review-title-row">
            <span className="cv-review-badge">Senior recruiter review</span>
            <h2>Анализ исходного CV</h2>
          </div>
          <p>Рекрутерская версия CV и единый финальный список вакансий с соответствием исходному профилю.</p>
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
      <div className="final-vacancy-section">
        <h2>Финальные вакансии и соответствие исходному CV</h2>
        {vacancies.length === 0 ? (
          <p className="final-vacancy-empty">Финальный список появится здесь после поиска по источникам.</p>
        ) : (
          <div className="final-vacancy-grid">
            {vacancies.map((vacancy) => (
              <article className="final-vacancy-card" key={vacancy.id}>
                <div className="final-vacancy-heading">
                  <span>#{vacancy.rank ?? vacancy.id}</span>
                  <strong>{vacancy.title}</strong>
                </div>
                <p>{vacancy.company || vacancy.source}</p>
                <small>{keywordsForVacancy(vacancy)}</small>
                <div className="final-vacancy-meta">
                  <span>{vacancy.source || "Источник"}</span>
                  <span>Совпадение с CV: {vacancy.fit_score}%</span>
                  <span>{priorityLabel(vacancy.priority)}</span>
                </div>
                <div className="final-vacancy-links">
                  {vacancy.source_url && (
                    <a href={vacancy.source_url} target="_blank" rel="noreferrer">
                      Открыть вакансию
                    </a>
                  )}
                  {vacancy.cv_file_path && (
                    <a href={apiUrl(vacancy.cv_file_path)} target="_blank" rel="noreferrer">
                      Открыть CV
                    </a>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
