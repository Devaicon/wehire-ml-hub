from ai_agents.llm.openai import OpenAI_LLM
from security.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore


def evaluation(
    previous_question: str,
    question: str,
    answer: str,
    question_category: str,
    is_followup: bool,
    why_asked: str,
    relevance_to_cv: str,
):
    if is_followup:
        evaluation_prompt = f"""
        You are an expert interview evaluator. Analyze whether it is relevant to ask a follow-up question based on the candidate's answer.

        Instructions:
        - Read the interview question and candidate's answer.
        - Decide if a follow-up question is necessary to clarify, probe deeper, or evaluate competency.
        - Output only a single number between 0 and 10.
        - 0 = Follow-up not relevant at all
        - 10 = Follow-up extremely relevant and necessary

        EVALUATION INTERVIEW QUESTION WHICH GOING TO ASK AS NEXT:
        {question}

        PREVIOUS INTERVIEW QUESTION:
        {previous_question}

        PREVIOUS QUESTION ANSWER CANDIDATE ANSWER:
        {answer}

        EVALUATION QUESTION CATEGORY:
        {question_category}

        WHY THIS QUESTION WAS ASKED:
        {why_asked}

        RELEVANCE TO CANDIDATE'S CV:
        {relevance_to_cv}

        IMPORTANT:
        - Output ONLY a single numerical value (0–10). No explanation.
        """
    else:
        evaluation_prompt = f"""
        You are an expert interview evaluator. Analyze the relevance of the interview question based on the candidate's answer.

        Instructions:
        - Read the interview question and candidate's answer.
        - Decide how relevant the question is to the candidate's profile and the job description.
        - Output only a single number between 0 and 10.
        - 0 = Not relevant at all
        - 10 = Extremely relevant

        EVALUATION INTERVIEW QUESTION:
        {question}

        PREVIOUS INTERVIEW QUESTION:
        {previous_question}

        PREVIOUS QUESTION ANSWER CANDIDATE ANSWER:
        {answer}

        EVALUATION QUESTION CATEGORY:
        {question_category}

        WHY THIS QUESTION WAS ASKED:
        {why_asked}

        RELEVANCE TO CANDIDATE'S CV:
        {relevance_to_cv}

        IMPORTANT:
        - Output ONLY a single numerical value (0–10). No explanation.
        """

    response_text = llm.chat(
        messages=[
            {"role": "system", "content": "You are an expert interview evaluator."},
            {"role": "user", "content": evaluation_prompt},
        ],
        model="gpt-4o-mini",
    )
    # Clean output to extract only number
    response_text = response_text.strip()  # type: ignore
    try:
        relevance_score = float(response_text)
    except Exception as e:
        print(f"Error parsing relevance score: {e}")
        relevance_score = 0  # In case model returns unexpected output

    return relevance_score


def re_generate_question(
    previous_question: str,
    answer: str,
    question_category: str,
    why_asked: str,
    relevance_to_cv: str,
):
    generate_next_question_prompt = f"""
    You are an expert AI Interview Question Generator assisting a professional interviewer.

    Your task: Generate the most relevant and meaningful next interview question based on the provided context.

    CONTEXT DETAILS:
    ────────────────────────────
    PREVIOUS INTERVIEW QUESTION:
    {previous_question}

    CANDIDATE'S ANSWER:
    {answer}

    CURRENT QUESTION CATEGORY:
    {question_category}

    WHY THE PREVIOUS QUESTION WAS ASKED:
    {why_asked}

    RELEVANCE TO CANDIDATE'S CV:
    {relevance_to_cv}

    ────────────────────────────
    INSTRUCTIONS:
    1. Read the previous question and the candidate’s answer carefully.
    2. Identify any gaps, unclear points, or areas worth deeper exploration.
    3. Consider the question category and CV relevance while generating the next question.
    4. The new question must:
    - Be contextually related to the candidate’s previous response.
    - Reflect curiosity, depth, and logical follow-up.
    - Stay within the same or closely related topic domain.
    5. Output only ONE interview question in natural language.
    6. Do NOT include explanations, comments, or formatting — output just the question text.

    Now, generate the next question that should be asked.
    """

    return llm.chat_stream(
        messages=[
            {"role": "system", "content": "You are an expert interview evaluator."},
            {"role": "user", "content": generate_next_question_prompt},
        ],
        model="gpt-4o-mini",
    )
