"""Service for assembling the context used to render the CV PDF.

The context assembly previously lived inline in
``apps.portfolio.views.GeneratePDFView``. It is extracted here so both the
public PDF download path and any AI-adapted CV path can share the same
template and rendering pipeline.
"""

import types

import markdown
from django.conf import settings

from apps.portfolio.models import (
    Certification,
    Education,
    Experience,
    Skill,
    SocialSettings,
    Summary,
)


def _build_skill_columns():
    """Group skills by category and split the categories across 3 columns.

    Mirrors the original logic from ``GeneratePDFView``.
    """
    skills = Skill.objects.all()

    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)

    categories = list(skills_by_category.items())
    skill_columns = [[], [], []]
    for i, (cat, cat_skills) in enumerate(categories):
        skill_columns[i % 3].append({'category': cat, 'skills': cat_skills})

    return skill_columns


def _adapted_experiences(adapted_data):
    """Build a list of objects exposing the attributes the PDF template needs
    (``position``, ``company``, ``location``, ``start_date``, ``end_date``,
    ``current`` and ``description_html``) from the adapted data provided by
    the AI adaptation flow.

    ``adapted_data`` is expected to be a dict with the keys:
        - ``summary``: str (the adapted summary text)
        - ``experiences``: list of dicts with ``id``, ``position``,
          ``company`` and ``description_adapted``.
    """
    adapted_exp_map = {e['id']: e for e in adapted_data.get('experiences', [])}

    base_experiences = Experience.objects.all()
    adapted = []
    for exp in base_experiences:
        match = adapted_exp_map.get(exp.id)
        if match is None:
            # Not adapted -> use the original (markdown-rendered) description
            description_html = markdown.markdown(exp.description)
            adapted.append(types.SimpleNamespace(
                position=exp.position,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                current=exp.current,
                description_html=description_html,
            ))
            continue

        adapted.append(types.SimpleNamespace(
            position=match.get('position', exp.position),
            company=match.get('company', exp.company),
            location=exp.location,
            start_date=exp.start_date,
            end_date=exp.end_date,
            current=exp.current,
            description_html=markdown.markdown(match['description_adapted']),
        ))
    return adapted


def build_cv_context(adapted_data=None):
    """Assemble the context dict consumed by ``portfolio/cv_pdf.html``.

    When ``adapted_data`` is ``None`` the context is built from the base
    portfolio models exactly like the original ``GeneratePDFView`` did.

    When ``adapted_data`` is provided it must be a dict with the keys
    ``summary`` (str) and ``experiences`` (list of dicts with ``id``,
    ``position``, ``company`` and ``description_adapted``). The adapted
    values are used instead of the base models, while skills and
    social settings are always pulled from the base models.
    """
    # Always derived from the base portfolio
    certifications = Certification.objects.all()
    for cert in certifications:
        if cert.description:
            cert.description_html = markdown.markdown(cert.description)

    education_list = Education.objects.all()
    for edu in education_list:
        if edu.description:
            edu.description_html = markdown.markdown(edu.description)

    skill_columns = _build_skill_columns()
    social_settings = SocialSettings.objects.first()

    if adapted_data is None:
        summary = Summary.objects.first()
        if summary:
            summary.content_html = markdown.markdown(summary.content)

        experiences = Experience.objects.all()
        for exp in experiences:
            exp.description_html = markdown.markdown(exp.description)

        summary_obj = summary
    else:
        adapted_summary = adapted_data.get('summary', '')
        summary_obj = types.SimpleNamespace(
            title='Professional Summary',
            content=adapted_summary,
            content_html=markdown.markdown(adapted_summary),
        )
        experiences = _adapted_experiences(adapted_data)

    context = {
        'summary': summary_obj,
        'experiences': experiences,
        'certifications': certifications,
        'education_list': education_list,
        'skill_columns': skill_columns,
        'social_settings': social_settings,
        'pdf_owner_name': settings.PDF_OWNER_NAME,
    }
    return context