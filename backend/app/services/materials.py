from app.models import ApplicationMaterial, CandidateProfile, Vacancy


def generate_materials(profile: CandidateProfile, vacancy: Vacancy) -> ApplicationMaterial:
    headline = vacancy.tailored_headline or profile.target_titles.split("/")[0].strip()
    role = vacancy.title or "the role"
    company = vacancy.company or "your team"
    language = vacancy.language.lower()
    if "russian" in language:
        short_note = f"Здравствуйте! Откликаюсь на {role} в {company}. Мой профиль: {headline}."
        dm = f"Здравствуйте! Хочу откликнуться на роль {role}. Готов отправить адаптированное резюме и портфолио."
        email = f"Здравствуйте!\n\nХочу откликнуться на позицию {role} в {company}.\n\n{headline}.\n\nС уважением,\nAleksandr Grenkov"
    else:
        short_note = f"Hi, I’m applying for {role} at {company}. My profile: {headline}."
        dm = f"Hi, I’d like to apply for the {role} role at {company}. I can share a tailored CV and portfolio."
        email = f"Hi,\n\nI’d like to apply for the {role} role at {company}.\n\n{headline}.\n\nBest,\nAleksandr Grenkov"
    return ApplicationMaterial(
        vacancy_id=vacancy.id or 0,
        short_note=short_note,
        recruiter_dm=dm,
        email_cover_letter=email,
        fit_summary=f"{vacancy.priority} priority with fit score {vacancy.fit_score}.",
    )
