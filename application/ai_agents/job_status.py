from openai import OpenAI
from security import config as Config
from fastapi import Form

client = OpenAI(api_key=Config.API_KEY)

from ai_agents.openai_functions import ask_with_instruction_json


system_prompt = """
You are an assistant for an automated job application management system.
Your task is to classify incoming job application-related emails into one of four statuses
and generate a short, clear notification message for the candidate.

### STATUS DEFINITIONS:
- checked: The company has acknowledged, confirmed receipt, or reviewed the application
           (but no further action or decision is mentioned).
- required: The company explicitly requests additional documents, actions, or information
            (e.g., resume, portfolio, certificates, references, ID proof, assessments).
- accepted: The application has been approved, shortlisted, the candidate is invited for
            interview/next round, or hired.
- rejected: The application is declined or the candidate is not moving forward.

### NOTIFICATION RULES:
- Keep the notification very short, direct, and polite.
- Always use second-person voice ("Your application...").
- Examples:
  - checked → "Your application has been reviewed by the company."
  - required → "The company needs additional information: [insert requirement(s) directly from the email]."
  - accepted → "Congratulations! Your application has been accepted."
  - rejected → "We’re sorry, your application was not successful."


  For required status, be careful, also return what required from email in notification.


### OUTPUT FORMAT:
Respond ONLY with a JSON object that matches this schema:
{
  "status": "checked" | "required" | "accepted" | "rejected",
  "notification": "string"
}
"""


def classify_email_status(email_content: str, model: str = Config.MODEL):
    message = "Classify job application emails as checked, required, accepted, or rejected; return JSON {status, notification}; notification must be one short polite line in second-person; if required, extract the exact request(s) from the email."

    system_prompt = f"""
    You are an assistant for an automated job application management system.
    Your task is to classify incoming job application-related emails into one of four statuses
    and generate a short, clear notification message for the candidate.

    ### STATUS DEFINITIONS:
    - checked: The company has acknowledged, confirmed receipt, or reviewed the application
            (but no further action or decision is mentioned).
    - required: The company explicitly requests additional documents, actions, or information
                (e.g., resume, portfolio, certificates, references, ID proof, assessments, forms).
                This status is ONLY used when the email contains a clear request for something specific.
                Be very careful to extract exactly what is requested from the email — no assumptions.
    - accepted: The application has been approved, shortlisted, the candidate is invited for
                interview/next round, or hired.
    - rejected: The application is declined or the candidate is not moving forward.

    ### NOTIFICATION RULES:
    - Keep the notification very short, direct, and polite.
    - Always use second-person voice ("Your application...").
    - Examples:
    - checked → "Your application has been reviewed by the company."
    - required → "The company needs additional information: [insert requirement(s) exactly as stated in the email]."
    - accepted → "Congratulations! Your application has been accepted."
    - rejected → "We’re sorry, your application was not successful."
    - For **required status**, never summarize vaguely — copy the specific requirement(s) mentioned
    (e.g., "updated resume", "two references", "portfolio link", "government ID copy").
    If multiple requirements are listed, include all of them in the notification.

    Given Input Email Content:
    {email_content}

    ### OUTPUT FORMAT:
    Respond ONLY with a JSON object that matches this schema:
    {{
    "status": "checked" | "required" | "accepted" | "rejected",
    "notification": "string"
    }}
    """

    result = ask_with_instruction_json(system_prompt, message)

    return result


def check_validity_email(
    company_email_content: str = Form(...), user_response_content: str = Form(...)
):
    prompt = f"""
    You are an AI email validator.

    Company Email (request):
    \"\"\"{company_email_content}\"\"\"

    User Response:
    \"\"\"{user_response_content}\"\"\"

    Tasks:
    1. Identify what the company is asking for (requirements).
    2. Check if the user's response fulfills ALL requirements.
    3. Check if the user's response contains any spam, irrelevant, or promotional content.
    4. Return a JSON with:
    - status: "valid" if all requirements are fulfilled and no spam, otherwise "not valid"
    - description: short explanation of why it's valid or not.
    """

    result = ask_with_instruction_json(prompt, "Validate the user's email response")

    return result
