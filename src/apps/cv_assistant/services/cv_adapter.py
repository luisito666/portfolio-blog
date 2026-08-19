"""CV adaptation prompt builder and AI response parser.

Builds the system + user prompts for the LLM to adapt the base CV
to a specific job description, and parses/validates the structured
JSON response.
"""
import json
import re

from apps.portfolio.models import Experience


def _format_base_cv_data(base_cv_data):
    """Serialize the CV context dict into a plain-text block.

    Shared by the adaptation prompt (Generate CV endpoint) and the chat
    system prompt so both always describe the exact same base CV.

    Args:
        base_cv_data: Context dict from cv_builder.build_cv_context() with keys
                      'summary', 'experiences', 'skill_columns', 'education_list',
                      'certifications'. The values are Django model instances
                      (or SimpleNamespace for adapted data).

    Returns:
        Plain-text block with summary, experiences, skills, education and
        certifications.
    """
    # Extract summary text
    summary_obj = base_cv_data.get('summary')
    if summary_obj is not None:
        summary_text = getattr(summary_obj, 'content', '') or ''
    else:
        summary_text = 'No summary available.'

    # Extract experiences (Django model instances or SimpleNamespace)
    experiences_raw = base_cv_data.get('experiences', [])
    if not experiences_raw:
        experiences_text = "  No experiences listed."
    else:
        exp_lines = []
        for exp in experiences_raw:
            exp_id = getattr(exp, 'id', getattr(exp, 'pk', 'N/A'))
            position = getattr(exp, 'position', 'N/A')
            company = getattr(exp, 'company', 'N/A')
            description = getattr(exp, 'description', getattr(exp, 'description_html', 'N/A'))
            exp_lines.append(
                f"  - ID: {exp_id}, Position: {position}, Company: {company}, "
                f"Description: {description}"
            )
        experiences_text = "\n".join(exp_lines)

    # Extract skills from skill_columns (list of 3 lists, each with {'category', 'skills': [Skill]})
    skill_columns = base_cv_data.get('skill_columns', [])
    skill_names = []
    for col in skill_columns:
        for item in col:
            for skill in item.get('skills', []):
                skill_names.append(getattr(skill, 'name', str(skill)))
    skills_text = ", ".join(skill_names) if skill_names else "No skills listed."

    # Extract education
    education_raw = base_cv_data.get('education_list', [])
    if not education_raw:
        education_text = "  No education listed."
    else:
        edu_lines = []
        for edu in education_raw:
            degree = getattr(edu, 'degree', 'N/A')
            field = getattr(edu, 'field_of_study', 'N/A')
            institution = getattr(edu, 'institution', 'N/A')
            edu_lines.append(f"  - {degree} in {field} at {institution}")
        education_text = "\n".join(edu_lines)

    # Extract certifications
    cert_raw = base_cv_data.get('certifications', [])
    if not cert_raw:
        certifications_text = "  No certifications listed."
    else:
        cert_lines = []
        for cert in cert_raw:
            name = getattr(cert, 'name', 'N/A')
            org = getattr(cert, 'issuing_organization', 'N/A')
            cert_lines.append(f"  - {name} ({org})")
        certifications_text = "\n".join(cert_lines)

    return f"""Professional Summary:
{summary_text}

Work Experience:
{experiences_text}

Skills: {skills_text}

Education:
{education_text}

Certifications:
{certifications_text}"""


def build_system_prompt(base_cv_data):
    """Build the system prompt with base CV data and adaptation rules.

    Used by the Generate CV endpoint. The LLM must return a structured
    JSON with the adapted CV.

    Args:
        base_cv_data: Context dict from cv_builder.build_cv_context() with keys
                      'summary', 'experiences', 'skill_columns', 'education_list',
                      'certifications'. The values are Django model instances
                      (or SimpleNamespace for adapted data).

    Returns:
        System prompt string for the LLM.
    """
    cv_block = _format_base_cv_data(base_cv_data)

    return f"""You are a CV adaptation assistant. Given the base CV data and a job description, \
adapt the CV to match the job requirements.

BASE CV DATA:

{cv_block}

RULES:
1. Keep the same CV structure — do not add or remove sections.
2. Adapt language to match the job description keywords and requirements.
3. DO NOT invent new experiences, companies, positions, or dates.
4. DO NOT change company names, position titles, or dates.
5. Only rewrite the professional summary and experience descriptions to highlight \
relevant skills for the job.
6. Return your response as valid JSON with this exact structure:
   {{
     "summary": "adapted summary text",
     "experiences": [
       {{"id": <experience_id>, "description_adapted": "new description text"}}
     ]
   }}
   The "id" must be the numeric ID of the experience from the base data above.
   Only include experiences that need adaptation; you may omit unchanged ones.
7. If the job description is in Spanish, write the adapted content in Spanish. \
If in English, write in English.
8. Return ONLY the JSON — no markdown, no code blocks, no commentary."""


def build_chat_system_prompt(base_cv_data, job_description=None):
    """Build the system prompt for the interactive chat assistant.

    Unlike ``build_system_prompt`` (used by the Generate CV endpoint), this
    prompt positions the CV and the job description as read-only context.
    The chat answers questions and gives advice; it NEVER produces the full
    adapted CV — that is an explicit separate action ("Generate CV" button)
    to avoid burning tokens on unrequested CV dumps.

    Args:
        base_cv_data: Context dict from cv_builder.build_cv_context().
        job_description: Full text of the job posting being discussed (optional).

    Returns:
        System prompt string for the LLM.
    """
    cv_block = _format_base_cv_data(base_cv_data)
    job_block = job_description or "No job description provided."

    return f"""You are an expert career coach and CV advisor embedded in a job-application \
tracker. The user owns the CV below and is evaluating the job description shown.

BASE CV DATA (read-only context):

{cv_block}

JOB DESCRIPTION (read-only context):

{job_block}

RULES:
1. Answer the user's questions about job fit, interviews, negotiations and career \
strategy. Be direct, honest and specific — ground every claim in the CV and the \
job description provided above.
2. Respond in the same language the user writes in.
3. NEVER output a full adapted CV in the chat: no rewritten professional summary \
and no rewritten experience sections. Generating the adapted CV is a separate \
explicit action (the "Generate CV" button); the chat is for analysis and advice only.
4. You may quote short, specific fragments of the CV when useful for your analysis, \
but never produce rewritten CV sections.
5. If the user explicitly asks you to generate or rewrite the CV in the chat, \
politely decline, tell them to use the "Generate CV" button, and optionally \
summarize in one or two lines what the adaptation should focus on.
6. Do not invent experiences, skills, companies or dates that are not in the CV."""


def build_adaptation_prompt(job_description, user_instructions=None, conversation_history=None):
    """Build the user message with the job description and optional guidance.

    Args:
        job_description: The full text of the job posting/description.
        user_instructions: Optional additional guidance from the admin
                           (e.g., "Make it shorter", "Emphasize Kubernetes").
        conversation_history: Optional list of chat message dicts
                             ({"role": "user"|"assistant", "content": str})
                             from the conversation the user had with the
                             assistant before pressing "Generate CV". The
                             gaps/strengths/emphases discussed there inform
                             the adaptation.

    Returns:
        User message string for the LLM.
    """
    prompt = f"Please adapt my CV for the following job description:\n\n{job_description}"

    if conversation_history:
        history_lines = []
        for m in conversation_history:
            role = m.get("role")
            speaker = "User" if role == "user" else "Assistant"
            history_lines.append(f"{speaker}: {m.get('content', '')}")
        prompt += (
            "\n\nCONVERSATION HISTORY with the candidate (additional context for "
            "the adaptation — the strengths, gaps and emphases discussed here "
            "should inform how the CV is tailored, but never introduce facts "
            "that are not in the base CV):\n\n"
            + "\n\n".join(history_lines)
        )

    if user_instructions:
        prompt += f"\n\nAdditional instructions:\n{user_instructions}"
    return prompt


def parse_ai_response(ai_response):
    """Parse the AI's JSON response and validate experience IDs.

    Handles responses wrapped in markdown code blocks (```json...```).

    Args:
        ai_response: Raw text response from the LLM.

    Returns:
        Dict: {"summary": str, "experiences": [{"id": int, "description_adapted": str}]}

    Raises:
        ValueError: If the response cannot be parsed or contains unknown
                    experience IDs.
    """
    # Strip markdown code blocks if present
    cleaned = ai_response.strip()
    code_block_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(code_block_pattern, cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

    # Parse JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse AI response as JSON: {e}")

    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object.")

    summary = data.get('summary', '')
    experiences = data.get('experiences', [])

    if not isinstance(experiences, list):
        raise ValueError("'experiences' must be a list.")

    # Validate all experience IDs exist in the base data
    valid_ids = set(Experience.objects.values_list('id', flat=True))
    parsed_experiences = []

    for exp in experiences:
        if not isinstance(exp, dict):
            raise ValueError(f"Experience entry must be a dict, got: {type(exp)}")
        exp_id = exp.get('id')
        if exp_id is None:
            raise ValueError("Experience entry missing 'id' field.")
        try:
            exp_id = int(exp_id)
        except (TypeError, ValueError):
            raise ValueError(f"Experience ID must be an integer, got: {exp_id}")

        if exp_id not in valid_ids:
            raise ValueError(
                f"Unknown experience ID {exp_id}. "
                f"Valid IDs are: {sorted(valid_ids)}"
            )

        description_adapted = exp.get('description_adapted', '')
        if not isinstance(description_adapted, str):
            raise ValueError(
                f"Experience {exp_id}: 'description_adapted' must be a string."
            )

        parsed_experiences.append({
            'id': exp_id,
            'description_adapted': description_adapted,
        })

    return {
        'summary': str(summary),
        'experiences': parsed_experiences,
    }