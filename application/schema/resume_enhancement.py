from typing import Any
from pydantic import BaseModel

from enums.resume_parser import DegreeLevelEnum, EmploymentTypeEnum, FilterEducationLevelEnum, FilterGenderEnum, GenderEnum, JobTypeEnum, LanguageLevelEnum, WorkModeEnum
from utils.get_enum_values import get_enum_values


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
                    "gender": {"type": "string", "enum": get_enum_values(GenderEnum)},
                },
                "required": [
                    "firstName",
                    "lastName",
                    "email",
                    "mobile",
                    "maritalStatus",
                    "city",
                    "dob",
                    "gender",
                ],
                "additionalProperties": False,
            },
            "aboutMe": {
                "type": "object",
                "properties": {
                    "about": {
                    "type": "string",
                    "description": "A brief explain about the candidate, highlighting key skills, experiences, and career objectives."
                }
            },
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
            "workExperience": {  # ✅ corrected key spelling
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "jobTitle": {"type": "string"},
                        "companyName": {"type": "string"},
                        "location": {"type": "string"},
                        "employmentType": {"type": "string", "enum": get_enum_values(EmploymentTypeEnum)},
                        "startEmploymentPeriod": {"type": "string"},
                        "endEmploymentPeriod": {"type": "string"},
                        "currentStatus": {"type": "boolean"},
                        "description": {
                            "type": "string",
                            "description": "Explain the detailed description of roles and responsibilities."
                        },
                    },
                    "required": [
                        "jobTitle",
                        "companyName",
                        "startEmploymentPeriod",
                        "employmentType",
                        "endEmploymentPeriod",
                        "currentStatus",
                        "description",
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
                            "enum": get_enum_values(DegreeLevelEnum),
                        },
                        "startDateOfStudy": {"type": "string"},
                        "endDateOfStudy": {"type": "string"},
                        "currentStatus": {"type": "boolean"},
                        "description": {
                            "type": "string",
                            "description": "Explain the detailed description of the education background."
                        },
                    },
                    "required": [
                        "fieldOfStudy",
                        "universityName",
                        "degreeLevel",
                        "startDateOfStudy",
                        "endDateOfStudy",
                        "currentStatus",
                        "description",
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
                                "link": {"type": "string"},
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
                                    "enum": get_enum_values(LanguageLevelEnum),
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
                    "required": [
                        "jobCategory",
                        "jobCategorySalary",
                        "customSalary",
                        "acceptableContract",
                        "seniorityLevel",
                    ],
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
                        "achievements": {
                            "type": "array",
                            "items": {"type": "string"},
                        }
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
                        "enum": get_enum_values(FilterGenderEnum),
                    },
                    "education_level": {
                        "type": "string",
                        "enum": get_enum_values(FilterEducationLevelEnum),
                    },
                    "job_type": {
                        "type": "string",
                        "enum": get_enum_values(JobTypeEnum),
                    },
                    "work_mode": {
                        "type": "string",
                        "enum": get_enum_values(WorkModeEnum),
                    },
                },
                "required": [
                    "gender",
                    "education_level",
                    "job_type",
                    "work_mode",
                ],
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
                "description": (
                    "Short, concise notes about missing or incomplete resume data "
                    "(e.g., 'About section missing, no certifications, weak job descriptions')."
                ),
            },
        },
        "required": [
            "personalInfo",
            "aboutMe",
            "professionalSkills",
            "workExperience",
            "education",
            "links",
            "language",
            "jobPreferences",
            # "preferredJobBenefits",
            "jobAchievements",
            "filters",
            "tags",
            "missing_data_to_improve",
        ],
        "additionalProperties": False,
    }
