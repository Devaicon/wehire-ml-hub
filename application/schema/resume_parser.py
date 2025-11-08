from typing import List, Optional, Union
from pydantic import BaseModel, Field
from utils.get_enum_values import get_enum_values
from enums.resume_parser import (
    FilterEducationLevelEnum,
    FilterGenderEnum,
    GenderEnum,
    JobTypeEnum,
    WorkModeEnum,
    DegreeLevelEnum,
    AwardCategoryEnum,
    AwardLevelEnum,
    LanguageLevelEnum,
    ProjectTypeEnum,
)


class PersonalInfo(BaseModel):
    firstName: str = ""
    lastName: str = ""
    email: str = ""
    mobile: str = ""
    maritalStatus: str = ""
    city: str = ""
    dob: str = ""
    gender: FilterGenderEnum = FilterGenderEnum.ANY
    website: str = ""
    location: str = ""


class AboutMe(BaseModel):
    about: str = ""


class ProfessionalSkills(BaseModel):
    skills: List[str] = Field(default_factory=list)


class WorkExperience(BaseModel):
    jobTitle: str = ""
    companyName: str = ""
    location: str = ""
    employmentType: str = ""
    startEmploymentPeriod: str = ""
    endEmploymentPeriod: Optional[str] = None
    currentStatus: bool = False
    description: str = ""


class Education(BaseModel):
    universityName: str = ""
    degreeLevel: str = ""
    fieldOfStudy: str = ""
    startDateOfStudy: str = ""
    endDateOfStudy: Optional[str] = None
    currentStatus: bool = False
    location: str = ""
    gpa: str = ""
    hasMinor: bool = False
    minorField: str = ""
    minorGPA: str = ""
    relevantCoursework: str = ""
    achievements: str = ""
    honors: str = ""


class WorkProject(BaseModel):
    projectName: str = ""
    projectLink: str = ""
    projectDescription: str = ""
    technologiesUsed: List[str] = Field(default_factory=list)
    projectType: str = ""
    projectStartDate: str = ""
    projectEndDate: str = ""
    projectStatus: str = ""


class SocialMedia(BaseModel):
    title: str = ""
    link: str = ""


class Links(BaseModel):
    socialMedias: List[SocialMedia] = Field(default_factory=list)


class Language(BaseModel):
    langName: str = ""
    langLevel: str = ""


class Languages(BaseModel):
    languages: List[Language] = Field(default_factory=list)


class JobPreference(BaseModel):
    jobCategory: str = ""
    jobCategorySalary: Union[str, int] = ""
    customSalary: str = ""
    acceptableContract: List[str] = Field(default_factory=list)
    seniorityLevel: List[str] = Field(default_factory=list)


# class PreferredJobBenefit(BaseModel):
#     benefits: List[str] = Field(default_factory=list)


class JobAchievement(BaseModel):
    AwardName: str = ""
    OrganizationName: str = ""
    DateReceived: str = ""
    AwardDescription: str = ""
    AwardStartDate: str = ""
    AwardEndDate: str = ""
    AwardLevel: str = ""
    AwardCategory: str = ""


class Filters(BaseModel):
    gender: FilterGenderEnum = FilterGenderEnum.ANY
    education_level: FilterEducationLevelEnum = FilterEducationLevelEnum.ANY
    job_type: JobTypeEnum = JobTypeEnum.ANY
    work_mode: WorkModeEnum = WorkModeEnum.ANY


class ResumeData(BaseModel):
    personalInfo: PersonalInfo = Field(default_factory=PersonalInfo)
    aboutMe: AboutMe = Field(default_factory=AboutMe)
    professionalSkills: ProfessionalSkills = Field(default_factory=ProfessionalSkills)
    workExperience: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    workProjects: List[WorkProject] = Field(default_factory=list)
    links: Links = Field(default_factory=Links)
    language: Languages = Field(default_factory=Languages)
    jobPreferences: List[JobPreference] = Field(default_factory=list)
    # preferredJobBenefits: List[PreferredJobBenefit] = Field(default_factory=list)
    jobAchievements: List[JobAchievement] = Field(default_factory=list)
    filters: Filters = Field(default_factory=Filters)
    tags: List[str] = Field(default_factory=list, min_length=1)


def get_resume_extraction_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "personalInfo": {
                "type": "object",
                "properties": {
                    "firstName": {"type": "string"},
                    "lastName": {"type": "string"},
                    "email": {"type": "string"},
                    "mobile": {"type": "string"},
                    "maritalStatus": {"type": "string"},
                    "city": {"type": "string"},
                    "dob": {"type": "string"},
                    "gender": {"type": "string", "enum": get_enum_values(GenderEnum)},
                    "website": {"type": "string"},
                    "location": {"type": "string"},
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
                    "website",
                    "location",
                ],
                "additionalProperties": False,
            },
            "aboutMe": {
                "type": "object",
                "properties": {
                    "about": {"type": "string"},
                },
                "required": ["about"],
                "additionalProperties": False,
            },
            "professionalSkills": {
                "type": "object",
                "properties": {
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["skills"],
                "additionalProperties": False,
            },
            "workExperience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "jobTitle": {"type": "string"},
                        "companyName": {"type": "string"},
                        "location": {"type": "string"},
                        "employmentType": {"type": "string"},
                        "startEmploymentPeriod": {"type": "string"},
                        "endEmploymentPeriod": {"type": "string"},
                        "currentStatus": {"type": "boolean"},
                        "description": {"type": "string"},
                    },
                    "required": [
                        "jobTitle",
                        "companyName",
                        "location",
                        "employmentType",
                        "startEmploymentPeriod",
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
                        "universityName": {"type": "string"},
                        "degreeLevel": {
                            "type": "string",
                            "enum": get_enum_values(DegreeLevelEnum),
                        },
                        "fieldOfStudy": {"type": "string"},
                        "startDateOfStudy": {"type": "string"},
                        "endDateOfStudy": {"type": "string"},
                        "currentStatus": {"type": "boolean"},
                        "location": {"type": "string"},
                        "gpa": {"type": "string"},
                        "hasMinor": {"type": "boolean"},
                        "minorField": {"type": "string"},
                        "minorGPA": {"type": "string"},
                        "relevantCoursework": {"type": "string"},
                        "achievements": {"type": "string"},
                        "honors": {"type": "string"},
                    },
                    "required": [
                        "universityName",
                        "degreeLevel",
                        "fieldOfStudy",
                        "startDateOfStudy",
                        "endDateOfStudy",
                        "currentStatus",
                        "location",
                        "gpa",
                        "hasMinor",
                        "minorField",
                        "minorGPA",
                        "relevantCoursework",
                        "achievements",
                        "honors",
                    ],
                    "additionalProperties": False,
                },
            },
            "workProjects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "projectName": {"type": "string"},
                        "projectLink": {"type": "string"},  # Removed format: uri
                        "projectDescription": {"type": "string"},
                        "technologiesUsed": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "projectType": {
                            "type": "string",
                            "enum": get_enum_values(ProjectTypeEnum),
                        },
                        "projectStartDate": {"type": "string"},
                        "projectEndDate": {"type": "string"},
                        "projectStatus": {"type": "string"},
                    },
                    "required": [
                        "projectName",
                        "projectLink",
                        "projectDescription",
                        "technologiesUsed",
                        "projectType",
                        "projectStartDate",
                        "projectEndDate",
                        "projectStatus",
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
                                "link": {"type": "string"},  # Removed format: uri
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
            #                 "items": {"type": "string"},
            #             }
            #         },
            #         "required": ["benefits"],
            #         "additionalProperties": False,
            #     }
            # },
            "jobAchievements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "AwardName": {"type": "string"},
                        "OrganizationName": {"type": "string"},
                        "DateReceived": {"type": "string"},
                        "AwardDescription": {"type": "string"},
                        "AwardStartDate": {"type": "string"},
                        "AwardEndDate": {"type": "string"},
                        "AwardLevel": {
                            "type": "string",
                            "enum": get_enum_values(AwardLevelEnum),
                        },
                        "AwardCategory": {
                            "type": "string",
                            "enum": get_enum_values(AwardCategoryEnum),
                        },
                    },
                    "required": [
                        "AwardName",
                        "OrganizationName",
                        "DateReceived",
                        "AwardDescription",
                        "AwardStartDate",
                        "AwardEndDate",
                        "AwardLevel",
                        "AwardCategory",
                    ],
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
                "required": ["gender", "education_level", "job_type", "work_mode"],
                "additionalProperties": False,
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        },
        "required": [
            "personalInfo",
            "aboutMe",
            "professionalSkills",
            "workExperience",
            "education",
            "workProjects",
            "links",
            "language",
            "jobPreferences",
            # "preferredJobBenefits",
            "jobAchievements",
            "filters",
            "tags",
        ],
        "additionalProperties": False,
    }


# emp= {
#             "personal_info": {
#                 "full_name": "",
#                 "email": "",
#                 "phone": "",
#                 "linkedin": "",
#                 "github": "",
#                 "portfolio": "",
#                 "location": ""
#             },
#             "professional_summary": "",
#             "skills": [],
#             "experience": [],
#             "education": [],
#             "certifications": [],
#             "projects": [],
#             "languages": []
#         }

# res_req = {
#             "name": "resume_extraction",
#             "strict": True,
#             "schema": {
#                 "type": "object",
#                 "properties": {
#                     "personal_info": {
#                         "type": "object",
#                         "properties": {
#                             "full_name": {"type": "string"},
#                             "email": {"type": "string"},
#                             "phone": {"type": "string"},
#                             "linkedin": {"type": "string"},
#                             "github": {"type": "string"},
#                             "portfolio": {"type": "string"},
#                             "location": {"type": "string"}
#                         },
#                         "required": ["full_name", "email", "phone", "linkedin", "github", "portfolio", "location"],
#                         "additionalProperties": False
#                     },
#                     "professional_summary": {"type": "string"},
#                     "skills": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     },
#                     "experience": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "company": {"type": "string"},
#                                 "position": {"type": "string"},
#                                 "location": {"type": "string"},
#                                 "start_date": {"type": "string"},
#                                 "end_date": {"type": "string"},
#                                 "duration": {"type": "string"},
#                                 "responsibilities": {
#                                     "type": "array",
#                                     "items": {"type": "string"}
#                                 }
#                             },
#                             "required": ["company", "position", "location", "start_date", "end_date", "duration", "responsibilities"],
#                             "additionalProperties": False
#                         }
#                     },
#                     "education": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "institution": {"type": "string"},
#                                 "degree": {"type": "string"},
#                                 "field_of_study": {"type": "string"},
#                                 "graduation_year": {"type": "string"},
#                                 "gpa": {"type": "string"},
#                                 "location": {"type": "string"}
#                             },
#                             "required": ["institution", "degree", "field_of_study", "graduation_year", "gpa", "location"],
#                             "additionalProperties": False
#                         }
#                     },
#                     "certifications": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "name": {"type": "string"},
#                                 "issuer": {"type": "string"},
#                                 "date": {"type": "string"}
#                             },
#                             "required": ["name", "issuer", "date"],
#                             "additionalProperties": False
#                         }
#                     },
#                     "projects": {
#                         "type": "array",
#                         "items": {
#                             "type": "object",
#                             "properties": {
#                                 "name": {"type": "string"},
#                                 "description": {"type": "string"},
#                                 "technologies": {
#                                     "type": "array",
#                                     "items": {"type": "string"}
#                                 }
#                             },
#                             "required": ["name", "description", "technologies"],
#                             "additionalProperties": False
#                         }
#                     },
#                     "languages": {
#                         "type": "array",
#                         "items": {"type": "string"}
#                     }
#                 },
#                 "required": ["personal_info", "professional_summary", "skills", "experience", "education", "certifications", "projects", "languages"],
#                 "additionalProperties": False
#             }
#         }

# empty_schema = {
#             "personal_info": {
#                 "full_name": "",
#                 "email": "",
#                 "phone": "",
#                 "linkedin": "",
#                 "github": "",
#                 "portfolio": "",
#                 "location": ""
#             },
#             "professional_summary": "",
#             "skills": [],
#             "experience": [],
#             "education": [],
#             "certifications": [],
#             "projects": [],
#             "languages": []
#         }
