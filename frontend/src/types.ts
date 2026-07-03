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
  tailored_headline: string;
  top_match_keywords: string;
  gaps_risks: string;
  adaptation_strategy: string;
}

export interface ApplicationMaterial {
  vacancy_id: number;
  short_note: string;
  recruiter_dm: string;
  email_cover_letter: string;
  fit_summary: string;
}
