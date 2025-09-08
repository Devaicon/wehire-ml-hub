from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import shutil
import json
from fastapi import Form
from ai_agents import prompts_n_keys
from ai_agents import structured_prompt_n_keys
from ai_agents.openai_functions import enhance_resume_wrt_job, parse_resume_as_structured
from ai_agents.openai_functions import ask_with_instruction_json
from ai_agents.job_status import classify_email_status
from main_functions import get_resume_text
from ai_agents.prompts_n_keys import get_matching_score_json
from linkedin_scraping import get_linkedin_profile_text
from extraction.lib_scraping import extract_profile_data


app = FastAPI()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    print("temp_path:", temp_path)

    # Save uploaded file temporarily
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        extracted_text = get_resume_text(temp_path)
        return PlainTextResponse(content=extracted_text, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the PDF: {str(e)}")
    finally:
        os.remove(temp_path)
   




@app.post(
    "/parse-resume/",
    summary="Parse raw resume text into structured JSON",
)
async def parse_resume(cv_text: str = Form(...)):      # ⬅️  accept form field
    """
    Send the text received in the `cv_text` form field to OpenAI
    and return structured JSON.
    """

    cv_keys = ask_with_instruction_json(instruction=prompts_n_keys.structured_info.format(output_keys=prompts_n_keys.output_keys, available_filters=prompts_n_keys.available_filters,  cv_text=cv_text), message="extract data as json")
    return JSONResponse(json.loads(cv_keys))



@app.post(
    "/parse-resume-structured/",
    summary="Parse raw resume text into structured openai response",
)
async def parse_resume_structure(file: UploadFile = File(...)):      # ⬅️  accept form field

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file temporarily
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted_text = get_resume_text(temp_path)

    cv_keys = parse_resume_as_structured(cv_text=extracted_text, system_instructions=structured_prompt_n_keys.system_information, resume_schema=structured_prompt_n_keys.resume_schema)
    return JSONResponse(json.loads(cv_keys))





@app.post(
    "/parse-linkedin-structured/",
    summary="Parse LinkedIn profile into structured openai response",
)
async def parse_linkedin_structure(profile_url: str): 

    extracted_text = extract_profile_data(profile_url)

    cv_keys = parse_resume_as_structured(cv_text=extracted_text, system_instructions=structured_prompt_n_keys.system_information, resume_schema=structured_prompt_n_keys.resume_schema)
    return JSONResponse(json.loads(cv_keys))





@app.post(
    "/enhance_resume_with_jobs/",
    summary="Enhance resume according to job descriptions for ai search and ai apply",
)
async def enhance_resume_with_jobs(
    resume_json: str = Form(...),
    job_json: str = Form(...)
):
    cv_keys = enhance_resume_wrt_job(
        resume_json=resume_json,
        job_json=job_json,
        system_instructions=structured_prompt_n_keys.enhance_cv_prompt,
        resume_schema=structured_prompt_n_keys.resume_schema
    )
    return JSONResponse(json.loads(cv_keys))





# from linkedin_scraping import main

# @app.post("/get-linkedin-profile/")
# async def linkedin_profile_text(profile_url: str):
#     response = main(profile_url)

#     return response



from pydantic import BaseModel
from typing import List, Dict, Any

class MatchRequest(BaseModel):
    resume_json: Dict[str, Any]
    jobs_json: List[Dict[str, Any]]

@app.post("/match-jobs-form/")
async def call_openai_job_matcher(payload: MatchRequest):
    resume_json = payload.resume_json
    jobs_json = payload.jobs_json

    instructions = f"""
    Given the following resume data and list of job descriptions, return a list of matched jobs with detailed matching scores in form of JSON.

    Resume:
    {resume_json}

    Job Descriptions:
    {jobs_json}

    Output keys:
    {get_matching_score_json(skills_weightage=30, work_experience_weightage=25, projects_weightage=25, qualification_weightage=20)}
    """

    response = ask_with_instruction_json(instructions, "match jobs with resume data and return jobs")
    return JSONResponse(json.loads(response))





@app.post(
    "/generate-job-email/",
    summary="Generate email subject & content from CV + Job detail",
)
async def generate_job_email(job_json: str, resume_json: str):
    instructions = """
    You are an AI assistant helping a job applicant.
    Given the following **resume data** and a **job description**, 
    write a professional email subject and email content that the candidate 
    could use to apply for the job.

    Requirements:
    - Subject line should be concise and professional.
    - Email content should be polite, formal, and tailored to the job description.
    - Mention relevant skills/experience from the resume.

    Resume:
    {resume_data}

    Job Description:
    {job_data}

    Output JSON keys:
    {{
        "job_id": "<employerId from job_data>",
        "subject": "<email_subject>",
        "email_content": "<email_body>"
    }}
    """

    # job_json will be a dict in string form, so we parse it to extract job_id
    job_data = json.loads(job_json)
    resume_data = json.loads(resume_json)

    formatted_instructions = instructions.format(
        resume_data=json.dumps(resume_data, indent=2),
        job_data=json.dumps(job_data, indent=2),
    )

    message = "Write subject and email content for job application"
    
    # Call your OpenAI wrapper
    response = ask_with_instruction_json(formatted_instructions, message)
    
    # Attach job_id to final JSON
    response_json = json.loads(response)

    return JSONResponse(response_json)





@app.post("/classify-job-status")
def classify_email(
    email_content: str = Form(...),
):
    return classify_email_status(email_content)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)