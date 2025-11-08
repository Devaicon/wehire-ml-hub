import os
import shutil
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from api.services.interview import (
    interview_question_generation,
    interview_requirement_extractor,
    jd_extractor,
    pdf_extractor_optimized,
    qa_evaluation_and_generation,
)
from enums.interview import OCRMethod
from schema.interview import (
    ExtractionResumeResponse,
    InterviewQuestionRequest,
    InterviewQuestionResponse,
    InterviewRequirementExtractionResponse,
    JobDescription,
    QAEvaluationRequest,
)


router = APIRouter(prefix="/interview", tags=["Interview"])

UPLOAD_DIR = "public/static/uploads/pdf"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/health-check")
async def health_check():
    # Logic to start an interview for the candidate
    return {"message": "ok"}


@router.post("/parse-resume-optimized/", response_model=ExtractionResumeResponse)
async def parse_resume_optimized(
    file: UploadFile = File(...),
    ocr_method: OCRMethod = Form(default=OCRMethod.tesseract),
):
    try:
        if not file.filename.endswith(".pdf"):  # type: ignore
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        temp_path = os.path.join(UPLOAD_DIR, file.filename)  # type: ignore
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

            response = pdf_extractor_optimized(
                temp_path=temp_path, ocr_method=ocr_method
            )

            return response
    finally:
        if os.path.exists(temp_path):  # type: ignore
            os.remove(temp_path)  # type: ignore


@router.post("/parse-job-description/", response_model=JobDescription)
async def parse_job_description(
    text: str,
):
    try:
        if text.strip() == "":
            raise HTTPException(
                status_code=400, detail="Please insert the Job Description text."
            )
        response = jd_extractor(
            text=text,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Job Description: {str(e)}"
        )


@router.post(
    "/parse-interview-requirement/",
    response_model=InterviewRequirementExtractionResponse,
)
async def parse_interview_requirement(
    text: str,
):
    try:
        if text.strip() == "":
            raise HTTPException(
                status_code=400, detail="Please insert the Job Description text."
            )
        response = interview_requirement_extractor(
            text=text,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Job Description: {str(e)}"
        )


@router.post(
    "/interview-question-generation/", response_model=InterviewQuestionResponse
)
async def interview_question_generate(
    request: InterviewQuestionRequest,
):
    try:
        print("Generating interview questions...")
        print(f"Request: {request}")
        response = interview_question_generation(request=request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Question Generation: {str(e)}"
        )


@router.post(
    "/question-evaluation-generation/", response_model=InterviewQuestionResponse
)
async def qa_evaluation_and_gen(
    request: QAEvaluationRequest,
):
    try:
        print("Generating interview questions...")
        print(f"Request: {request}")

        def generate():
            for chunk in qa_evaluation_and_generation(request=request):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing Question Evaluation: {str(e)}"
        )
