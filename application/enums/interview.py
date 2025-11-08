from enum import Enum


class OCRMethod(str, Enum):
    vision = "vision"
    tesseract = "tesseract"
    none = "none"


class QuestionSource(Enum):
    """Question source types"""

    CLIENT_PROVIDED = "client_provided"
    AI_GENERATED = "ai_generated"
    HYBRID = "hybrid"


class DifficultyLevel(Enum):
    """Difficulty levels for interview questions"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewPhase(Enum):
    """Interview phases"""

    FIRST = "first_round"
    SECOND = "second_round"
    FINAL = "final_round"
