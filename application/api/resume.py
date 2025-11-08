import os
import shutil
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from api.services.resume import enhance_resume_wrt_ai, extract_resume
from api.services.resume import enhance_resume_wrt_job
from schema.resume_enhancement import (
    EnhanceResumeRequest,
    EnhanceResumeWthAiRequest,
    EnhanceResumeWthAiResponse,
    EnhancedResumeResponse,
)
from schema.interview import ExtractionResumeResponse
import json

UPLOAD_DIR = "public/static/uploads/pdf"

os.makedirs(UPLOAD_DIR, exist_ok=True)


router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post(
    "/parse-resume-structured/",
    summary="Parse raw resume text into structured openai response",
    response_model=ExtractionResumeResponse,
)
async def parse_resume_structure(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):  # type: ignore
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        temp_path = os.path.join(UPLOAD_DIR, file.filename)  # type: ignore
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

            response = extract_resume(pdf_path=temp_path, verbose=True)

            return response
    finally:
        if os.path.exists(temp_path):  # type: ignore
            os.remove(temp_path)  # type: ignore


@router.post(
    "/enhance_resume_with_jobs/",
    summary="Enhance resume according to job descriptions for AI search and AI apply",
)
async def enhance_resume_with_jobs(
    resume_json: str = Form(...), job_json: str = Form(...)
) -> EnhancedResumeResponse:
    response = enhance_resume_wrt_job(
        resume_json=resume_json,
        job_json=job_json,
    )

    return response


@router.post(
    "/enhance_resume_with_jobs_body/",
    summary="Enhance resume according to job descriptions for AI search and AI apply",
)
async def enhance_resume_with_jobs_body(
    payload: EnhanceResumeRequest,
) -> EnhancedResumeResponse:
    resume_dict = payload.resume_json
    job_dict = payload.job_json

    resume_subset = {
        "aboutMe": resume_dict.get("aboutMe", {}),
        "professionalSkills": resume_dict.get("professionalSkills", {}),
        "workExperience": resume_dict.get("workExperience", []),
        "workProjects": resume_dict.get("workProjects", []),
    }

    resume_str = json.dumps(resume_subset, indent=2)
    job_str = json.dumps(job_dict, indent=2)

    response = enhance_resume_wrt_job(
        resume_json=resume_str,
        job_json=job_str,
    )

    return response


@router.post(
    "/enhance_resume_ai/",
    summary="Generate an AI-enhanced, ATS-optimized resume with professional improvements and missing data insights",
)
async def enhance_resume_wth_ai(
    payload: EnhanceResumeWthAiRequest,
) -> EnhanceResumeWthAiResponse:
    response = enhance_resume_wrt_ai(resume_json=payload.resume_json)

    return response
