from typing import Any
from pydantic import BaseModel


class EmailClasifyResponse(BaseModel):
    data: dict[str, Any]


class EmailValidateResponse(BaseModel):
    data: dict[str, Any]


def get_clasify_email_schema():
    return {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["checked", "required", "accepted", "rejected"],
                "description": "The current status of the process or action.",
            },
            "notification": {
                "type": "string",
                "description": "A human-readable message describing the status or action taken.",
            },
        },
        "required": ["status", "notification"],
        "additionalProperties": False,
    }


def get_validate_email_schema():
    return {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["valid", "not valid"]},
            "description": {"type": "string"},
        },
        "required": ["status", "description"],
        "additionalProperties": False,
    }
