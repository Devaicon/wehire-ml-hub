from typing import Any, Literal
from pydantic import BaseModel
from dataclasses import dataclass

from enums.interview import DifficultyLevel, QuestionSource


# Define Metrics schema
@dataclass
class ExtractionResumeMetrics:
    """Track extraction performance metrics"""

    total_pages: int
    chunks_processed: int
    api_calls: int
    total_time: float
    cost_estimate: float

    def __str__(self):
        return f"""
╔══════════════════════════════════════════════╗
║          EXTRACTION METRICS                  ║
╠══════════════════════════════════════════════╣
║ Total Pages:      {self.total_pages:>4}      ║
║ Chunks Processed: {self.chunks_processed:>4} ║
║ API Calls:        {self.api_calls:>4}        ║
║ Time Elapsed:     {self.total_time:>6.2f}s   ║
║ Est. Cost:        ${self.cost_estimate:>6.4f}║
╚══════════════════════════════════════════════╝
"""


# Define main Response schema
class ExtractionResumeResponse(BaseModel):
    id: str
    status: str
    data: Any  # Use more specific type if you know the structure of extracted_data
    metrics: ExtractionResumeMetrics


@dataclass
class ExtractionJdMetrics:
    """Track extraction performance metrics"""

    api_calls: int
    input_tokens: int
    output_tokens: int
    cost_estimate: float

    def __str__(self):
        return f"""
╔══════════════════════════════════════════════╗
║      JOB EXTRACTION METRICS                  ║
╠══════════════════════════════════════════════╣
║ API Calls:        {self.api_calls:>4}        ║
║ Input Tokens:     {self.input_tokens:>4}     ║
║ Output Tokens:    {self.output_tokens:>4}    ║
║ Est. Cost:        ${self.cost_estimate:>6.4f}║
╚══════════════════════════════════════════════╝
"""


class JobDescription(BaseModel):
    id: str
    status: str
    data: Any
    metrics: ExtractionJdMetrics


@dataclass
class InterviewConfig:
    """Configuration for interview question generation"""

    difficulty_level: DifficultyLevel
    question_source: QuestionSource
    include_intro_questions: bool
    interview_duration_minutes: int  # Changed from total_questions
    question_length: Literal["short", "medium", "long"]
    client_questions: list[str] = None  # type: ignore
    client_questions_count: int = 0  # Only used if HYBRID mode
    buffer_time_percent: float = 0.15  # 15% buffer for transitions, rapport building

    def __post_init__(self):
        if self.client_questions is None:
            self.client_questions = []
        if self.question_source == QuestionSource.HYBRID and not self.client_questions:
            raise ValueError("Client questions required for HYBRID mode")

        # Calculate number of questions based on time
        self.total_questions = self._calculate_question_count()

    def _calculate_question_count(self) -> int:
        """Calculate how many questions fit in the given time"""
        # Answer time per question (in minutes)
        answer_times = {
            "short": 2,  # 1-2 minutes
            "medium": 4,  # 3-5 minutes
            "long": 7,  # 5-10 minutes
        }

        # Add 1 minute per question for asking the question + brief discussion
        time_per_question = answer_times[self.question_length] + 1

        # Apply buffer (e.g., 15% for intro, transitions, wrap-up)
        available_time = self.interview_duration_minutes * (
            1 - self.buffer_time_percent
        )

        # Calculate questions
        question_count = int(available_time / time_per_question)

        # Ensure at least 1 question
        return max(1, question_count)


@dataclass
class InterviewMetrics:
    """Metrics for interview generation"""

    api_calls: int
    input_tokens: int
    output_tokens: int
    cost_estimate: float
    questions_generated: int
    interview_duration_minutes: int
    estimated_actual_duration_minutes: int
    buffer_time_minutes: float

    def __str__(self):
        return f"""
╔════════════════════════════════════════════════════╗
║      INTERVIEW GENERATION METRICS                  ║
╠════════════════════════════════════════════════════╣
║ Target Duration:      {self.interview_duration_minutes:>3} minutes            ║
║ Estimated Actual:     {self.estimated_actual_duration_minutes:>3} minutes            ║
║ Buffer Time:          {self.buffer_time_minutes:>3.1f} minutes            ║
║ Questions Generated:  {self.questions_generated:>3}                    ║
║                                                    ║
║ API Calls:            {self.api_calls:>4}                   ║
║ Input Tokens:         {self.input_tokens:>6}                 ║
║ Output Tokens:        {self.output_tokens:>6}                 ║
║ Est. Cost:            ${self.cost_estimate:>7.4f}              ║
╚════════════════════════════════════════════════════╝
"""


class InterviewRequirementExtractionResponse(BaseModel):
    id: str
    status: str
    data: Any
    metrics: ExtractionJdMetrics


class InterviewQuestionResponse(BaseModel):
    id: str
    jd_id: str
    resume_id: str
    intervew_req_id: str
    status: str
    data: Any  # Use more specific type if you know the structure of generated questions
    metrics: InterviewMetrics


class InterviewQuestionRequest(BaseModel):
    resume_id: str
    jd_id: str
    interview_req_id: str
    include_intro_questions: bool = True
    difficulty_level: DifficultyLevel = DifficultyLevel.EASY
    question_source: QuestionSource = QuestionSource.AI_GENERATED
    interview_duration_minutes: int = 10
    question_length: Literal["short", "medium", "long"] = "short"
    client_questions: list[str] | None = None
    client_questions_count: int | None = 0
    model_config = {"arbitrary_types_allowed": True}


class QAEvaluationRequest(BaseModel):
    generated_question_id: str
    question_id: str
    is_followup: bool = False
    followup_index: int | None = None
    previous_question: str
    user_answer: str
