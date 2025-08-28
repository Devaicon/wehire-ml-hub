structured_info = """
You are an intelligent resume parser. Extract the following fields from the OCR text of a CV.  
Always return the result in **valid JSON** following the exact schema below.  
Each field must follow the required type and structure exactly.  

### Expected JSON Schema
{output_keys}


### Filters  
You must review the CV text carefully and assign values for the filters only from the given options below.  
If not found, use the `"default"` value.  

{available_filters}


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

---

Here is the OCR text from the user's resume:  
{cv_text}
"""



available_filters = {
  "gender": {
    "default": "any",
    "options": [
      { "value": "any", "label": "Any gender" },
      { "value": "male", "label": "Male" },
      { "value": "female", "label": "Female" },
      { "value": "other", "label": "Other" }
    ]
  },
  "education_level": {
    "default": "any",
    "options": [
      { "value": "any", "label": "Any education" },
      { "value": "high_school", "label": "High School" },
      { "value": "diploma", "label": "Diploma" },
      { "value": "bachelors", "label": "Bachelor's Degree" },
      { "value": "masters", "label": "Master's Degree" },
      { "value": "phd", "label": "PhD" }
    ]
  },
  "job_type": {
    "default": "any",
    "options": [
      { "value": "any", "label": "Any type" },
      { "value": "full_time", "label": "Full-time" },
      { "value": "part_time", "label": "Part-time" },
      { "value": "contract", "label": "Contract" },
      { "value": "internship", "label": "Internship" },
      { "value": "remote", "label": "Remote" }
    ]
  },
  "work_modes": {
    "default": "any",
    "options": [
      { "value": "any", "label": "Any work mode" },
      { "value": "on_site", "label": "On-site" },
      { "value": "hybrid", "label": "Hybrid" },
      { "value": "remote", "label": "Remote" }
    ]
  }
}



output_keys = {
  "personalInfo": {
    "firstName": "string",
    "lastName": "string",
    "email": "string (valid email format)",
    "mobile": "string (international format if possible)",
    "maritalStatus": "string",
    "city": "string",
    "dob": "string (YYYY-MM-DD if available, else keep as in resume)",
    "gender": "string"
  },
  "aboutMe": {
    "about": "string"
    
  },
  "professionalSkills": {
    "skills": ["string", "string", "..."]
  },
  "workExpereince": [
    {
      "jobTitle": "string",
      "companyName": "string",
      "startEmploymentPeriod": "string (YYYY-MM-DD or partial)",
      "endEmploymentPeriod": "string (YYYY-MM-DD or null if current)",
      "currentStatus": "boolean",
      "description": "string"
    }
  ],
  "education": [
    {
      "fieldOfStudy": "string",
      "UniversityName": "string",
      "degreeLevel": "string (e.g., Bachelor's, Master's, PhD)",
      "startDateOfStudy": "string (YYYY-MM-DD or partial)",
      "endDateOfStudy": "string (YYYY-MM-DD or null if current)",
      "currentStatus": "boolean",
      "description": "string"
    }
  ],
  "links": {
    "socialMedias": [
      {
        "title": "string (platform name)",
        "link": "string (valid URL)"
      }
    ]
  },
  "language": {
    "languages": [
      {
        "langName": "string",
        "langLevel": "string (Beginner, Intermediate, Fluent, Native)"
      }
    ]
  },
  "jobPreferences": [
    {
      "jobCategory": "string",
      "jobCategorySalary": "string or number",
      "customSalary": "string",
      "acceptableContract": ["string", "..."],
      "seniorityLevel": ["string", "..."]
    }
  ],
  "preferredJobBenefits": [
    {
      "benefits": ["string", "..."]
    }
  ],
  "jobAchievements": [
    {
      "achievements": ["string", "..."]
    }
  ],
  "filters": {
      "gender": "",
      "education_level": "",
      "job_type": "",
      "work_mode": ""
  }
}




def get_matching_score_json(skills_weightage, work_experience_weightage, projects_weightage, qualification_weightage):

    if sum([skills_weightage, work_experience_weightage, projects_weightage, qualification_weightage]) != 100:
        raise ValueError("Total weightage must be 100.")

    matching_output_json = {
            "matched_jobs": [
                {
                    "job_id": "",
                    "job_title": "",
                    "match_score": 0,
                    "match_details": {
                        "skills": {
                            "requirement": [],
                            "candidate": [],
                            "score": 0,
                            "max_score": skills_weightage,
                            "notes": ""
                            },
                        "work_experience": {
                            "requirement": "",
                            "candidate": "",
                            "score": 0,
                            "max_score": work_experience_weightage,
                            "notes": ""
                            },
                        "projects": {
                            "requirement": "",
                            "candidate": [],
                            "score": 0,
                            "max_score": projects_weightage,
                            "notes": ""
                            },
                        "qualification": {
                            "requirement": "",
                            "candidate": "",
                            "score": 0,
                            "max_score": qualification_weightage,
                            "notes": ""
                        }
                    }
                }
              ]
            }

    return matching_output_json