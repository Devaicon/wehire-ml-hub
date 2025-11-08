import json
import os
from typing import Generator
from uuid import uuid4
from fastapi import HTTPException
from ai_agents.pdf_extractor.jd_extractor import JobDescriptionExtractor
from ai_agents.generation.question_generation import InterviewQuestionGenerator
from ai_agents.generation.question_evaluation import evaluation, re_generate_question
from ai_agents.pdf_extractor.interview_requirement_extractor import (
    InterviewRequirementsExtractor,
)
from enums.interview import DifficultyLevel, QuestionSource
from utils.find_resume import get_uploaded_file_names, load_json_from_file
from schema.interview import (
    ExtractionJdMetrics,
    ExtractionResumeResponse,
    ExtractionResumeMetrics,
    InterviewConfig,
    InterviewMetrics,
    InterviewQuestionRequest,
    InterviewQuestionResponse,
    InterviewRequirementExtractionResponse,
    JobDescription,
    QAEvaluationRequest,
)
from ai_agents.pdf_extractor.resume_extractor import OptimizedResumeExtractor

BASE_UPLOAD_PATH = os.path.join("public", "static", "uploads")

UPLOAD_JSON_DIR = os.path.join(BASE_UPLOAD_PATH, "resume_json")
UPLOAD_JSON_JD_DIR = os.path.join(BASE_UPLOAD_PATH, "jd_json")
UPLOAD_JSON_QUESTION_DIR = os.path.join(BASE_UPLOAD_PATH, "question_json")
UPLOAD_JSON_INTERVIEW_REQ_DIR = os.path.join(BASE_UPLOAD_PATH, "interview_req_json")

for path in [
    UPLOAD_JSON_DIR,
    UPLOAD_JSON_JD_DIR,
    UPLOAD_JSON_QUESTION_DIR,
    UPLOAD_JSON_INTERVIEW_REQ_DIR,
]:
    os.makedirs(path, exist_ok=True)


def pdf_extractor_optimized(
    temp_path: str, ocr_method: str
) -> ExtractionResumeResponse:
    try:
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Use fewer workers for better concurrent handling
        extractor = OptimizedResumeExtractor(
            pages_per_chunk=5, max_workers=3, model="gpt-4o-mini"
        )

        extracted_data, metrics = extractor.extract_from_pdf(
            pdf_path=temp_path,
            ocr_method=ocr_method,
            verbose=False,  # Disable verbose in production
        )

        metrics = ExtractionResumeMetrics(
            total_pages=metrics.total_pages,
            chunks_processed=metrics.chunks_processed,
            api_calls=metrics.api_calls,
            total_time=metrics.total_time,
            cost_estimate=metrics.cost_estimate,
        )
        UUID = str(uuid4())
        response = ExtractionResumeResponse(
            id=str(UUID), status="success", data=extracted_data, metrics=metrics
        )

        file_name = f"{UUID}.json"  # generate unique name
        file_path = os.path.join(UPLOAD_JSON_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response.dict(), f, indent=4)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


def jd_extractor(text: str):
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    extractor = JobDescriptionExtractor(openai_api_key=api_key)

    # Extract requirements
    result, metrics = extractor.extract(text)
    print("Extraction Result:", result)

    UUID = str(uuid4())
    metrics = ExtractionJdMetrics(
        api_calls=metrics.api_calls,
        input_tokens=metrics.input_tokens,
        output_tokens=metrics.output_tokens,
        cost_estimate=metrics.cost_estimate,
    )
    response = JobDescription(id=UUID, status="success", data=result, metrics=metrics)

    file_name = f"{UUID}.json"  # generate unique name
    file_path = os.path.join(UPLOAD_JSON_JD_DIR, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response.dict(), f, indent=4)

    return response


def interview_requirement_extractor(text: str):
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    extractor = InterviewRequirementsExtractor(openai_api_key=api_key)

    # Extract requirements
    result, metrics = extractor.extract(text)
    print("Extraction Result:", result)

    UUID = str(uuid4())
    metrics = ExtractionJdMetrics(
        api_calls=metrics.api_calls,
        input_tokens=metrics.input_tokens,
        output_tokens=metrics.output_tokens,
        cost_estimate=metrics.cost_estimate,
    )
    response = InterviewRequirementExtractionResponse(
        id=UUID, status="success", data=result, metrics=metrics
    )

    file_name = f"{UUID}.json"  # generate unique name
    file_path = os.path.join(UPLOAD_JSON_INTERVIEW_REQ_DIR, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(response.dict(), f, indent=4)

    return response


def interview_question_generation(
    request: InterviewQuestionRequest,
) -> InterviewQuestionResponse:
    try:
        resume_id = (request.resume_id).strip()
        jd_id = (request.jd_id).strip()
        interview_req_id = (request.interview_req_id).strip()
        print(f"Resume ID: {resume_id}, JD ID: {jd_id}")
        if resume_id == "":
            raise ValueError("Please provide a valid resume ID.")
        if jd_id == "":
            raise ValueError("Please provide a valid job description ID.")

        if interview_req_id == "":
            raise ValueError("Please provide a valid Interview Requirement ID.")

        get_resumes_id = get_uploaded_file_names(UPLOAD_JSON_DIR, ".json")

        if resume_id not in get_resumes_id:
            raise ValueError("Please provide a valid resume ID.")

        get_jds_id = get_uploaded_file_names(UPLOAD_JSON_JD_DIR, ".json")
        if jd_id not in get_jds_id:
            raise ValueError("Please provide a valid job description ID.")

        get_interview_req_id = get_uploaded_file_names(
            UPLOAD_JSON_INTERVIEW_REQ_DIR, ".json"
        )
        if interview_req_id not in get_interview_req_id:
            raise ValueError("Please provide a valid Interview Requirement ID.")

        if request.difficulty_level not in DifficultyLevel:
            raise ValueError("Invalid difficulty level.")

        if request.question_source not in QuestionSource:
            raise ValueError("Invalid question source.")

        api_key = os.getenv("API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        config = InterviewConfig(
            include_intro_questions=request.include_intro_questions,
            difficulty_level=request.difficulty_level,
            question_source=request.question_source,
            interview_duration_minutes=request.interview_duration_minutes,
            question_length=request.question_length,
            client_questions=request.client_questions,  # type: ignore
            client_questions_count=request.client_questions_count,  # type: ignore
        )

        generator = InterviewQuestionGenerator(openai_api_key=api_key)

        job_requirements = load_json_from_file(UPLOAD_JSON_JD_DIR, jd_id)
        candidate_cv = load_json_from_file(UPLOAD_JSON_DIR, resume_id)
        interview_requirement = load_json_from_file(
            UPLOAD_JSON_INTERVIEW_REQ_DIR, interview_req_id
        )
        questions, metrics = generator.generate(
            job_requirements=job_requirements,
            candidate_cv=candidate_cv,
            interview_requirement=interview_requirement,
            config=config,
        )
        UUID = str(uuid4())
        metrics = InterviewMetrics(
            api_calls=metrics.api_calls,
            input_tokens=metrics.input_tokens,
            output_tokens=metrics.output_tokens,
            cost_estimate=metrics.cost_estimate,
            questions_generated=metrics.questions_generated,
            interview_duration_minutes=metrics.interview_duration_minutes,
            estimated_actual_duration_minutes=metrics.estimated_actual_duration_minutes,
            buffer_time_minutes=metrics.buffer_time_minutes,
        )

        response = InterviewQuestionResponse(
            id=UUID,
            jd_id=jd_id,
            resume_id=resume_id,
            intervew_req_id=interview_req_id,
            status="success",
            data=questions,
            metrics=metrics,
        )
        file_name = f"{UUID}.json"  # generate unique name
        file_path = os.path.join(UPLOAD_JSON_QUESTION_DIR, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response.dict(), f, indent=4)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Question Generation: {str(e)}"
        )


def qa_evaluation_and_generation(request: QAEvaluationRequest) -> Generator:
    try:
        generated_id = request.generated_question_id.strip()
        question_id = request.question_id.strip()

        if generated_id == "":
            raise ValueError("Please provide a valid Schema Generated Question ID.")
        if question_id == "":
            raise ValueError("Please provide a valid Question ID.")

        # ✅ Check generated question file exists
        get_generated_question_id = get_uploaded_file_names(
            UPLOAD_JSON_QUESTION_DIR, ".json"
        )
        if generated_id not in get_generated_question_id:
            raise ValueError("Please provide a valid Schema Generated Question ID.")

        api_key = os.getenv("API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # load from question folder
        questions = load_json_from_file(UPLOAD_JSON_QUESTION_DIR, generated_id)

        questions_data = questions.get("data", {}).get("questions", [])

        # convert question_id to int
        question_id_int = int(question_id)

        question = next(
            (q for q in questions_data if q["question_id"] == question_id_int), None
        )
        if not question:
            raise ValueError("No questions found in the generated question data.")

        # correct key name
        if request.is_followup:
            followup_index = request.followup_index
            if followup_index is None:
                raise ValueError(
                    "Follow-up index must be provided for follow-up questions."
                )

            question_to_evaluate = question.get("follow_up_questions", [])[
                followup_index
            ]
        else:
            question_to_evaluate = question.get("question", "")

        # Evaluate score
        score = evaluation(
            previous_question=request.previous_question,
            question=question_to_evaluate,
            answer=request.user_answer,
            question_category=question.get("category", ""),
            is_followup=request.is_followup,
            why_asked=question.get("why_asked", ""),
            relevance_to_cv=question.get("relevance_to_cv", ""),
        )

        if score >= 7.0:
            print(question_to_evaluate)
            # return whole question
            return question_to_evaluate
        else:
            # stream regeneration
            return re_generate_question(
                previous_question=request.previous_question,
                answer=request.user_answer,
                question_category=question.get("category", ""),
                why_asked=question.get("why_asked", ""),
                relevance_to_cv=question.get("relevance_to_cv", ""),
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Question Evaluation: {str(e)}"
        )
