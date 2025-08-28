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
                    "UniversityName": {"type": "string"},
                    "degreeLevel": {
                        "type": "string",
                        "enum": ["high_school", "diploma", "bachelors", "masters", "phd"]
                    },
                    "startDateOfStudy": {"type": "string"},
                    "endDateOfStudy": {"type": ["string", "null"]},
                    "currentStatus": {"type": "boolean"},
                    "description": {"type": "string"}
                },
                "required": ["fieldOfStudy", "UniversityName", "degreeLevel", "startDateOfStudy", "currentStatus"],
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
