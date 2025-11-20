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

class GenerateJobMailRequest(BaseModel):
    job_json: dict[str, Any]
    resume_json: dict[str, Any]

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
                                        "score": {
                                            "type": "number",
                                            "description": "Score for skills matching."
                                        },
                                        "max_score": {
                                            "type": "number",
                                            "description": f"Maximum possible score for skills matching. Must be {skills_weightage}.",
                                        },
                                        "notes": {
                                            "type": "string",
                                            "description": "Notes about skills matching."
                                        },
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                    "additionalProperties": False,
                                },
                                "work_experience": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {
                                            "type": "string",
                                            "description": "Work experience requirement."
                                        },
                                        "candidate": {
                                            "type": "string",
                                            "description": "Candidate's work experience."
                                        },
                                        "score": {
                                            "type": "number",
                                            "description": "Score for work experience matching."
                                        },
                                        "max_score": {
                                            "type": "number",
                                            "description": f"Maximum possible score for work experience. Must be {work_experience_weightage}.",
                                        },
                                        "notes": {
                                            "type": "string",
                                            "description": "Notes about work experience matching."
                                        },
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                    "additionalProperties": False,
                                },
                                "projects": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {
                                            "type": "string",
                                            "description": "Projects requirement."
                                        },
                                        "candidate": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Candidate's relevant projects."
                                        },
                                        "score": {
                                            "type": "number",
                                            "description": "Score for projects matching."
                                        },
                                        "max_score": {
                                            "type": "number",
                                            "description": f"Maximum possible score for projects. Must be {projects_weightage}.",
                                        },
                                        "notes": {
                                            "type": "string",
                                            "description": "Notes about projects matching."
                                        },
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                    "additionalProperties": False,
                                },
                                "qualification": {
                                    "type": "object",
                                    "properties": {
                                        "requirement": {
                                            "type": "string",
                                            "description": "Qualification requirement."
                                        },
                                        "candidate": {
                                            "type": "string",
                                            "description": "Candidate's qualification."
                                        },
                                        "score": {
                                            "type": "number",
                                            "description": "Score for qualification matching."
                                        },
                                        "max_score": {
                                            "type": "number",
                                            "description": f"Maximum possible score for qualification. Must be {qualification_weightage}.",
                                        },
                                        "notes": {
                                            "type": "string",
                                            "description": "Notes about qualification matching."
                                        },
                                    },
                                    "required": [
                                        "requirement",
                                        "candidate",
                                        "score",
                                        "max_score",
                                        "notes",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                            "required": [
                                "skills",
                                "work_experience",
                                "projects",
                                "qualification",
                            ],
                            "additionalProperties": False,
                        },
                    },
                    "required": ["job_id", "job_title", "match_score", "match_details"],
                    "additionalProperties": False,
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
