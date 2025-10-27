resume_extraction_schema = {
            "name": "resume_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "personal_info": {
                        "type": "object",
                        "properties": {
                            "full_name": {"type": "string"},
                            "email": {"type": "string"},
                            "phone": {"type": "string"},
                            "linkedin": {"type": "string"},
                            "github": {"type": "string"},
                            "portfolio": {"type": "string"},
                            "location": {"type": "string"}
                        },
                        "required": ["full_name", "email", "phone", "linkedin", "github", "portfolio", "location"],
                        "additionalProperties": False
                    },
                    "professional_summary": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "experience": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "company": {"type": "string"},
                                "position": {"type": "string"},
                                "location": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "duration": {"type": "string"},
                                "responsibilities": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["company", "position", "location", "start_date", "end_date", "duration", "responsibilities"],
                            "additionalProperties": False
                        }
                    },
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "institution": {"type": "string"},
                                "degree": {"type": "string"},
                                "field_of_study": {"type": "string"},
                                "graduation_year": {"type": "string"},
                                "gpa": {"type": "string"},
                                "location": {"type": "string"}
                            },
                            "required": ["institution", "degree", "field_of_study", "graduation_year", "gpa", "location"],
                            "additionalProperties": False
                        }
                    },
                    "certifications": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "issuer": {"type": "string"},
                                "date": {"type": "string"}
                            },
                            "required": ["name", "issuer", "date"],
                            "additionalProperties": False
                        }
                    },
                    "projects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "technologies": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["name", "description", "technologies"],
                            "additionalProperties": False
                        }
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["personal_info", "professional_summary", "skills", "experience", "education", "certifications", "projects", "languages"],
                "additionalProperties": False
            }
        }

empty_schema = {
            "personal_info": {
                "full_name": "",
                "email": "",
                "phone": "",
                "linkedin": "",
                "github": "",
                "portfolio": "",
                "location": ""
            },
            "professional_summary": "",
            "skills": [],
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "languages": []
        }