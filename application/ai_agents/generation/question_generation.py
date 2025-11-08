import json
from typing import Dict, Any, List
from openai import OpenAI
from ai_agents.llm.openai import OpenAI_LLM
from schema.interview import InterviewConfig, InterviewMetrics
from enums.interview import DifficultyLevel, QuestionSource
from schema.question_generation import interview_question_schema
from security.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore


class InterviewQuestionGenerator:
    """
    Generate customized interview questions based on:
    - TIME DURATION (10, 30, 60 minutes)
    - JOB REQUIREMENTS (extracted from JD)
    - CANDIDATE CV (extracted resume)
    - INTERVIEW REQUIREMENTS (user-defined evaluation criteria)
    """

    INPUT_PRICE_PER_1K = 0.000150
    OUTPUT_PRICE_PER_1K = 0.000600

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.schema = self._get_schema()

        # Metrics
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def _get_schema(self) -> dict:
        """JSON schema for interview questions"""
        return interview_question_schema

    def generate(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        interview_requirement: Dict[str, Any],  # ✅ NOW USED
        config: InterviewConfig,
        verbose: bool = True,
    ) -> tuple[Dict[str, Any], InterviewMetrics]:
        """
        Generate interview questions based on all inputs

        Args:
            job_requirements: Extracted job requirements JSON (from JD parser)
            candidate_cv: Extracted resume data JSON (from resume parser)
            interview_requirement: Extracted interview requirements (from interview req parser)
            config: InterviewConfig with TIME-BASED parameters
            include_intro_questions: Add introductory questions at start (default: True)
            verbose: Print progress

        Returns:
            (generated_questions, metrics)
        """
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

        if verbose:
            print("🚀 Starting TIME-BASED interview question generation...")
            print(f"⏱️  Interview Duration: {config.interview_duration_minutes} minutes")
            print(f"📊 Calculated Questions: {config.total_questions}")
            print(f"📄 Model: {self.model}")
            print(f"🎯 Difficulty: {config.difficulty_level.value}")
            print(f"📊 Source: {config.question_source.value}")
            print(f"⏳ Answer Length: {config.question_length}")
            print(f"👋 Include Intro: {config.include_intro_questions}")

            # ✅ Show interview requirements info
            if interview_requirement:
                print(
                    f"📋 Interview Type: {interview_requirement.get('interview_type', 'N/A')}"
                )
                print(
                    f"🎯 Focus Areas: {len(interview_requirement.get('key_focus_areas', []))}"
                )
                print(
                    f"✓ Must Evaluate: {len(interview_requirement.get('must_evaluate', []))}"
                )
            print()

        # Build prompt based on source type
        if config.question_source == QuestionSource.CLIENT_PROVIDED:
            if verbose:
                print("✓ Using client-provided questions only")
            questions = self._format_client_questions(config.client_questions, config)

        elif config.question_source == QuestionSource.AI_GENERATED:
            if verbose:
                print("🤖 Generating all questions with AI...")
            questions = self._generate_ai_questions(
                job_requirements, candidate_cv, interview_requirement, config, verbose
            )

        else:  # HYBRID
            if verbose:
                print(
                    f"🔄 Using hybrid approach: {config.client_questions_count} client + "
                    f"{config.total_questions - config.client_questions_count} AI questions"
                )
            questions = self._generate_hybrid_questions(
                job_requirements, candidate_cv, interview_requirement, config, verbose
            )

        # Calculate metrics
        cost = self._calculate_cost()
        buffer_time = config.interview_duration_minutes * config.buffer_time_percent

        metrics = InterviewMetrics(
            api_calls=self.api_calls,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cost_estimate=cost,
            questions_generated=len(questions.get("questions", [])),
            interview_duration_minutes=config.interview_duration_minutes,
            estimated_actual_duration_minutes=questions["interview_summary"][
                "estimated_interview_duration_minutes"
            ],
            buffer_time_minutes=buffer_time,
        )

        if verbose:
            print("\n✅ Interview generation complete!\n")
            print(metrics)

        return questions, metrics

    def _format_client_questions(
        self, questions: List[str], config: InterviewConfig
    ) -> Dict[str, Any]:
        """Format client-provided questions with time estimates"""
        answer_times = {"short": 2, "medium": 4, "long": 7}
        time_per_q = answer_times[config.question_length] + 1  # +1 for asking

        formatted_questions = []
        for idx, question in enumerate(questions[: config.total_questions], 1):
            formatted_questions.append(
                {
                    "question_id": idx,
                    "question": question,
                    "category": "Client-Provided",
                    "difficulty": config.difficulty_level.value,
                    "expected_answer_type": config.question_length,
                    "estimated_time_minutes": time_per_q,
                    "key_points": [],
                    "follow_up_questions": [],
                    "why_asked": "Provided by client",
                    "relevance_to_cv": "To be determined during interview",
                }
            )

        total_time = len(formatted_questions) * time_per_q

        return {
            "questions": formatted_questions,
            "interview_summary": {
                "total_questions": len(formatted_questions),
                "difficulty_distribution": {
                    "easy": len(
                        [
                            q
                            for q in formatted_questions
                            if config.difficulty_level == DifficultyLevel.EASY
                        ]
                    ),
                    "medium": len(
                        [
                            q
                            for q in formatted_questions
                            if config.difficulty_level == DifficultyLevel.MEDIUM
                        ]
                    ),
                    "hard": len(
                        [
                            q
                            for q in formatted_questions
                            if config.difficulty_level == DifficultyLevel.HARD
                        ]
                    ),
                },
                "question_categories": ["Client-Provided"],
                "estimated_interview_duration_minutes": total_time,
            },
        }

    def _generate_ai_questions(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        interview_requirement: Dict[str, Any],  # ✅ NOW PASSED
        config: InterviewConfig,
        verbose: bool,
    ) -> Dict[str, Any]:
        """Generate all questions using AI"""
        prompt = self._build_generation_prompt(
            job_requirements, candidate_cv, interview_requirement, config, all_ai=True
        )
        return self._call_api(prompt)

    def _generate_hybrid_questions(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        interview_requirement: Dict[str, Any],  # ✅ NOW PASSED
        config: InterviewConfig,
        verbose: bool,
    ) -> Dict[str, Any]:
        """Generate hybrid questions (client + AI)"""
        client_qs_section = f"""
CLIENT PROVIDED QUESTIONS (Must include these):
{json.dumps(config.client_questions, indent=2)}

Include these {config.client_questions_count} questions as-is, then generate {config.total_questions - config.client_questions_count} additional AI questions.
"""

        prompt = self._build_generation_prompt(
            job_requirements,
            candidate_cv,
            interview_requirement,
            config,
            all_ai=False,
            client_questions_section=client_qs_section,
        )
        return self._call_api(prompt)

    def _build_generation_prompt(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        interview_requirement: Dict[str, Any],  # ✅ NOW USED IN PROMPT
        config: InterviewConfig,
        all_ai: bool = True,
        client_questions_section: str = "",
    ) -> str:
        """Build the prompt for question generation with interview requirements"""

        answer_length_guidance = {
            "short": "1-2 minute answers expected",
            "medium": "3-5 minute answers expected",
            "long": "5-10 minute answers expected",
        }

        time_per_question = {
            "short": 3,  # 2 min answer + 1 min asking/transition
            "medium": 5,  # 4 min answer + 1 min asking/transition
            "long": 8,  # 7 min answer + 1 min asking/transition
        }

        # ✅ Extract key evaluation criteria from interview_requirement
        evaluation_section = self._build_evaluation_section(interview_requirement)

        prompt = f"""You are an expert interview panel coordinator. Generate interview questions for a {config.interview_duration_minutes}-minute interview.

        TIME CONSTRAINTS:
        - Total Interview Duration: {config.interview_duration_minutes} minutes
        - Questions to Generate: {config.total_questions}
        - Time per Question: ~{time_per_question[config.question_length]} minutes (including answer + asking)
        - Buffer Time: {config.buffer_time_percent * 100}% for intro, transitions, wrap-up

        INTERVIEW CONTEXT:
        - Difficulty: {config.difficulty_level.value}
        - Answer Length: {answer_length_guidance[config.question_length]}
        - Question Source: {config.question_source.value}

        {evaluation_section}

        JOB REQUIREMENTS:
        {json.dumps(job_requirements, indent=2)}

        CANDIDATE PROFILE:
        {json.dumps(candidate_cv, indent=2)}

        {client_questions_section}

        CRITICAL REQUIREMENTS:
        1. Generate EXACTLY {config.total_questions} questions (optimized for {config.interview_duration_minutes} minutes)
        2. Each question should have estimated_time_minutes set to {time_per_question[config.question_length]}
        3. Tailor questions to match the candidate's experience and the job role
        5. Include follow-up questions for each main question
        6. Provide key points that indicate a good answer
        7. Explain why each question is relevant to this role
        8. Reference the candidate's CV when relevant
        9. Ensure difficulty level is consistent: {config.difficulty_level.value}
        10. Mix question types: technical, behavioral, situational, problem-solving
        11. Questions should expose gaps or strengths relative to job requirements
        12. Prioritize most important questions first (in case interview runs short)

        ⚠️ STRICTLY FOLLOW THE EVALUATION GUIDELINES ABOVE - Focus on what TO judge, avoid what NOT to judge.

        GENERATE {config.total_questions} TIME-OPTIMIZED INTERVIEW QUESTIONS."""

        return prompt

    def _build_evaluation_section(self, interview_requirement: Dict[str, Any]) -> str:
        """
        Build evaluation criteria section from interview requirements

        ✅ This uses the parsed interview_requirement JSON to guide question generation
        """
        if not interview_requirement:
            return ""

        # Extract what to judge
        judge_for = interview_requirement.get("judge_for", {})
        do_not_judge = interview_requirement.get("do_not_judge", {})

        judge_list = [k.replace("_", " ").title() for k, v in judge_for.items() if v]
        dont_judge_list = [
            k.replace("_", " ").title() for k, v in do_not_judge.items() if v
        ]

        # Extract key areas
        key_focus_areas = interview_requirement.get("key_focus_areas", [])
        must_evaluate = interview_requirement.get("must_evaluate", [])
        nice_to_evaluate = interview_requirement.get("nice_to_evaluate", [])
        technical_skills = interview_requirement.get("technical_skills_to_assess", [])
        soft_skills = interview_requirement.get("soft_skills_to_assess", [])
        red_flags = interview_requirement.get("red_flags", [])
        green_flags = interview_requirement.get("green_flags", [])

        # Extract evaluation criteria with weights
        evaluation_criteria = interview_requirement.get("evaluation_criteria", [])
        criteria_text = ""
        if evaluation_criteria:
            criteria_text = "\nEVALUATION CRITERIA (with weights):\n"
            for criterion in evaluation_criteria:
                criteria_text += f"- {criterion.get('criterion', '')}: {criterion.get('weight_percentage', '')}% - {criterion.get('description', '')}\n"

        section = f"""
        INTERVIEW EVALUATION GUIDELINES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ✅ WHAT TO JUDGE (Focus questions on these areas):
        {", ".join(judge_list) if judge_list else "Standard technical and behavioral assessment"}

        ❌ WHAT NOT TO JUDGE (Avoid questions related to):
        {", ".join(dont_judge_list) if dont_judge_list else "Personal background, appearance, nervousness"}

        🎯 KEY FOCUS AREAS:
        {chr(10).join(f"- {area}" for area in key_focus_areas) if key_focus_areas else "- General role fit"}

        ⭐ MUST EVALUATE (Critical areas):
        {chr(10).join(f"- {area}" for area in must_evaluate) if must_evaluate else "- Core competencies"}

        💡 NICE TO EVALUATE (If time permits):
        {chr(10).join(f"- {area}" for area in nice_to_evaluate) if nice_to_evaluate else "- Additional skills"}

        🔧 TECHNICAL SKILLS TO ASSESS:
        {", ".join(technical_skills) if technical_skills else "As per job requirements"}

        🤝 SOFT SKILLS TO ASSESS:
        {", ".join(soft_skills) if soft_skills else "Communication, problem-solving, teamwork"}

        🚩 RED FLAGS TO WATCH FOR:
        {chr(10).join(f"- {flag}" for flag in red_flags) if red_flags else "- Poor communication, lack of preparation"}

        ✨ GREEN FLAGS (Positive indicators):
        {chr(10).join(f"- {flag}" for flag in green_flags) if green_flags else "- Clear communication, asks clarifying questions"}

        {criteria_text}

        📋 INTERVIEW TYPE: {interview_requirement.get("interview_type", "Technical")}
        ⏱️ EXPECTED DURATION: {interview_requirement.get("duration_minutes", "N/A")} minutes
        🎓 POSITION: {interview_requirement.get("position", "N/A")}
        📊 DIFFICULTY: {interview_requirement.get("overall_difficulty", "Medium")}

        SPECIAL INSTRUCTIONS:
        {interview_requirement.get("special_instructions", "Follow standard interview guidelines")}

        INTERVIEWER NOTES:
        {interview_requirement.get("interviewer_notes", "N/A")}

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return section

    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API with schema validation"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert interview question generator. Generate comprehensive, time-optimized interview questions with detailed follow-ups and evaluation criteria. Strictly follow the evaluation guidelines provided.",
            },
            {"role": "user", "content": prompt},
        ]

        response = llm.generate_json(
            messages=messages, model=self.model, schema=self.schema
        )

        # Track metrics
        self.api_calls += 1
        if response and response.usage:
            self.input_tokens += response.usage.prompt_tokens
            self.output_tokens += response.usage.completion_tokens

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from LLM response.")
        return json.loads(content)

    def save_to_file(
        self, questions: Dict[str, Any], output_file: str, verbose: bool = True
    ) -> None:
        """Save generated questions to JSON file"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)

        if verbose:
            print(f"💾 Questions saved to: {output_file}\n")

    def _calculate_cost(self) -> float:
        """Calculate estimated cost"""
        input_cost = (self.input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (self.output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
