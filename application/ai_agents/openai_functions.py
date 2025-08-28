import json
from openai import OpenAI
from utils import config as Config
from utils import config as Config


client = OpenAI(api_key=Config.API_KEY)


def ask_with_instruction_json(
        instruction, message, model=Config.MODEL):  
        client = OpenAI(api_key=Config.API_KEY)
        chat_completion = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": message},
            ] 
        )

        out = chat_completion.choices[0].message.content

        print("response:: ", out)

        return out


def ask_with_instruction(
        instruction, message, model=Config.MODEL, temperature=Config.TEMPERATURE
    ):  
        client = OpenAI(api_key=Config.API_KEY)
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": message},
            ],
            temperature=temperature,
        )

        out = chat_completion.choices[0].message.content
        return out




def parse_resume_as_structured(
    cv_text: str,
    system_instructions: str,
    resume_schema: dict,
    model: str = Config.MODEL
):
    client = OpenAI(api_key=Config.API_KEY)

    # Merge schema into system instructions
    schema_instructions = f"""
    You must output strictly valid JSON following this schema:
    {json.dumps(resume_schema, indent=2)}
    """

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_instructions + "\n\n" + schema_instructions
            },
            {
                "role": "user",
                "content": cv_text
            }
        ]
    )

    try:
        parsed = response.output_text
    except json.JSONDecodeError:
        raise ValueError("Model did not return valid JSON")

    return parsed











