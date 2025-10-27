jd_extraction_schema = {
            "name": "job_requirements_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "company": {"type": "string"},
                    "job_type": {"type": "string"},
                    "experience_level": {"type": "string"},
                    "years_of_experience": {"type": "string"},
                    "required_skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "preferred_skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "technical_requirements": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "required_qualifications": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "preferred_qualifications": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "education": {
                        "type": "object",
                        "properties": {
                            "minimum_degree": {"type": "string"},
                            "field_of_study": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["minimum_degree", "field_of_study"],
                        "additionalProperties": False
                    },
                    "certifications": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "responsibilities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "key_responsibilities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "salary_range": {
                        "type": "object",
                        "properties": {
                            "min": {"type": "string"},
                            "max": {"type": "string"},
                            "currency": {"type": "string"},
                            "period": {"type": "string"}
                        },
                        "required": ["min", "max", "currency", "period"],
                        "additionalProperties": False
                    },
                    "benefits": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "location": {"type": "string"},
                    "remote_status": {"type": "string"},
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "soft_skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "industry": {"type": "string"},
                    "reporting_to": {"type": "string"}
                },
                "required": [
                    "job_title", "company", "job_type", "experience_level", "years_of_experience",
                    "required_skills", "preferred_skills", "technical_requirements",
                    "required_qualifications", "preferred_qualifications", "education", 
                    "certifications", "responsibilities", "key_responsibilities", "salary_range",
                    "benefits", "location", "remote_status", "languages", "soft_skills",
                    "industry", "reporting_to"
                ],
                "additionalProperties": False
            }
        }