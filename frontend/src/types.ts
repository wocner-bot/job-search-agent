export type ApplicationStatus = "Draft" | "Ready to send" | "Sent" | "Follow-up" | "Rejected" | "Archived";

export interface Vacancy {
  id: number;
  external_id: string;
  rank: number | null;
  source: string;
  company: string;
  title: string;
  location: string;
  posted: string;
  date_status: string;
  language: string;
  fit_score: number;
  priority: string;
  submit_status: ApplicationStatus;
  next_action: string;
  cv_file_path: string;
  pdf_file_path: string;
  png_preview_path: string;
  source_url: string;
  description_raw: string;
  requirements: string;
  responsibilities: string;
  vacancy_keywords: string;
  tailored_headline: string;
  top_match_keywords: string;
  gaps_risks: string;
  adaptation_strategy: string;
}

export interface VacancyDraft {
  external_id: string;
  source: string;
  company: string;
  title: string;
  location: string;
  language: string;
  source_url: string;
  description_raw: string;
  requirements: string;
  responsibilities: string;
}

export interface ApplicationMaterial {
  vacancy_id: number;
  short_note: string;
  recruiter_dm: string;
  email_cover_letter: string;
  fit_summary: string;
}

export interface CandidateRoleMatch {
  rank: number;
  title: string;
  fit_score: number;
  priority: string;
  headline: string;
  keywords: string[];
  strategy: string;
}

export interface CandidateReview {
  source_cv: string;
  improved_cv: string;
  role_matches: CandidateRoleMatch[];
}
