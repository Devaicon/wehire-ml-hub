from fastapi import APIRouter, Form

from api.services.email import check_validity_email, classify_email_status
from schema.email import EmailClasifyResponse, EmailValidateResponse

router = APIRouter(prefix="/email", tags=["Email"])


@router.post("/classify-job-status", response_model=EmailClasifyResponse)
def classify_email(email_content: str = Form(...)):
    response = classify_email_status(email_content)
    return response


@router.post("/check-validity-email", response_model=EmailValidateResponse)
def check_email_validatity(
    company_email_content: str = Form(...), user_response_content: str = Form(...)
):
    response = check_validity_email(
        company_email_content=company_email_content,
        user_response_content=user_response_content,
    )
    return response
