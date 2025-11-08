import json
from ai_agents.prompts.email.classify_email import (
    SYSTEM_PROMPT as CLASSIFY_EMAIL_SYSTEM_PROMPT,
)
from ai_agents.prompts.email.validate_email import (
    SYSTEM_PROMPT as VALIDATE_EMAIL_SYSTEM_PROMPT,
)
from ai_agents.llm.openai import OpenAI_LLM
from schema.email import (
    EmailClasifyResponse,
    EmailValidateResponse,
    get_clasify_email_schema,
    get_validate_email_schema,
)
from security.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore


def classify_email_status(email_content: str) -> EmailClasifyResponse:
    message = "Classify job application emails as checked, required, accepted, or rejected; return JSON {status, notification}; notification must be one short polite line in second-person; if required, extract the exact request(s) from the email."

    messages = [
        {
            "role": "system",
            "content": CLASSIFY_EMAIL_SYSTEM_PROMPT.format(email_content=email_content),
        },
        {"role": "user", "content": message},
    ]
    response = llm.generate_json(
        schema=get_clasify_email_schema(),
        messages=messages,
        model="gpt-4o-mini",
    )

    content = "{}"
    if response and getattr(response, "choices", None):
        try:
            content = response.choices[0].message.content or "{}"
        except Exception:
            content = "{}"

    return EmailClasifyResponse(data=json.loads(content))


def check_validity_email(
    company_email_content: str, user_response_content: str
) -> EmailValidateResponse:
    messages = [
        {
            "role": "system",
            "content": VALIDATE_EMAIL_SYSTEM_PROMPT.format(
                company_email_content=company_email_content,
                user_response_content=user_response_content,
            ),
        },
        {"role": "user", "content": "Validate the user's email response"},
    ]
    response = llm.generate_json(
        schema=get_validate_email_schema(),
        messages=messages,
        model="gpt-4o-mini",
    )
    content = "{}"
    if response and getattr(response, "choices", None):
        try:
            content = response.choices[0].message.content or "{}"
        except Exception:
            content = "{}"

    return EmailValidateResponse(data=json.loads(content))
