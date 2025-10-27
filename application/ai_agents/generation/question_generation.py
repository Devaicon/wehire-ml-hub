import json
from typing import Dict, Any, List
from openai import OpenAI
from ai_agents.llm.openai import OpenAI_LLM
from schema.interview import InterviewConfig, InterviewMetrics
from enums.interview import DifficultyLevel, InterviewPhase, QuestionSource
from schema.question_generation import interview_question_schema
from utils.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)

class InterviewQuestionGenerator:
    """
    Generate customized interview questions based on TIME DURATION:
    - Specify interview duration (e.g., 10, 30, 60 minutes)
    - System automatically calculates optimal number of questions
    - Accounts for answer length, transitions, and buffer time
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
        config: InterviewConfig,
        verbose: bool = True
    ) -> tuple[Dict[str, Any], InterviewMetrics]:
        """
        Generate interview questions based on time duration
        
        Args:
            job_requirements: Extracted job requirements JSON
            candidate_cv: Extracted resume data JSON
            config: InterviewConfig with TIME-BASED parameters
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
            print(f"🎯 Configuration: {config.phase.value} - {config.difficulty_level.value}")
            print(f"📊 Source: {config.question_source.value}")
            print(f"⏳ Answer Length: {config.question_length}\n")
        
        # Build prompt based on source type
        if config.question_source == QuestionSource.CLIENT_PROVIDED:
            if verbose:
                print("✓ Using client-provided questions only")
            questions = self._format_client_questions(config.client_questions, config)
        
        elif config.question_source == QuestionSource.AI_GENERATED:
            if verbose:
                print("🤖 Generating all questions with AI...")
            questions = self._generate_ai_questions(
                job_requirements, candidate_cv, config, verbose
            )
        
        else:  # HYBRID
            if verbose:
                print(f"🔄 Using hybrid approach: {config.client_questions_count} client + "
                      f"{config.total_questions - config.client_questions_count} AI questions")
            questions = self._generate_hybrid_questions(
                job_requirements, candidate_cv, config, verbose
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
            estimated_actual_duration_minutes=questions["interview_summary"]["estimated_interview_duration_minutes"],
            buffer_time_minutes=buffer_time
        )
        
        if verbose:
            print("\n✅ Interview generation complete!\n")
            print(metrics)
        
        return questions, metrics
    
    def _format_client_questions(self, questions: List[str], config: InterviewConfig) -> Dict[str, Any]:
        """Format client-provided questions with time estimates"""
        answer_times = {"short": 2, "medium": 4, "long": 7}
        time_per_q = answer_times[config.question_length] + 1  # +1 for asking
        
        formatted_questions = []
        for idx, question in enumerate(questions[:config.total_questions], 1):
            formatted_questions.append({
                "question_id": idx,
                "question": question,
                "category": "Client-Provided",
                "difficulty": config.difficulty_level.value,
                "expected_answer_type": config.question_length,
                "estimated_time_minutes": time_per_q,
                "key_points": [],
                "follow_up_questions": [],
                "why_asked": "Provided by client",
                "relevance_to_cv": "To be determined during interview"
            })
        
        total_time = len(formatted_questions) * time_per_q
        
        return {
            "questions": formatted_questions,
            "interview_summary": {
                "total_questions": len(formatted_questions),
                "difficulty_distribution": {
                    "easy": len([q for q in formatted_questions if config.difficulty_level == DifficultyLevel.EASY]),
                    "medium": len([q for q in formatted_questions if config.difficulty_level == DifficultyLevel.MEDIUM]),
                    "hard": len([q for q in formatted_questions if config.difficulty_level == DifficultyLevel.HARD])
                },
                "question_categories": ["Client-Provided"],
                "estimated_interview_duration_minutes": total_time
            }
        }
    
    def _generate_ai_questions(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        config: InterviewConfig,
        verbose: bool
    ) -> Dict[str, Any]:
        """Generate all questions using AI"""
        prompt = self._build_generation_prompt(
            job_requirements, candidate_cv, config, all_ai=True
        )
        return self._call_api(prompt)
    
    def _generate_hybrid_questions(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        config: InterviewConfig,
        verbose: bool
    ) -> Dict[str, Any]:
        """Generate hybrid questions (client + AI)"""
        client_qs_section = f"""
CLIENT PROVIDED QUESTIONS (Must include these):
{json.dumps(config.client_questions, indent=2)}

Include these {config.client_questions_count} questions as-is, then generate {config.total_questions - config.client_questions_count} additional AI questions.
"""
        
        prompt = self._build_generation_prompt(
            job_requirements, candidate_cv, config, all_ai=False,
            client_questions_section=client_qs_section
        )
        return self._call_api(prompt)
    
    def _build_generation_prompt(
        self,
        job_requirements: Dict[str, Any],
        candidate_cv: Dict[str, Any],
        config: InterviewConfig,
        all_ai: bool = True,
        client_questions_section: str = ""
    ) -> str:
        """Build the prompt for question generation"""
        
        phase_descriptions = {
            InterviewPhase.FIRST: "screening round - focus on basic fit and foundational skills",
            InterviewPhase.SECOND: "technical round - dive deep into technical expertise and problem-solving",
            InterviewPhase.FINAL: "executive/final round - assess culture fit, leadership, and final suitability"
        }
        
        answer_length_guidance = {
            "short": "1-2 minute answers expected",
            "medium": "3-5 minute answers expected",
            "long": "5-10 minute answers expected"
        }
        
        time_per_question = {
            "short": 3,   # 2 min answer + 1 min asking/transition
            "medium": 5,  # 4 min answer + 1 min asking/transition
            "long": 8     # 7 min answer + 1 min asking/transition
        }
        
        prompt = f"""You are an expert interview panel coordinator. Generate interview questions for a {config.interview_duration_minutes}-minute interview.

TIME CONSTRAINTS:
- Total Interview Duration: {config.interview_duration_minutes} minutes
- Questions to Generate: {config.total_questions}
- Time per Question: ~{time_per_question[config.question_length]} minutes (including answer + asking)
- Buffer Time: {config.buffer_time_percent * 100}% for intro, transitions, wrap-up

INTERVIEW CONTEXT:
- Phase: {config.phase.value} ({phase_descriptions[config.phase]})
- Difficulty: {config.difficulty_level.value}
- Answer Length: {answer_length_guidance[config.question_length]}
- Question Source: {config.question_source.value}

JOB REQUIREMENTS:
{json.dumps(job_requirements, indent=2)}

CANDIDATE PROFILE:
{json.dumps(candidate_cv, indent=2)}

{client_questions_section}

REQUIREMENTS:
1. Generate EXACTLY {config.total_questions} questions (optimized for {config.interview_duration_minutes} minutes)
2. Each question should have estimated_time_minutes set to {time_per_question[config.question_length]}
3. Tailor questions to match the candidate's experience and the job role
4. For {config.phase.value}, adjust question depth and scope appropriately
5. Include follow-up questions for each main question
6. Provide key points that indicate a good answer
7. Explain why each question is relevant to this role
8. Reference the candidate's CV when relevant
9. Ensure difficulty level is consistent: {config.difficulty_level.value}
10. Mix question types: technical, behavioral, situational, problem-solving
11. Questions should expose gaps or strengths relative to job requirements
12. Prioritize most important questions first (in case interview runs short)

GENERATE {config.total_questions} TIME-OPTIMIZED INTERVIEW QUESTIONS."""
        
        return prompt
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API with schema validation"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert interview question generator. Generate comprehensive, time-optimized interview questions with detailed follow-ups and evaluation criteria."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = llm.generate_json(
            messages=messages,
            model=self.model,
            schema=self.schema
        )
        # Track metrics
        self.api_calls += 1
        self.input_tokens += response.usage.prompt_tokens
        self.output_tokens += response.usage.completion_tokens
        
        return json.loads(response.choices[0].message.content)
    
    def save_to_file(self, questions: Dict[str, Any], output_file: str, verbose: bool = True) -> None:
        """Save generated questions to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(questions, f, indent=2)
        
        if verbose:
            print(f"💾 Questions saved to: {output_file}\n")
    
    def _calculate_cost(self) -> float:
        """Calculate estimated cost"""
        input_cost = (self.input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (self.output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
