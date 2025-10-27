"""
Optimized Parallel Resume Extractor for GPT-4o-mini
Best for 10-30 page documents with parallel chunk processing

Dependencies:
- Required: openai, PyMuPDF (fitz)
- Optional: pytesseract, Pillow (for Tesseract OCR mode)
- Optional: Pillow (for Vision API mode)

Install:
  pip install openai PyMuPDF
  
Optional for image-based PDFs:
  pip install Pillow pytesseract
"""

import io
import fitz
import json
from typing import Dict, Any, List
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from schema.interview import ExtractionResumeMetrics as ExtractionMetrics
import time
import warnings
from ai_agents.llm.openai import OpenAI_LLM
from schema.resume_parser import resume_extraction_schema, empty_schema
from utils.config import API_KEY
llm = OpenAI_LLM(api_key=API_KEY)

# Optional dependencies
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from PIL import Image
    import base64
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


class OptimizedResumeExtractor:
    """
    High-performance resume extractor optimized for GPT-4o-mini
    - Parallel chunk processing
    - Smart token management
    - Cost optimization
    - Fast merging algorithm
    
    Supports multiple extraction modes:
    - TEXT: Fast text extraction (always available)
    - VISION: GPT-4 Vision API (requires Pillow)
    - TESSERACT: Tesseract OCR + LLM (requires pytesseract + Pillow)
    - AUTO: Automatic mode selection
    """
    
    # GPT-4o-mini pricing (as of 2024)
    INPUT_PRICE_PER_1K = 0.000150   # $0.15 per 1M tokens
    OUTPUT_PRICE_PER_1K = 0.000600  # $0.60 per 1M tokens
    
    def __init__(
        self, 
        openai_api_key: str,
        pages_per_chunk: int = 5,
        max_workers: int = 5,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize extractor
        
        Args:
            openai_api_key: Your OpenAI API key
            pages_per_chunk: Pages to process per chunk (3-7 recommended)
            max_workers: Parallel threads (5-10 recommended)
            model: OpenAI model to use
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.pages_per_chunk = pages_per_chunk
        self.max_workers = max_workers
        self.model = model
        self.schema = self._get_schema()
        
        # Metrics
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        
        # Check optional dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check and warn about optional dependencies"""
        if not PILLOW_AVAILABLE:
            warnings.warn(
                "Pillow not installed. Vision and Tesseract modes will be unavailable.\n"
                "Install with: pip install Pillow",
                ImportWarning
            )
        
        if not TESSERACT_AVAILABLE:
            warnings.warn(
                "pytesseract not installed. Tesseract mode will be unavailable.\n"
                "Install with: pip install pytesseract\n"
                "Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract",
                ImportWarning
            )
    
    def get_available_modes(self) -> List[str]:
        """Get list of available extraction modes based on installed dependencies"""
        modes = ["text", "auto"]  # Always available
        
        if PILLOW_AVAILABLE:
            modes.append("vision")
        
        if PILLOW_AVAILABLE and TESSERACT_AVAILABLE:
            modes.append("tesseract")
        
        return modes
    
    def _get_schema(self) -> dict:
        """Extraction schema for structured output"""
        return resume_extraction_schema
    
    def extract_from_pdf(self, pdf_path: str, ocr_method: str = "tesseract",verbose: bool = True) -> tuple[Dict[str, Any], ExtractionMetrics]:
        """
        Extract resume data from PDF with parallel processing
        
        Returns:
            (extracted_data, metrics)
        """
        start_time = time.time()
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        
        if verbose:
            print("🚀 Starting resume extraction...")
            print(f"📄 Model: {self.model}")
            print(f"⚙️  Config: {self.pages_per_chunk} pages/chunk, {self.max_workers} workers\n")
        
        # Step 1: Extract text from PDF
        if verbose:
            print("📖 Reading PDF...")
        doc = fitz.open(pdf_path)
        pages_text = []
        for page_num in range(len(doc)):
            text = doc[page_num].get_text()
            if not text.strip():  # type: ignore # If page has no text, try OCR
                if ocr_method != "none":
                    if verbose:
                        print(f"🔍 Page {page_num + 1} is scanned, trying OCR via {ocr_method}...")
                    page_image = doc[page_num].get_pixmap()

                    if ocr_method == "tesseract":
                        text = self._extract_with_tesseract(page_image)
                        print("Tesseract OCR Result:", text)

                    elif ocr_method == "vision":
                        text = self._extract_with_vision(page_image)
                        print("Vision OCR Result:", text)

            if text.strip():  # type: ignore # Only include non-empty pages
                pages_text.append(text)
        doc.close()
        
        num_pages = len(pages_text)
        if verbose:
            print(f"✓  Extracted {num_pages} pages\n")
        
        # Step 2: Create chunks
        chunks = self._create_chunks(pages_text)
        if verbose:
            print(f"📦 Created {len(chunks)} chunks for parallel processing\n")
        
        # Step 3: Parallel extraction
        if verbose:
            print("⚡ Processing chunks in parallel...")
        partial_results = self._extract_parallel(chunks, verbose)
        
        # Step 4: Merge results
        if verbose:
            print("\n🔄 Merging results...")
        merged_result = self._merge_results(partial_results)
        
        # Calculate metrics
        elapsed = time.time() - start_time
        cost = self._calculate_cost()
        
        metrics = ExtractionMetrics(
            total_pages=num_pages,
            chunks_processed=len(chunks),
            api_calls=self.api_calls,
            total_time=elapsed,
            cost_estimate=cost
        )
        
        if verbose:
            print("✅ Extraction complete!\n")
            print(metrics)
        
        return merged_result, metrics
    
    def _extract_with_tesseract(self, page_image):
        img = Image.frombytes("RGB", [page_image.width, page_image.height], page_image.samples) # type: ignore
        img.show()
        return pytesseract.image_to_string(img) # type: ignore

    def _extract_with_vision(self, page_image):
        # Convert Pixmap → PNG bytes
        img = Image.frombytes("RGB", (page_image.width, page_image.height), page_image.samples) # type: ignore
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8") # type: ignore
        return llm.extract_text_from_image(img_base64) # type: ignore


    def _create_chunks(self, pages_text: List[str]) -> List[str]:
        """Create optimal chunks from pages"""
        chunks = []
        current_chunk = []
        
        for i, page_text in enumerate(pages_text):
            current_chunk.append(page_text)
            
            # Create chunk when reaching target size or last page
            if len(current_chunk) >= self.pages_per_chunk or i == len(pages_text) - 1:
                chunks.append("\n\n--- PAGE BREAK ---\n\n".join(current_chunk))
                current_chunk = []
        
        return chunks
    
    def _extract_parallel(self, chunks: List[str], verbose: bool = True) -> List[Dict[str, Any]]:
        """Extract data from chunks in parallel"""
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_chunk = {
                executor.submit(self._extract_chunk, i, chunk): i 
                for i, chunk in enumerate(chunks)
            }
            
            # Process as they complete
            for future in as_completed(future_to_chunk):
                chunk_idx = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append((chunk_idx, result))
                    completed += 1
                    if verbose:
                        print(f"  ✓ Chunk {completed}/{len(chunks)} processed")
                except Exception as e:
                    if verbose:
                        print(f"  ✗ Chunk {chunk_idx + 1} failed: {e}")
                    results.append((chunk_idx, self._empty_result()))
        
        # Sort by original chunk order
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]
    
    def _extract_chunk(self, chunk_idx: int, chunk_text: str) -> Dict[str, Any]:
        """Extract data from a single chunk"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert resume parser. Extract ALL information from this resume section accurately. Use empty strings \"\" for missing text fields and empty arrays [] for missing lists."
            },
            {
                "role": "user",
                "content": f"Extract resume information from this text:\n\n{chunk_text}"
            }
        ]
        
        # response = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=messages,
        #     response_format={
        #         "type": "json_schema",
        #         "json_schema": self.schema
        #     }
        # )
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
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return empty_schema
    
    def _merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intelligently merge multiple partial results
        Optimized merging algorithm for speed
        """
        merged = self._empty_result()
        
        # Merge personal info (first non-null wins)
        for result in results:
            for key, value in result.get("personal_info", {}).items():
                if value and not merged["personal_info"].get(key):
                    merged["personal_info"][key] = value
        
        # Merge professional summary (longest wins)
        summaries = [r.get("professional_summary") for r in results if r.get("professional_summary")]
        if summaries:
            merged["professional_summary"] = max(summaries, key=len) # type: ignore
        
        # Merge skills (deduplicate, case-insensitive)
        skills_set = set()
        skills_map = {}  # lowercase -> original case
        for result in results:
            for skill in result.get("skills", []):
                skill_lower = skill.lower()
                if skill_lower not in skills_set:
                    skills_set.add(skill_lower)
                    skills_map[skill_lower] = skill
        merged["skills"] = sorted(skills_map.values())
        
        # Merge languages (deduplicate)
        langs_set = set()
        for result in results:
            langs_set.update(result.get("languages", []))
        merged["languages"] = sorted(list(langs_set))
        
        # Merge experience (deduplicate by company+position)
        seen_exp = set()
        for result in results:
            for exp in result.get("experience", []):
                key = (exp.get("company", "").lower(), exp.get("position", "").lower())
                if key not in seen_exp and key != ("", ""):
                    seen_exp.add(key)
                    merged["experience"].append(exp)
        
        # Merge education (deduplicate by institution+degree)
        seen_edu = set()
        for result in results:
            for edu in result.get("education", []):
                key = (edu.get("institution", "").lower(), edu.get("degree", "").lower())
                if key not in seen_edu and key != ("", ""):
                    seen_edu.add(key)
                    merged["education"].append(edu)
        
        # Merge certifications (deduplicate by name)
        seen_certs = set()
        for result in results:
            for cert in result.get("certifications", []):
                cert_name = cert.get("name", "").lower()
                if cert_name and cert_name not in seen_certs:
                    seen_certs.add(cert_name)
                    merged["certifications"].append(cert)
        
        # Merge projects (deduplicate by name)
        seen_projects = set()
        for result in results:
            for proj in result.get("projects", []):
                proj_name = proj.get("name", "").lower()
                if proj_name and proj_name not in seen_projects:
                    seen_projects.add(proj_name)
                    merged["projects"].append(proj)
        
        return merged
    
    def _calculate_cost(self) -> float:
        """Calculate estimated cost based on token usage"""
        input_cost = (self.input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (self.output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
