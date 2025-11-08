import json
from typing import Dict, Any
from openai import OpenAI
from schema.interview import ExtractionJdMetrics as ExtractionMetrics
from ai_agents.llm.openai import OpenAI_LLM
from schema.jd_parser import jd_extraction_schema
from security.config import API_KEY

llm = OpenAI_LLM(api_key=API_KEY)  # type: ignore


class JobDescriptionExtractor:
    """
    Extract structured job requirements from job descriptions
    Returns skills, qualifications, experience, responsibilities, etc.

    Supports:
    - Technical and soft skills extraction
    - Required vs. preferred qualifications
    - Experience level requirements
    - Responsibilities and duties
    - Salary/compensation info
    - Benefits
    """

    # GPT-4o-mini pricing
    INPUT_PRICE_PER_1K = 0.000150
    OUTPUT_PRICE_PER_1K = 0.000600

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize job description extractor

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
        """JSON schema for structured job requirement extraction"""
        return jd_extraction_schema

    def extract(
        self, job_description: str, verbose: bool = True
    ) -> tuple[Dict[str, Any], ExtractionMetrics]:
        """
        Extract structured requirements from job description

        Args:
            job_description: Raw job description text
            verbose: Print extraction progress

        Returns:
            (extracted_data, metrics)
        """
        if verbose:
            print("🚀 Starting job requirement extraction...")
            print(f"📄 Model: {self.model}\n")

        # Reset metrics
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

        # Extract requirements
        if verbose:
            print("📋 Parsing job description...")

        extracted_data = self._extract_requirements(job_description)

        # Calculate metrics
        cost = self._calculate_cost()

        metrics = ExtractionMetrics(
            api_calls=self.api_calls,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cost_estimate=cost,
        )

        if verbose:
            print("✅ Extraction complete!\n")
            print(metrics)

        return extracted_data, metrics

    def _extract_requirements(self, job_description: str) -> Dict[str, Any]:
        """Extract requirements using GPT-4o-mini with structured output"""
        messages = [
            {
                "role": "system",
                "content": """You are an expert job description analyzer. Extract ALL job requirements and information from the provided job description.

                Extract information systematically:
                - Identify required vs preferred skills and qualifications
                - Extract technical and soft skills
                - List key responsibilities
                - Identify education and certification requirements
                - Extract salary, benefits, and location info
                - Determine remote status and job type

                Use empty strings "" for missing text fields and empty arrays [] for missing lists.""",
            },
            {
                "role": "user",
                "content": f"Extract structured job requirements from this job description:\n\n{job_description}",
            },
        ]

        response = llm.generate_json(
            messages=messages, model=self.model, schema=self.schema
        )

        # Track metrics
        self.api_calls += 1
        if response.usage is not None:
            self.input_tokens += getattr(response.usage, "prompt_tokens", 0)
            self.output_tokens += getattr(response.usage, "completion_tokens", 0)

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content received from LLM response")

        return json.loads(content)

    def extract_to_file(
        self, job_description: str, output_file: str, verbose: bool = True
    ) -> None:
        """Extract and save results to JSON file"""
        extracted_data, metrics = self.extract(job_description, verbose)

        with open(output_file, "w") as f:
            json.dump(extracted_data, f, indent=2)

        if verbose:
            print(f"💾 Results saved to: {output_file}\n")

    def _calculate_cost(self) -> float:
        """Calculate estimated cost based on token usage"""
        input_cost = (self.input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (self.output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
