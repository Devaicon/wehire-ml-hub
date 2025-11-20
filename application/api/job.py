from fastapi import APIRouter
from api.services.job import generate_job_mail, resume_with_job_matcher
from db_apis.fetch_jobs import process_jobs_in_batches
from fastapi import Request, HTTPException
from schema.job import (
    GenerateJobMailRequest,
    JobMailResponse,
    JobMatchDbErrorResponse,
    JobMatchDbResponse,
    JobMatchRequest,
    JobMatchDbRequest,
    JobMatchResponse,
)
from security.config import MAX_JOBS


router = APIRouter(prefix="/job", tags=["Job"])


@router.post("/match-jobs-form/")
async def call_openai_job_matcher(payload: JobMatchRequest) -> JobMatchResponse:
    response = resume_with_job_matcher(payload=payload)
    return response


@router.post(
    "/generate-job-email/",
    summary="Generate email subject & content from CV + Job detail",
    response_model=JobMailResponse,
)
async def generate_job_email(request: Request):
    try:
        body = await request.json()
        object = GenerateJobMailRequest(**body)
        response = generate_job_mail(job_json=object.job_json, resume_json=object.resume_json)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating job email: {str(e)}")


@router.post("/match-jobs-db/")
async def call_limited_job_matcher(payload: JobMatchDbRequest):
    try:
        user_id = payload.user_id
        resume_json = payload.resume_json

        process_jobs_in_batches(
            user_id=user_id,
            resume_json=resume_json,
            batch_size=MAX_JOBS
        )

        return JobMatchDbResponse(status="success")

    except Exception as e:
        error_message = f"Error during match score process: {str(e)}"
        return JobMatchDbErrorResponse(
            err_status=False, err_message=error_message, data={"status": "failed"}
        )
