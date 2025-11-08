interview_question_schema = {
    "name": "interview_questions_generation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_id": {"type": "integer"},
                        "question": {"type": "string"},
                        "category": {"type": "string"},
                        "difficulty": {"type": "string"},
                        "expected_answer_type": {"type": "string"},
                        "estimated_time_minutes": {"type": "integer"},
                        "key_points": {"type": "array", "items": {"type": "string"}},
                        "follow_up_questions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "why_asked": {"type": "string"},
                        "relevance_to_cv": {"type": "string"},
                    },
                    "required": [
                        "question_id",
                        "question",
                        "category",
                        "difficulty",
                        "expected_answer_type",
                        "estimated_time_minutes",
                        "key_points",
                        "follow_up_questions",
                        "why_asked",
                        "relevance_to_cv",
                    ],
                    "additionalProperties": False,
                },
            },
            "interview_summary": {
                "type": "object",
                "properties": {
                    "total_questions": {"type": "integer"},
                    "difficulty_distribution": {
                        "type": "object",
                        "properties": {
                            "easy": {"type": "integer"},
                            "medium": {"type": "integer"},
                            "hard": {"type": "integer"},
                        },
                        "required": ["easy", "medium", "hard"],
                        "additionalProperties": False,
                    },
                    "question_categories": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "estimated_interview_duration_minutes": {"type": "integer"},
                },
                "required": [
                    "total_questions",
                    "difficulty_distribution",
                    "question_categories",
                    "estimated_interview_duration_minutes",
                ],
                "additionalProperties": False,
            },
        },
        "required": ["questions", "interview_summary"],
        "additionalProperties": False,
    },
}
