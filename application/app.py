from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import os
import shutil
import time
import json
from fastapi import Form
from ai_agents import prompts_n_keys
from ai_agents import structured_prompt_n_keys, enhanced_resume_prompts
from ai_agents.openai_functions import enhance_resume_wrt_job, parse_resume_as_structured, enhance_resume_wrt_ai
from ai_agents.openai_functions import ask_with_instruction_json
from ai_agents.job_status import classify_email_status, check_validity_email
from main_functions import get_resume_text
from ai_agents.prompts_n_keys import get_matching_score_json
from extraction.apify_scraping import extract_profile_data

from pydantic import BaseModel
from typing import List, Dict, Any

class MatchRequest(BaseModel):
    resume_json: Dict[str, Any]
    jobs_json: List[Dict[str, Any]]


class MatchRequestDb(BaseModel):
    user_id: str
    resume_json: Dict[str, Any]



class EnhanceRequest(BaseModel):
    resume_json: Dict[str, Any]
    job_json: Dict[str, Any]


class EnhancedRequest(BaseModel):
    resume_json: Dict[str, Any]




app = FastAPI()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "wehire-ml-hub"}


@app.get("/health")
async def detailed_health_check():
    return {
        "status": "healthy",
        "service": "wehire-ml-hub",
        "version": "1.0.0",
        "timestamp": "2025-08-30"
    }



# @app.post("/upload-resume/")
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
   




# @app.post(
#     "/parse-resume/",
#     summary="Parse raw resume text into structured JSON",
# )
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

    start_total = time.perf_counter()

    # ---- Part 1: Validation, Save, Extract ----
    start_part1 = time.perf_counter()


    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file temporarily
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted_text = get_resume_text(temp_path)

    end_part1 = time.perf_counter()

    # ---- Part 2: Parsing ----
    start_part2 = time.perf_counter()

    cv_keys = parse_resume_as_structured(cv_text=extracted_text, system_instructions=structured_prompt_n_keys.system_information, resume_schema=structured_prompt_n_keys.resume_schema)

    end_part2 = time.perf_counter()
    end_total = time.perf_counter()

    # ---- Print timings ----
    # print(f"⏱ File validation + extraction took: {end_part1 - start_part1:.4f} sec")
    # print(f"⏱ Parsing took: {end_part2 - start_part2:.4f} sec")
    # print(f"⏱ Total time: {end_total - start_total:.4f} sec")

    print("processed: returning response")
    
    return JSONResponse(json.loads(cv_keys))





@app.post(
    "/parse-linkedin-structured/",
    summary="Parse LinkedIn profile into structured openai response",
)
async def parse_linkedin_structure(profile_url: str): 

    response = {"error_status": False, "error_message": "", "data": {}}

    try:
        extracted_text = extract_profile_data(profile_url)
        print("extracted_text:", extracted_text)
    except Exception as e:
        response["error_status"] = True
        response["error_message"] = f"Error extracting the LinkedIn profile data: {str(e)}"
        return response

    cv_keys = parse_resume_as_structured(cv_text=extracted_text, system_instructions=structured_prompt_n_keys.system_information, resume_schema=structured_prompt_n_keys.resume_schema)
    response["data"] = json.loads(cv_keys)
    print("final response")
    return response





@app.post(
    "/enhance_resume_with_jobs/",
    summary="Enhance resume according to job descriptions for AI search and AI apply",
)
async def enhance_resume_with_jobs(
    resume_json: str = Form(...),
    job_json: str = Form(...)
):
    import json

    # Step 1: Parse input resume JSON
    resume_dict = json.loads(resume_json)

    # Step 2: Extract subset to send to AI
    resume_subset = {
        "aboutMe": resume_dict.get("aboutMe", {}),
        "professionalSkills": resume_dict.get("professionalSkills", {}),
        "workExperience": resume_dict.get("workExperience", []),
        "workProjects": resume_dict.get("workProjects", [])
    }

    resume_str = json.dumps(resume_subset, indent=2)

    # Step 3: Call AI enhancement with job description
    cv_keys = enhance_resume_wrt_job(
        resume_json=resume_str,
        job_json=job_json,
        system_instructions=structured_prompt_n_keys.enhance_cv_prompt,
        resume_schema=structured_prompt_n_keys.resume_schema
    )

    # Step 4: Parse AI response into dict
    updated_subset = json.loads(cv_keys)

    # Step 5: Merge updated subset back into full resume
    for key in ["aboutMe", "professionalSkills", "workExperience", "workProjects"]:
        if key in updated_subset:
            resume_dict[key] = updated_subset[key]

    # Step 6: Return full enhanced resume
    return JSONResponse(resume_dict)





@app.post(
    "/enhance_resume_with_jobs_body/",
    summary="Enhance resume according to job descriptions for AI search and AI apply",
)
async def enhance_resume_with_jobs_body(payload: EnhanceRequest):
    import json

    # Step 1: Extract original resume
    resume_dict = payload.resume_json
    job_dict = payload.job_json

    # Step 2: Extract subset for AI enhancement
    resume_subset = {
        "aboutMe": resume_dict.get("aboutMe", {}),
        "professionalSkills": resume_dict.get("professionalSkills", {}),
        "workExperience": resume_dict.get("workExperience", []),
        "workProjects": resume_dict.get("workProjects", [])
    }

    resume_str = json.dumps(resume_subset, indent=2)
    job_str = json.dumps(job_dict, indent=2)

    # Step 3: Call AI enhancement
    cv_keys = enhance_resume_wrt_job(
        resume_json=resume_str,
        job_json=job_str,
        system_instructions=structured_prompt_n_keys.enhance_cv_prompt,
        resume_schema=structured_prompt_n_keys.resume_schema
    )

    # Step 4: Parse AI response
    updated_subset = json.loads(cv_keys)

    # Step 5: Merge subset back into full resume
    for key in ["aboutMe", "professionalSkills", "workExperience", "workProjects"]:
        if key in updated_subset:
            resume_dict[key] = updated_subset[key]

    # Step 6: Return the full updated resume
    return JSONResponse(resume_dict)



@app.post(
    "/enhance_resume_ai/",
    summary="Generate an AI-enhanced, ATS-optimized resume with professional improvements and missing data insights"
)
async def enhance_resume_with_jobs_body(payload: EnhancedRequest):
    import json
    resume_str = json.dumps(payload.resume_json, indent=2)


    cv_keys = enhance_resume_wrt_ai(
        resume_json=resume_str,
        system_instructions=enhanced_resume_prompts.enhance_cv_via_ai.format(resume_json=resume_str),
        resume_schema=enhanced_resume_prompts.resume_enhanced_schema
    )
    return JSONResponse(json.loads(cv_keys))






# from linkedin_scraping import main

# @app.post("/get-linkedin-profile/")
# async def linkedin_profile_text(profile_url: str):
#     response = main(profile_url)

#     return response





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



# @app.post("/match-jobs-db/")
async def call_openai_job_matcher(payload: MatchRequestDb):
    resume_json = payload.resume_json
    user_id = payload.user_id


    sample_jobs = "JSONS/db_jobs.json"

    with open(sample_jobs, "r") as f:
        jobs_db_data = json.load(f)

        jobs_json = jobs_db_data.get("data", {}).get("jobPosts", [])

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
    You are an expert HR copywriter and career coach. Given the following **resume data** and **job description**, write a job-application email that follows current best practices and professional standards.

    ---

    ### Input

    **Resume Data:**  
    {resume_data}

    **Job Description:**  
    {job_data}

    ---

    ### Requirements / Best Practices

    - Output must be valid JSON with exactly these keys:
    {{
        "job_id": "<employerId from job_data>",
        "subject": "<email_subject>",
        "email_content": "<email_body>"
    }}

    - **Subject line**:
    * Must match *one of these formats*:
        1. Application for [Job Title] – [Your Full Name]  
        2. [Job Title] Position – [Your Name]  
        3. [Your Name] – [Job Title] Application – [X+ Years Experience]  
        4. Experienced [Role] Applying for [Role] Role – [Your Name]  
        5. Application: [Role] – [Key qualifier] – [Your Name]  
    * Include the candidate’s name and job title (and job reference/ID if provided).  
    * Be clear, professional. Avoid vague or generic phrases.  
    * Keep concise (approx 6-10 words) so it isn’t truncated, especially on mobile.

    - **Salutation / Greeting**:
    * If hiring manager or contact person is known, address by name (“Dear Ms. Smith,” etc.).  
    * If not, “Dear Hiring Manager,” or similar formal greeting.

    - **Opening paragraph**:
    * State clearly which position you are applying for, and optionally where you found the listing.  
    * Introduce yourself briefly.

    - **Body**:
    * Highlight top 1-3 relevant skills, experiences, or achievements from the resume that map to requirements in the job description.  
    * Use specific examples (metrics, results if possible).  
    * Show alignment with the company or job (why this role, what you bring).

    - **Attachments and Documents**:
    * Mention that you’ve attached your resume (and cover letter if applicable).  
    * Use professional file names and suitable format (PDF if possible).

    - **Tone, Language, Style**:
    * Polite, formal, respectful; avoid slang, emojis, abbreviations.  
    * Use active voice.  
    * Proofread: grammar, spelling, consistency.

    - **Length / Structure**:
    * Body should be 3-4 short paragraphs. Total ~150-200 words.  
    * Use paragraph breaks for readability.

    - **Closing / Signature**:
    * Close with a courteous line (e.g. “Thank you for considering my application. I look forward to the possibility of discussing this opportunity.”)  
    * Include full name, email, phone number in signature.

    ---

    ### Example Output

    {{
    "job_id": "98765",
    "subject": "Application for Marketing Manager – Jane Doe",
    "email_content": "Dear Hiring Manager,\\n\\nI am writing to apply for the Marketing Manager position at Acme Corp that I found on LinkedIn. With over six years of experience in digital marketing and campaign strategy, I have successfully increased customer acquisition by 40% at my current role through targeted social media and email campaigns.\\n\\nI believe these experiences align well with Acme’s goal to expand its online presence. I have attached my resume in PDF format for your review. Thank you for considering my application. I would welcome the opportunity to discuss further how I can contribute to your team.\\n\\nSincerely,\\nJane Doe\\n[jane.doe@example.com]\\n[+1-234-567-890]"
    }}

    ---
    """
    # Later format this with resume_data, job_data

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
    email_content: str = Form(...)
    ):
    response =  classify_email_status(email_content)

    return JSONResponse(json.loads(response))



@app.post("/check-validity-email")
def check_email_validatity(
    company_email_content: str = Form(...),
    user_response_content: str = Form(...)
):

    response = check_validity_email(company_email_content, user_response_content)
    
    return JSONResponse(json.loads(response))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)