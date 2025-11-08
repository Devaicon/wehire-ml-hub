import json
from schema.job import (
    JobMailResponse,
    JobMatchRequest,
    JobMatchResponse,
    get_mail_schema,
)
from ai_agents.prompts.job.job_match import SYSTEM_PROMPT as MATCH_SYSTEM_PROMPT
from ai_agents.prompts.job.generate_job_email import (
    SYSTEM_PROMPT as EMAIL_SYSTEM_PROMPT,
)
from schema.job import get_matching_score_json
from ai_agents.llm.openai import OpenAI_LLM
from security.config import (
    API_KEY,
    skills_weightage,
    work_experience_weightage,
    projects_weightage,
    qualification_weightage,
)

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore


def resume_with_job_matcher(payload: JobMatchRequest) -> JobMatchResponse:
    resume_json = payload.resume_json
    jobs_json = payload.jobs_json

    messages = [
        {
            "role": "system",
            "content": MATCH_SYSTEM_PROMPT.format(
                resume_json=resume_json,
                jobs_json=jobs_json,
            ),
        },
        {"role": "user", "content": "match jobs with resume data and return jobs"},
    ]
    response = llm.generate_json(
        schema=get_matching_score_json(
            skills_weightage=skills_weightage,
            work_experience_weightage=work_experience_weightage,
            projects_weightage=projects_weightage,
            qualification_weightage=qualification_weightage,
        ),
        model="gpt-4o-mini",
        messages=messages,
    )
    content = "{}"
    if response and getattr(response, "choices", None):
        try:
            content = response.choices[0].message.content or "{}"
        except Exception:
            content = "{}"
    return JobMatchResponse(data=json.loads(content))


def generate_job_mail(job_json: str, resume_json: str) -> JobMailResponse:
    # job_json will be a dict in string form, so we parse it to extract job_id
    job_data = json.loads(job_json)
    resume_data = json.loads(resume_json)

    messages = [
        {
            "role": "system",
            "content": EMAIL_SYSTEM_PROMPT.format(
                resume_data=json.dumps(resume_data, indent=2),
                job_data=json.dumps(job_data, indent=2),
            ),
        },
        {
            "role": "user",
            "content": "Write subject and email content for job application",
        },
    ]
    response = llm.generate_json(
        schema=get_mail_schema(), model="gpt-4o-mini", messages=messages
    )
    content = "{}"
    if response and getattr(response, "choices", None):
        try:
            content = response.choices[0].message.content or "{}"
        except Exception:
            content = "{}"
    return JobMailResponse(data=json.loads(content))
