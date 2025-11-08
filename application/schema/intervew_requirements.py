interview_requirements_schema = {
    "name": "interview_requirements_extraction",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            # Basic Interview Info
            "interview_title": {"type": "string"},
            "interview_type": {
                "type": "string"
            },  # Technical, Behavioral, System Design, etc.
            "position": {"type": "string"},
            "experience_level": {"type": "string"},  # Junior, Mid, Senior, Lead, etc.
            "duration_minutes": {"type": "string"},
            # Technical Assessment Areas
            "technical_topics": {"type": "array", "items": {"type": "string"}},
            "coding_languages": {"type": "array", "items": {"type": "string"}},
            "frameworks_libraries": {"type": "array", "items": {"type": "string"}},
            "tools_technologies": {"type": "array", "items": {"type": "string"}},
            # Skill Assessment Categories
            "technical_skills_to_assess": {
                "type": "array",
                "items": {"type": "string"},
            },
            "soft_skills_to_assess": {"type": "array", "items": {"type": "string"}},
            "problem_solving_areas": {"type": "array", "items": {"type": "string"}},
            # Interview Focus Areas
            "key_focus_areas": {"type": "array", "items": {"type": "string"}},
            "must_evaluate": {"type": "array", "items": {"type": "string"}},
            "nice_to_evaluate": {"type": "array", "items": {"type": "string"}},
            # Question Types & Topics
            "question_categories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "topics": {"type": "array", "items": {"type": "string"}},
                        "difficulty": {"type": "string"},
                        "time_allocation_minutes": {"type": "string"},
                    },
                    "required": [
                        "category",
                        "topics",
                        "difficulty",
                        "time_allocation_minutes",
                    ],
                    "additionalProperties": False,
                },
            },
            # Evaluation Criteria
            "evaluation_criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion": {"type": "string"},
                        "description": {"type": "string"},
                        "weight_percentage": {"type": "string"},
                    },
                    "required": ["criterion", "description", "weight_percentage"],
                    "additionalProperties": False,
                },
            },
            # What to Judge
            "judge_for": {
                "type": "object",
                "properties": {
                    "technical_accuracy": {"type": "boolean"},
                    "code_quality": {"type": "boolean"},
                    "problem_solving_approach": {"type": "boolean"},
                    "communication_clarity": {"type": "boolean"},
                    "time_management": {"type": "boolean"},
                    "debugging_skills": {"type": "boolean"},
                    "system_design_thinking": {"type": "boolean"},
                    "best_practices": {"type": "boolean"},
                    "scalability_considerations": {"type": "boolean"},
                    "edge_case_handling": {"type": "boolean"},
                },
                "required": [
                    "technical_accuracy",
                    "code_quality",
                    "problem_solving_approach",
                    "communication_clarity",
                    "time_management",
                    "debugging_skills",
                    "system_design_thinking",
                    "best_practices",
                    "scalability_considerations",
                    "edge_case_handling",
                ],
                "additionalProperties": False,
            },
            # What NOT to Judge
            "do_not_judge": {
                "type": "object",
                "properties": {
                    "personal_background": {"type": "boolean"},
                    "accent_or_language": {"type": "boolean"},
                    "appearance": {"type": "boolean"},
                    "typing_speed": {"type": "boolean"},
                    "nervousness": {"type": "boolean"},
                    "specific_syntax": {"type": "boolean"},
                    "internet_connection_issues": {"type": "boolean"},
                    "previous_company_names": {"type": "boolean"},
                },
                "required": [
                    "personal_background",
                    "accent_or_language",
                    "appearance",
                    "typing_speed",
                    "nervousness",
                    "specific_syntax",
                    "internet_connection_issues",
                    "previous_company_names",
                ],
                "additionalProperties": False,
            },
            # Red Flags to Watch For
            "red_flags": {"type": "array", "items": {"type": "string"}},
            # Green Flags (Positive Indicators)
            "green_flags": {"type": "array", "items": {"type": "string"}},
            # Difficulty & Complexity
            "overall_difficulty": {"type": "string"},  # Easy, Medium, Hard, Expert
            "expected_pass_rate": {"type": "string"},
            # Special Instructions
            "special_instructions": {"type": "string"},
            "interviewer_notes": {"type": "string"},
            # Preparation Guidance
            "candidate_should_prepare": {"type": "array", "items": {"type": "string"}},
            # Follow-up Areas
            "common_followup_topics": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "interview_title",
            "interview_type",
            "position",
            "experience_level",
            "duration_minutes",
            "technical_topics",
            "coding_languages",
            "frameworks_libraries",
            "tools_technologies",
            "technical_skills_to_assess",
            "soft_skills_to_assess",
            "problem_solving_areas",
            "key_focus_areas",
            "must_evaluate",
            "nice_to_evaluate",
            "question_categories",
            "evaluation_criteria",
            "judge_for",
            "do_not_judge",
            "red_flags",
            "green_flags",
            "overall_difficulty",
            "expected_pass_rate",
            "special_instructions",
            "interviewer_notes",
            "candidate_should_prepare",
            "common_followup_topics",
        ],
        "additionalProperties": False,
    },
}


# Empty schema for initialization
empty_interview_schema = {
    "interview_title": "",
    "interview_type": "",
    "position": "",
    "experience_level": "",
    "duration_minutes": "",
    "technical_topics": [],
    "coding_languages": [],
    "frameworks_libraries": [],
    "tools_technologies": [],
    "technical_skills_to_assess": [],
    "soft_skills_to_assess": [],
    "problem_solving_areas": [],
    "key_focus_areas": [],
    "must_evaluate": [],
    "nice_to_evaluate": [],
    "question_categories": [],
    "evaluation_criteria": [],
    "judge_for": {
        "technical_accuracy": False,
        "code_quality": False,
        "problem_solving_approach": False,
        "communication_clarity": False,
        "time_management": False,
        "debugging_skills": False,
        "system_design_thinking": False,
        "best_practices": False,
        "scalability_considerations": False,
        "edge_case_handling": False,
    },
    "do_not_judge": {
        "personal_background": False,
        "accent_or_language": False,
        "appearance": False,
        "typing_speed": False,
        "nervousness": False,
        "specific_syntax": False,
        "internet_connection_issues": False,
        "previous_company_names": False,
    },
    "red_flags": [],
    "green_flags": [],
    "overall_difficulty": "",
    "expected_pass_rate": "",
    "special_instructions": "",
    "interviewer_notes": "",
    "candidate_should_prepare": [],
    "common_followup_topics": [],
}
