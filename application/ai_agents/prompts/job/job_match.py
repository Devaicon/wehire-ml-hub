SYSTEM_PROMPT = """
    Given the following resume data and list of job descriptions, return a list of matched jobs with detailed matching scores in form of JSON.

    Resume:
    {resume_json}

    Job Descriptions:
    {jobs_json}

    You have to only generate the Json format.
    """
