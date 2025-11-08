import json
from typing import Dict, Any
from openai import OpenAI
from schema.interview import ExtractionJdMetrics as ExtractionMetrics
from schema.intervew_requirements import interview_requirements_schema
from ai_agents.llm.openai import OpenAI_LLM
from security.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore


class InterviewRequirementsExtractor:
    """
    Extract structured interview requirements from user-written text

    Parses:
    - Interview type and focus areas
    - Technical topics and skills to assess
    - Evaluation criteria and weights
    - What to judge vs what NOT to judge
    - Red flags and green flags
    - Question categories and difficulty levels
    """

    # GPT-4o-mini pricing
    INPUT_PRICE_PER_1K = 0.000150
    OUTPUT_PRICE_PER_1K = 0.000600

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize interview requirements extractor

        Args:
            openai_api_key: Your OpenAI API key
            model: OpenAI model to use
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
        self.schema = self._get_schema()

        # Metrics
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def _get_schema(self) -> dict:
        """JSON schema for structured interview requirements extraction"""
        return interview_requirements_schema

    def extract(
        self, interview_requirements: str, verbose: bool = False
    ) -> tuple[Dict[str, Any], ExtractionMetrics]:
        """
        Extract structured requirements from interview description

        Args:
            interview_requirements: Raw interview requirements text written by user
            verbose: Print extraction progress

        Returns:
            (extracted_data, metrics)
        """
        if verbose:
            print("🚀 Starting interview requirements extraction...")
            print(f"📄 Model: {self.model}\n")

        # Reset metrics
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

        # Extract requirements
        if verbose:
            print("📋 Parsing interview requirements...")

        extracted_data = self._extract_requirements(interview_requirements)

        # Calculate metrics
        cost = self._calculate_cost()

        metrics = ExtractionMetrics(
            api_calls=self.api_calls,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cost_estimate=cost,
        )

        if verbose:
            print("✅ Extraction complete!")
            print(f"💰 Cost: ${cost:.4f}\n")

        return extracted_data, metrics

    def _extract_requirements(self, interview_requirements: str) -> Dict[str, Any]:
        """Extract requirements using GPT-4o-mini with structured output"""
        messages = [
            {
                "role": "system",
                "content": """You are an expert interview design analyzer. Extract ALL interview requirements and guidelines from the provided text.

            Extract information systematically:
            - Identify interview type, position, and experience level
            - List all technical topics, languages, and frameworks to cover
            - Extract skills to assess (technical and soft skills)
            - Identify evaluation criteria with weights
            - Determine what TO judge and what NOT to judge
            - List red flags (negative indicators) and green flags (positive indicators)
            - Extract question categories with topics and time allocations
            - Identify special instructions and preparation guidance

            CRITICAL INSTRUCTIONS:
            - For boolean fields (judge_for, do_not_judge): Set to true if mentioned, false otherwise
            - Use empty strings "" for missing text fields
            - Use empty arrays [] for missing lists
            - Extract difficulty levels accurately
            - Preserve all specific technical requirements""",
            },
            {
                "role": "user",
                "content": f"Extract structured interview requirements from this text:\n\n{interview_requirements}",
            },
        ]

        response = llm.generate_json(
            messages=messages, model=self.model, schema=self.schema
        )

        # Track metrics
        self.api_calls += 1
        if response.usage:
            self.input_tokens += response.usage.prompt_tokens
            self.output_tokens += response.usage.completion_tokens

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Response content is None")
        return json.loads(content)

    def extract_to_file(
        self, interview_requirements: str, output_file: str, verbose: bool = False
    ) -> None:
        """Extract and save results to JSON file"""
        extracted_data, metrics = self.extract(interview_requirements, verbose)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)

        if verbose:
            print(f"💾 Results saved to: {output_file}\n")

    def _calculate_cost(self) -> float:
        """Calculate estimated cost based on token usage"""
        input_cost = (self.input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (self.output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
