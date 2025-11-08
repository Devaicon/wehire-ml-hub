from typing import Any
from pydantic import BaseModel


class EnhanceResumeRequest(BaseModel):
    resume_json: dict[str, Any]
    job_json: dict[str, Any]


class EnhancedResumeResponse(BaseModel):
    data: dict


class EnhanceResumeWthAiRequest(BaseModel):
    resume_json: dict


class EnhanceResumeWthAiResponse(BaseModel):
    data: dict


def get_resume_enhancement_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "personalInfo": {
                "type": "object",
                "properties": {
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "mobile": {"type": "string"},
                    "maritalStatus": {"type": "string"},
                    "city": {"type": "string"},
                    "dob": {"type": "string"},
                    "gender": {"type": "string"},
                },
                "required": [
                    "firstName",
                    "lastName",
                    "email",
                    "mobile",
                    "city",
                    "gender",
                ],
                "additionalProperties": False,
            },
            "aboutMe": {
                "type": "object",
                "properties": {"about": {"type": "string"}},
                "required": ["about"],
                "additionalProperties": False,
            },
            "professionalSkills": {
                "type": "object",
                "properties": {
                    "skills": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["skills"],
                "additionalProperties": False,
            },
            "workExpereince": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "jobTitle": {"type": "string"},
                        "companyName": {"type": "string"},
                        "startEmploymentPeriod": {"type": "string"},
                        "endEmploymentPeriod": {"type": "string"},
                        "currentStatus": {"type": "boolean"},
                        "description": {"type": "string"},
                    },
                    "required": [
                        "jobTitle",
                        "companyName",
                        "startEmploymentPeriod",
                        "currentStatus",
                    ],
                    "additionalProperties": False,
                },
            },
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fieldOfStudy": {"type": "string"},
                        "universityName": {"type": "string"},
                        "degreeLevel": {
                            "type": "string",
                            "enum": [
                                "high_school",
                                "diploma",
                                "bachelors",
                                "masters",
                                "phd",
                            ],
                        },
                        "startDateOfStudy": {"type": "string"},
                        "endDateOfStudy": {"type": "string"},
                        "currentStatus": {"type": "boolean"},
                        "description": {"type": "string"},
                    },
                    "required": [
                        "fieldOfStudy",
                        "universityName",
                        "degreeLevel",
                        "startDateOfStudy",
                        "currentStatus",
                    ],
                    "additionalProperties": False,
                },
            },
            "links": {
                "type": "object",
                "properties": {
                    "socialMedias": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "link": {"type": "string", "format": "uri"},
                            },
                            "required": ["title", "link"],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["socialMedias"],
                "additionalProperties": False,
            },
            "language": {
                "type": "object",
                "properties": {
                    "languages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "langName": {"type": "string"},
                                "langLevel": {
                                    "type": "string",
                                    "enum": [
                                        "Beginner",
                                        "Intermediate",
                                        "Fluent",
                                        "Native",
                                    ],
                                },
                            },
                            "required": ["langName", "langLevel"],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["languages"],
                "additionalProperties": False,
            },
            "jobPreferences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "jobCategory": {"type": "string"},
                        "jobCategorySalary": {"type": ["string", "number"]},
                        "customSalary": {"type": "string"},
                        "acceptableContract": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "seniorityLevel": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["jobCategory"],
                    "additionalProperties": False,
                },
            },
            # "preferredJobBenefits": {
            #     "type": "array",
            #     "items": {
            #         "type": "object",
            #         "properties": {
            #             "benefits": {
            #                 "type": "array",
            #                 "items": {"type": "string"}
            #             }
            #         },
            #         "required": ["benefits"],
            #         "additionalProperties": False
            #     }
            # },
            "jobAchievements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "achievements": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["achievements"],
                    "additionalProperties": False,
                },
            },
            "filters": {
                "type": "object",
                "properties": {
                    "gender": {
                        "type": "string",
                        "enum": ["any", "male", "female", "other"],
                    },
                    "education_level": {
                        "type": "string",
                        "enum": [
                            "any",
                            "high_school",
                            "diploma",
                            "bachelors",
                            "masters",
                            "phd",
                        ],
                    },
                    "job_type": {
                        "type": "string",
                        "enum": [
                            "any",
                            "full_time",
                            "part_time",
                            "contract",
                            "internship",
                            "remote",
                        ],
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": ["any", "on_site", "hybrid", "remote"],
                    },
                },
                "required": ["gender", "education_level", "job_type", "work_mode"],
                "additionalProperties": False,
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Extract a list of relevant job role tags...",
            },
            "missing_data_to_improve": {
                "type": "string",
                "description": "Short, concise notes about missing or incomplete resume data (e.g., 'About section missing, no certifications, weak job descriptions').",
            },
        },
        "required": [
            "personalInfo",
            "aboutMe",
            "professionalSkills",
            "workExpereince",
            "education",
            "links",
            "language",
            "jobPreferences",
            # "preferredJobBenefits",
            "jobAchievements",
            "filters",
            "missing_data_to_improve",
        ],
        "additionalProperties": False,
    }
