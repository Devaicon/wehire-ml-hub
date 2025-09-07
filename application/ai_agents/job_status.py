from openai import OpenAI
import json
from utils import config as Config

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
                        "enum": ["sent", "checked", "accepted", "rejected"],
                        "description": "The current status of the application"
                    },
                    "notification": {
                        "type": "string",
                        "description": "A short notification for the user about the status"
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
