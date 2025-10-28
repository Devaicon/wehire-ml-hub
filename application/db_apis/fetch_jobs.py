import requests
import json
import time
from ai_agents.prompts_n_keys import get_matching_score_json
from ai_agents.openai_functions import ask_with_instruction_json

from utils import config as Config



# -----------------------------
# Mock DB update function
# -----------------------------
def update_job_status_in_db(job_id, status):
    """
    Mock function to update job processing status in DB.
    Replace with your actual DB logic (e.g., SQLAlchemy, MongoDB, etc.).
    """
    print(f"🟢 Job {job_id} status updated to '{status}' in database.")


# -----------------------------
# API Fetch Function
# -----------------------------
def get_unprocessed_jobs(user_id, page=1, limit=5):
    """
    Fetch Vehire public jobs for a user and return only unprocessed job posts.
    """
    url = 'https://www.vehire.ai/api/job-applying/jobpost/getAllPublic'
    params = {
        'page': page,
        'limit': limit,
        'tags': '["Software"]',
        'userId': user_id
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        print("data: ", data)

        job_posts = data.get("data", {}).get("jobPosts", [])
        user_jobs = data.get("data", {}).get("userJobs", [])
        processed_ids = {job["jobId"] for job in user_jobs}
        unprocessed_jobs = [job for job in job_posts if job["_id"] not in processed_ids]

        print(f"🔎 Found {len(unprocessed_jobs)} unprocessed jobs on page {page}")
        return unprocessed_jobs, data.get("data", {}).get("totalPages", 1)

    except requests.exceptions.RequestException as e:
        print("❌ Error:", e)
        return [], 1


# -----------------------------
# Job Processing Function
# -----------------------------
def process_jobs_in_batches(user_id, resume_json, batch_size=5):
    """
    Fetch all unprocessed jobs (page by page) and process them in batches.
    """
    page = 1

    match_score_criteria = get_matching_score_json(
        skills_weightage=Config.skills_weightage,
        work_experience_weightage=Config.work_experience_weightage,
        projects_weightage=Config.projects_weightage,
        qualification_weightage=Config.qualification_weightage
    )

    while True:
        unprocessed_jobs, total_pages = get_unprocessed_jobs(user_id, page=page)
        if not unprocessed_jobs:
            break  # no more jobs

        print(f"\n📄 Page {page}/{total_pages} — Jobs fetched: {len(unprocessed_jobs)}")
        print("match_score_criteria: ", match_score_criteria)

        # Process jobs in batches
        for i in range(0, len(unprocessed_jobs), batch_size):
            jobs_json = unprocessed_jobs[i:i + batch_size]
            print(f"\n🚀 Processing batch {i//batch_size + 1} (jobs {i+1}-{i+len(jobs_json)})")

            instructions = f"""
            Given the following resume data and list of job descriptions, return a list of matched jobs with detailed matching scores in form of JSON.

            Resume:
            {resume_json}

            Job Descriptions:
            {jobs_json}

            Output keys:
            {match_score_criteria}
            """

            response = ask_with_instruction_json(instructions, "match jobs with resume data and return jobs")
            response = json.loads(response)

            for job in response["matched_jobs"]:
                job_id = job["job_id"]
                job_title = job.get("job_title", "N/A")
                match_score = job.get("match_score", 0)

                payload = {"user": user_id, "jobId": job_id, "jobScore": match_score}
                headers = {"Content-Type": "application/json"}

                r = requests.put("https://www.vehire.ai/api/job-applying/jobpost/updateScore",
                                 headers=headers, data=json.dumps(payload))
                print(f"→ Updated {job_title} ({job_id}) → {r.status_code}")

            print(f"✅ Completed batch {i//batch_size + 1}")

        if page >= total_pages:
            break
        page += 1

    print("🎯 All unprocessed jobs processed successfully!")



# -----------------------------
# Run Example
# -----------------------------
if __name__ == "__main__":
    user_id = "68fa9063bd12881cb5141d84"
    resume_json = {}
    process_jobs_in_batches(user_id, resume_json)
