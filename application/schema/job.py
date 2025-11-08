from typing import Any

from pydantic import BaseModel


class JobMatchRequest(BaseModel):
    resume_json: dict[str, Any]
    jobs_json: list[dict[str, Any]]


class JobMatchResponse(BaseModel):
    data: dict[str, Any]


class JobMailResponse(BaseModel):
    data: dict[str, Any]


class JobMatchDbRequest(BaseModel):
    user_id: str
    resume_json: dict[str, Any]


class JobMatchDbResponse(BaseModel):
    status: str


class JobMatchDbErrorResponse(BaseModel):
    err_status: bool
    err_message: str
    data: dict


def get_matching_score_json(
    skills_weightage,
    work_experience_weightage,
    projects_weightage,
    qualification_weightage,
):
    if (
        sum(
            [
                skills_weightage,
                work_experience_weightage,
                projects_weightage,
                qualification_weightage,
            ]
        )
        != 100
    ):
        raise ValueError("Total weightage must be 100.")

    matching_output_json = {
        "type": "object",
        "properties": {
            "matched_jobs": {
                "type": "array",
                "description": "List of jobs matched with the candidate profile.",
                "items": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Unique identifier for the job.",
                        },
                        "job_title": {
                            "type": "string",
                            "description": "Title of the job position.",
                        },
                        "match_score": {
                            "type": "number",
                            "description": "Overall match score for the candidate on this job.",
                        },
                        "match_details": {
                            "type": "object",
                            "properties": {
                                "skills": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Required skills for the job.",
                                        },
                                        "candidate": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Skills possessed by the candidate.",
                                        },
                                        "score": {"type": "number"},
                                        "max_score": {
                                            "type": "number",
                                            "description": "Maximum possible score for skills matching.",
                                        },
                                        "notes": {"type": "string"},
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                },
                                "work_experience": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {"type": "string"},
                                        "candidate": {"type": "string"},
                                        "score": {"type": "number"},
                                        "max_score": {"type": "number"},
                                        "notes": {"type": "string"},
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                },
                                "projects": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {"type": "string"},
                                        "candidate": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                        "score": {"type": "number"},
                                        "max_score": {"type": "number"},
                                        "notes": {"type": "string"},
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                },
                                "qualification": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {"type": "string"},
                                        "candidate": {"type": "string"},
                                        "score": {"type": "number"},
                                        "max_score": {"type": "number"},
                                        "notes": {"type": "string"},
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                },
                            },
                            "required": [
                                "skills",
                                "work_experience",
                                "projects",
                                "qualification",
                            ],
                        },
                    },
                    "required": ["job_id", "job_title", "match_score", "match_details"],
                },
            }
        },
        "required": ["matched_jobs"],
        "additionalProperties": False,
    }

    return matching_output_json


def get_mail_schema():
    return {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "description": "The employerId from job_data.",
            },
            "subject": {
                "type": "string",
                "description": "The subject line of the generated email.",
            },
            "email_content": {
                "type": "string",
                "description": "The full body text of the generated email.",
            },
        },
        "required": ["job_id", "subject", "email_content"],
        "additionalProperties": False,
    }
