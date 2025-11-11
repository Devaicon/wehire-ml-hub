import json
import os
from typing import Any
from uuid import uuid4
from fastapi import HTTPException
from ai_agents.pdf_extractor.resume_extractor import OptimizedResumeExtractor
from ai_agents.prompts.resume.resume_enhance import (
    AI_SYSTEM_PROMPT,
    SYSTEM_PROMPT as JOB_SYSTEM_PROMPT,
)
from schema.resume_enhancement import (
    EnhanceResumeWthAiResponse,
    EnhancedResumeResponse,
    get_resume_enhancement_schema,
)
from schema.resume_parser import get_resume_extraction_schema
from schema.interview import ExtractionResumeMetrics, ExtractionResumeResponse
from ai_agents.llm.openai import OpenAI_LLM
from security.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore

BASE_UPLOAD_PATH = os.path.join("public", "static", "uploads")

UPLOAD_JSON_DIR = os.path.join(BASE_UPLOAD_PATH, "resume_json")

os.makedirs(UPLOAD_JSON_DIR, exist_ok=True)


# # @app.post("/upload-resume/")
# async def parse_resume(cv_text: str = Form(...)):      # ⬅️  accept form field
#     """
#     Send the text received in the `cv_text` form field to OpenAI
#     and return structured JSON.
#     """

#     cv_keys = ask_with_instruction_json(instruction=prompts_n_keys.structured_info.format(output_keys=prompts_n_keys.output_keys, available_filters=prompts_n_keys.available_filters,  cv_text=cv_text), message="extract data as json")
#     return JSONResponse(json.loads(cv_keys))

# @app.post(
#     "/parse-resume/",
#     summary="Parse raw resume text into structured JSON",
# )
# async def upload_resume(file: UploadFile = File(...)):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported.")

#     temp_path = os.path.join(UPLOAD_DIR, file.filename)
#     print("temp_path:", temp_path)

#     # Save uploaded file temporarily
#     with open(temp_path, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     try:
#         extracted_text = get_resume_text(temp_path)
#         return PlainTextResponse(content=extracted_text, media_type="text/plain")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing the PDF: {str(e)}")
#     finally:
#         os.remove(temp_path)


def extract_resume(
    pdf_path: str,
    pages_per_chunk: int = 5,
    max_workers: int = 5,
    ocr_method: str = "tesseract",
    verbose: bool = True,
) -> ExtractionResumeResponse:
    """
    Convenience function for quick extraction

    Args:
        pdf_path: Path to PDF resume
        api_key: OpenAI API key
        pages_per_chunk: Pages per chunk (3-7 recommended)
        max_workers: Parallel workers (5-10 recommended)
        ocr_method: "none", "tesseract", or "vision"
        verbose: Print progress

    Returns:
        (extracted_data, metrics)

    Example:
        data, metrics = extract_resume("resume.pdf", "sk-...")
        print(f"Name: {data['personalInfo']['firstName']}")
        print(f"Skills: {data['professionalSkills']['skills']}")
    """
    try:
        extractor = OptimizedResumeExtractor(
            pages_per_chunk=pages_per_chunk, max_workers=max_workers
        )
        extracted_data, metrics = extractor.extract_from_pdf(
            pdf_path, ocr_method, verbose
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


def enhance_resume_wrt_job(resume_json: str, job_json: str) -> EnhancedResumeResponse:
    # Step 1: Parse input resume JSON
    resume_dict = json.loads(resume_json)

    # Step 2: Extract subset to send to AI
    resume_subset = {
        "aboutMe": resume_dict.get("aboutMe", {}),
        "professionalSkills": resume_dict.get("professionalSkills", {}),
        "workExperience": resume_dict.get("workExperience", []),
        "workProjects": resume_dict.get("workProjects", []),
    }

    resume_jsonify = json.dumps(resume_subset, indent=2)


    messages = [
        {"role": "system", "content": JOB_SYSTEM_PROMPT},
        {"role": "user", "content": f"{resume_jsonify}" + "\n\n" + job_json},
    ]
    response = llm.generate_json(
        schema=get_resume_extraction_schema(), model="gpt-4o-mini", messages=messages
    )

    # Safely extract content
    content = "{}"
    if response and getattr(response, "choices", None):
        try:
            content = response.choices[0].message.content or "{}"
        except Exception:
            content = "{}"

    # Step 4: Parse AI response into dict
    updated_subset = json.loads(content)

    # Step 5: Merge updated subset back into full resume
    for key in ["aboutMe", "professionalSkills", "workExperience", "workProjects"]:
        if key in updated_subset:
            resume_dict[key] = updated_subset[key]

    return EnhancedResumeResponse(data=resume_dict)


def enhance_resume_wrt_ai(resume_json: dict[str, Any]) -> EnhanceResumeWthAiResponse:
    resume_str = json.dumps(resume_json, indent=2)
    messages = [
        {"role": "system", "content": AI_SYSTEM_PROMPT.format(resume_json=resume_str)},
        {"role": "user", "content": resume_str},
    ]

    response = llm.generate_json(
        schema=get_resume_enhancement_schema(), model="gpt-4o-mini", messages=messages
    )
    # Safely extract content
    content = "{}"
    if response and getattr(response, "choices", None):
        try:
            content = response.choices[0].message.content or "{}"
        except Exception:
            content = "{}"

    return EnhanceResumeWthAiResponse(data=json.loads(content))
