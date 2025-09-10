from openai import OpenAI
import json
from utils import config as Config
from fastapi import FastAPI, Form

client = OpenAI(api_key=Config.API_KEY)

def classify_email_status(email_content: str, model: str = Config.MODEL):
    functions = [
        {
            "name": "classify_application_status",
            "description": "Classify job application email into a status and generate a short notification",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["sent", "checked", "required", "accepted", "rejected"],
                        "description": (
                            "The current status of the application:\n"
                            "- sent: Application has been submitted but no response yet.\n"
                            "- checked: Company has reviewed or acknowledged the application.\n"
                            "- required: Company has requested additional documents, information, or actions.\n"
                            "- accepted: Application has passed the phase (e.g., shortlisted, interview cleared, or hired).\n"
                            "- rejected: Application was declined by the company."
                        )
                    },
                    "notification": {
                        "type": "string",
                        "description": (
                            "A short, clear notification for the user:\n"
                            "- sent: 'Your application has been submitted successfully.'\n"
                            "- checked: 'Your application has been reviewed by the company.'\n"
                            "- required: 'The company needs additional information: [extract the exact requirement(s) from the email].'\n"
                            "- accepted: 'Congratulations! Your application has been accepted.'\n"
                            "- rejected: 'We’re sorry, your application was not successful.'"
                        )
                    }
                },
                "required": ["status", "notification"]
            }
        }
    ]


    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a classifier that reads job application emails and determines their status. Respond only with the function arguments."
            },
            {
                "role": "user",
                "content": email_content
            }
        ],
        functions=functions,
        function_call={"name": "classify_application_status"}
    )

    # Extract the JSON string from function_call arguments
    args = response.choices[0].message.function_call.arguments
    result = json.loads(args)

    # Ensure response contains both keys
    return {
        "status": result["status"],
        "notification": result["notification"]
    }



from ai_agents.openai_functions import ask_with_instruction_json

def check_validity_email(
    company_email_content: str = Form(...),
    user_response_content: str = Form(...)
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