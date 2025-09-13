resume_schema = {
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
                "gender": {"type": "string"}
            },
            "required": ["firstName", "lastName", "email", "mobile", "city", "gender"],
            "additionalProperties": False
        },
        "aboutMe": {
            "type": "object",
            "properties": {
                "about": {"type": "string"}
            },
            "required": ["about"],
            "additionalProperties": False
        },
        "professionalSkills": {
            "type": "object",
            "properties": {
                "skills": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["skills"],
            "additionalProperties": False
        },
        "workExpereince": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "jobTitle": {"type": "string"},
                    "companyName": {"type": "string"},
                    "startEmploymentPeriod": {"type": "string"},
                    "endEmploymentPeriod": {"type": ["string", "null"]},
                    "currentStatus": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "required": ["jobTitle", "companyName", "startEmploymentPeriod", "currentStatus"],
                "additionalProperties": False
            }
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
                        "enum": ["high_school", "diploma", "bachelors", "masters", "phd"]
                    },
                    "startDateOfStudy": {"type": "string"},
                    "endDateOfStudy": {"type": ["string", "null"]},
                    "currentStatus": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "required": ["fieldOfStudy", "universityName", "degreeLevel", "startDateOfStudy", "currentStatus"],
                "additionalProperties": False
            }
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
                            "link": {"type": "string", "format": "uri"}
                        },
                        "required": ["title", "link"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["socialMedias"],
            "additionalProperties": False
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
                                "enum": ["Beginner", "Intermediate", "Fluent", "Native"]
                            }
                        },
                        "required": ["langName", "langLevel"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["languages"],
            "additionalProperties": False
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
                        "items": {"type": "string"}
                    },
                    "seniorityLevel": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["jobCategory"],
                "additionalProperties": False
            }
        },
        "preferredJobBenefits": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "benefits": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["benefits"],
                "additionalProperties": False
            }
        },
        "jobAchievements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "achievements": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["achievements"],
                "additionalProperties": False
            }
        },
        "filters": {
            "type": "object",
            "properties": {
                "gender": {"type": "string", "enum": ["any", "male", "female", "other"]},
                "education_level": {"type": "string", "enum": ["any", "high_school", "diploma", "bachelors", "masters", "phd"]},
                "job_type": {"type": "string", "enum": ["any", "full_time", "part_time", "contract", "internship", "remote"]},
                "work_mode": {"type": "string", "enum": ["any", "on_site", "hybrid", "remote"]}
            },
            "required": ["gender", "education_level", "job_type", "work_mode"],
            "additionalProperties": False
        },

        "tags": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "description": """Extract a list of relevant job role tags from the given resume data.

        Only include job titles that are directly supported by the candidate’s experience, projects, or qualifications.

        Tags must represent clear job categories such as:

        Data Scientist, Machine Learning Engineer, Frontend Developer, Backend Developer, Full Stack Developer, DevOps Engineer, Cloud Engineer, Mobile Developer, Cybersecurity Specialist, UI/UX Designer, Database Administrator, Project Manager, Business Analyst, etc.

        Do not include specific skills, tools, technologies, programming languages, or certifications.

        Do not guess or assume unrelated roles — only include jobs clearly aligned with the resume content.

        Avoid duplicates or near-duplicate roles.

        Always return at least 5 distinct, job-ready role tags the person is qualified for, based on the resume.

        🎯 Tags must be:

        Concise

        Directly inferred from resume data

        Job-focused

        Non-redundant

        Relevant for job applications"""
    }



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
        "preferredJobBenefits",
        "jobAchievements",
        "filters"
    ],
    "additionalProperties": False
}



system_information = """
You are an intelligent resume parser. Extract the following fields from the OCR text of a CV.  
Always return the result in **valid JSON** strictly following the provided schema.  
Each field must follow the required type and structure exactly.  

### Filters  
You must review the CV text carefully and assign values for the filters only from the given options.  
If not found, use the `"default"` value.  

### Parsing Instructions:
1. **Missing Data**:  
   - If a field is missing, return it as an empty string `""` (for strings) or an empty array `[]` (for lists).  

2. **Dates**:  
   - Normalize to `YYYY-MM-DD` format whenever possible.  
   - If only partial information is available (e.g., year/month), keep as `"YYYY"` or `"YYYY-MM"`.  
   - Use `null` for `endEmploymentPeriod` or `endDateOfStudy` if the position/study is current.  

3. **Booleans**:  
   - `currentStatus` must be strictly `true` or `false`.  

4. **Validation Rules**:  
   - `email` must be a valid email format.  
   - `mobile` should be in international format if possible (`+countrycode...`).  
   - `links.socialMedias[].link` must be a valid URL.  
   - `language.langLevel` must be one of: `Beginner`, `Intermediate`, `Fluent`, `Native`.  
   - `degreeLevel` must match common education terms (e.g., High School, Diploma, Bachelor's, Master's, PhD).  

5. **Filters Handling**:  
   - Each filter (`gender`, `education_level`, `job_type`, `work_mode`) must strictly use one of the defined `options` values.  
   - If not explicitly found in the CV text, set to `"any"`.  

6. **Output Restrictions**:  
   - Do not add extra fields outside of the given schema.  
   - Do not change key names.  
   - Ensure the final response is strictly valid JSON.  
"""





enhance_cv_prompt = """
You are an AI assistant that enhances a candidate’s résumé JSON to better match a given job description JSON. 
The goal is not to fabricate information, but to intelligently reorder and highlight existing résumé data so that 
the most relevant skills, projects, and experiences appear prominently.

Rules:
1. Always preserve all original résumé information. Do not delete content.
2. Identify relevant skills, projects, experiences, and education that closely match the job description.
3. Move these relevant items to the top of their respective sections (skills, projects, experiences).
   - Keep original ordering for unrelated items, placing them after relevant ones.
4. If certain résumé items can be slightly renamed or summarized to better match job wording 
   (e.g., “ML model development” → “Machine Learning model development for business applications”), 
   you may enhance the text without changing factual accuracy.
5. Ensure the JSON schema structure stays consistent with `resume_schema`.
6. Add a new field `"job_relevance_score"` (0–100) for each project and skill, based on how well they match the job description.
7. Keep formatting clean and structured for AI search and AI apply pipelines.

"""


enhance_cv_prompt_json = """
You are an AI assistant that enhances a candidate’s résumé JSON to better match a given job description JSON. 
The goal is not to fabricate information, but to intelligently reorder and highlight existing résumé data so that 
the most relevant skills, projects, and experiences appear prominently.

Rules:
1. Always preserve all original résumé information. Do not delete content.
2. Identify relevant skills, projects, experiences, and education that closely match the job description.
3. Move these relevant items to the top of their respective sections (skills, projects, experiences).
   - Keep original ordering for unrelated items, placing them after relevant ones.
4. If certain résumé items can be slightly renamed or summarized to better match job wording 
   (e.g., “ML model development” → “Machine Learning model development for business applications”), 
   you may enhance the text without changing factual accuracy.
5. Ensure the JSON schema structure stays consistent with `resume_schema`.
6. Add a new field `"job_relevance_score"` (0–100) for each project and skill, based on how well they match the job description.
7. Keep formatting clean and structured for AI search and AI apply pipelines.



job_description_json:
{job_description_json}


candidate_resume_json: 
{candidate_resume_json}


return the enhanced résumé strictly in valid JSON format following the original schema, with the new relevance scores included.


"""