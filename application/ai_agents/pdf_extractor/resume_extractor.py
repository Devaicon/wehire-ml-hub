import io
import fitz
import json
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import ValidationError
from ai_agents.prompts.resumeparser import SYSTEM_PROMPT
from schema.interview import ExtractionResumeMetrics as ExtractionMetrics
import time
from ai_agents.llm.openai import OpenAI_LLM
from schema.resume_parser import ResumeData, get_resume_extraction_schema
from security.config import API_KEY

if not API_KEY:
    raise ValueError("API_KEY must be set")
llm = OpenAI_LLM(api_key=API_KEY)

# OCR dependencies
try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False

try:
    from PIL import Image
    import base64

    PILLOW_AVAILABLE = True
except ImportError:
    Image = None
    base64 = None
    PILLOW_AVAILABLE = False


class OptimizedResumeExtractor:
    """
    Page-level parallel resume extractor
    - 1 page: Single API call (fastest)
    - 2+ pages: Parallel processing per page (maximum speed)
    - Default OCR: Tesseract (faster), Vision API as fallback
    """

    INPUT_PRICE_PER_1K = 0.000150
    OUTPUT_PRICE_PER_1K = 0.000600

    def __init__(
        self,
        pages_per_chunk: int = 1,  # Process each page separately
        max_workers: int = 5,  # High parallelism for pages
        model: str = "gpt-4o-mini",
    ):
        self.pages_per_chunk = pages_per_chunk
        self.max_workers = max_workers
        self.model = model
        self.schema = get_resume_extraction_schema()

        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def extract_from_pdf(
        self,
        pdf_path: str,
        ocr_method: str = "tesseract",  # Default to tesseract (faster)
        verbose: bool = False,
    ) -> tuple[Dict[str, Any], ExtractionMetrics]:
        """
        Extract with page-level parallelization

        Args:
            pdf_path: Path to PDF file
            ocr_method: "none", "tesseract" (default), or "vision"
            verbose: Print progress
        """
        start_time = time.time()
        self.api_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

        if verbose:
            print("🚀 Starting extraction...")

        # Extract text from PDF
        pages_text = self._extract_text_fast(pdf_path, ocr_method, verbose)
        num_pages = len(pages_text)

        if verbose:
            print(f"📄 {num_pages} page(s) extracted")

        # Choose strategy based on page count
        if num_pages == 1:
            if verbose:
                print("⚡ Single-page mode (1 API call)")
            extracted_data = self._extract_single_page(pages_text[0], verbose)
        else:
            if verbose:
                print(f"⚙️  Parallel mode ({num_pages} API calls in parallel)")
            extracted_data = self._extract_parallel_pages(pages_text, verbose)

        # Fast validation
        validated_result = self._validate_fast(extracted_data)
        validated_result = self._quick_cleanup(validated_result)

        elapsed = time.time() - start_time
        cost = self._calculate_cost()

        metrics = ExtractionMetrics(
            total_pages=num_pages,
            chunks_processed=num_pages,
            api_calls=self.api_calls,
            total_time=elapsed,
            cost_estimate=cost,
        )

        if verbose:
            print(
                f"✅ Done in {elapsed:.2f}s | ${cost:.4f} | {self.api_calls} API calls"
            )

        return validated_result, metrics

    def _extract_text_fast(
        self,
        pdf_path: str,
        ocr_method: str,
        verbose: bool,
        vision_required: bool = False,
    ) -> List[str]:
        """Fast text extraction with OCR fallback"""
        doc = fitz.open(pdf_path)
        pages_text = []

        for page_num in range(len(doc)):
            # Force plain text extraction to ensure a str is returned
            text = doc[page_num].get_text("text")
            # OCR fallback if page is empty or has very little text
            if len(text.strip()) < 50 and ocr_method != "none":  # type: ignore
                if verbose:
                    print(f"  🔍 OCR page {page_num + 1} ({ocr_method})...")

                page_image = doc[page_num].get_pixmap(
                    dpi=150
                )  # Higher DPI for better quality

                if ocr_method == "tesseract" and TESSERACT_AVAILABLE:
                    text = self._extract_with_tesseract(page_image, verbose)
                elif ocr_method == "vision" and PILLOW_AVAILABLE and vision_required:
                    text = self._extract_with_vision_fast(page_image)
                elif ocr_method == "tesseract" and not TESSERACT_AVAILABLE:
                    if verbose:
                        print("  ⚠️  Tesseract not available, trying Vision API...")
                    if PILLOW_AVAILABLE and vision_required:
                        text = self._extract_with_vision_fast(page_image)

            if text.strip():  # type: ignore
                pages_text.append(text)

        doc.close()
        return pages_text

    def _extract_with_tesseract(self, page_image, verbose: bool = False) -> str:
        """Extract text using Tesseract OCR (faster than Vision API)"""
        if not PILLOW_AVAILABLE or not TESSERACT_AVAILABLE:
            return ""

        try:
            # Convert pixmap to PIL Image
            img = Image.frombytes(  # type: ignore
                "RGB", (page_image.width, page_image.height), page_image.samples
            )

            # Preprocess for better OCR
            # Convert to grayscale for better text recognition
            img = img.convert("L")

            # Extract text with Tesseract
            # PSM 6 = Assume a single uniform block of text
            text = pytesseract.image_to_string(img, config="--psm 6")  # type: ignore

            return text if text else ""

        except Exception as e:
            if verbose:
                print(f"  ⚠️  Tesseract OCR failed: {e}")
            return ""

    def _extract_with_vision_fast(self, page_image) -> str:
        """Fast vision OCR using OpenAI API"""
        if not PILLOW_AVAILABLE:
            return ""

        try:
            img = Image.frombytes(  # type: ignore
                "RGB", (page_image.width, page_image.height), page_image.samples
            )

            # Optimize image size for faster upload
            max_size = 1024
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)  # type: ignore

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=False)
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")  # type: ignore

            return llm.extract_text_from_image(img_base64)  # type: ignore

        except Exception as e:
            print(f"  ⚠️  Vision OCR failed: {e}")
            return ""

    def _extract_single_page(self, page_text: str, verbose: bool) -> Dict[str, Any]:
        """
        Extract from single page (no merging needed)
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": page_text},
        ]

        if verbose:
            print("  Processing page 1...")

        response = llm.generate_json(
            messages=messages, model=self.model, schema=self.schema
        )

        self.api_calls += 1
        # Safely handle missing usage info
        usage = getattr(response, "usage", None)
        prompt_tokens = usage.prompt_tokens if usage is not None else 0
        completion_tokens = usage.completion_tokens if usage is not None else 0
        self.input_tokens += prompt_tokens
        self.output_tokens += completion_tokens

        if verbose:
            print(f"  ✓ Complete ({prompt_tokens} → {completion_tokens} tokens)")

        return json.loads(response.choices[0].message.content or "{}")

    def _extract_parallel_pages(
        self, pages_text: List[str], verbose: bool
    ) -> Dict[str, Any]:
        """
        Extract from multiple pages in parallel (one API call per page)
        """
        results = []
        completed = 0
        total_pages = len(pages_text)

        if verbose:
            print(f"  Launching {total_pages} parallel extractions...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all pages at once
            future_to_page = {
                executor.submit(self._extract_page, page_num, page_text): page_num
                for page_num, page_text in enumerate(pages_text)
            }

            # Collect results as they complete
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    result = future.result()
                    results.append((page_num, result))
                    completed += 1
                    if verbose:
                        print(f"  ✓ Page {page_num + 1}/{total_pages} done")
                except Exception as e:
                    if verbose:
                        print(f"  ✗ Page {page_num + 1} failed: {e}")
                    results.append((page_num, self._empty_result()))

        # Sort by page number to maintain order
        results.sort(key=lambda x: x[0])
        page_results = [r[1] for r in results]

        if verbose:
            print(f"  🔄 Merging {len(page_results)} results...")

        return self._merge_pages(page_results)

    def _extract_page(self, page_num: int, page_text: str) -> Dict[str, Any]:
        """
        Extract data from a single page
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": page_text},
        ]

        response = llm.generate_json(
            messages=messages, model=self.model, schema=self.schema
        )

        self.api_calls += 1
        if response.usage is not None:
            self.input_tokens += response.usage.prompt_tokens
            self.output_tokens += response.usage.completion_tokens

        return json.loads(response.choices[0].message.content or "{}")

    def _merge_pages(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intelligently merge results from multiple pages
        """
        if len(results) == 1:
            return results[0]

        merged = self._empty_result()

        # Personal Info - take most complete (usually on first page)
        for result in results:
            for key, value in result.get("personalInfo", {}).items():
                current = merged["personalInfo"].get(key, "")
                if value and len(str(value)) > len(str(current)):
                    merged["personalInfo"][key] = value

        # About Me - take longest description
        about_texts = [r.get("aboutMe", {}).get("about", "") for r in results]
        about_texts = [a.strip() for a in about_texts if a and len(a.strip()) > 20]
        if about_texts:
            merged["aboutMe"]["about"] = max(about_texts, key=len)

        # Skills - deduplicate across pages (case-insensitive)
        skills_map = {}
        for result in results:
            for skill in result.get("professionalSkills", {}).get("skills", []):
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                if skill_lower not in skills_map and skill_clean:
                    skills_map[skill_lower] = skill_clean
        merged["professionalSkills"]["skills"] = sorted(skills_map.values())

        # Work Experience - deduplicate by company + title
        seen_exp = set()
        for result in results:
            for exp in result.get("workExperience", []):
                company = exp.get("companyName", "").strip()
                title = exp.get("jobTitle", "").strip()
                key = (company.lower(), title.lower())

                if key not in seen_exp and company and title:
                    seen_exp.add(key)
                    merged["workExperience"].append(exp)

        # Sort by start date (most recent first)
        merged["workExperience"].sort(
            key=lambda x: x.get("startEmploymentPeriod", ""), reverse=True
        )

        # Education - deduplicate by institution + degree
        seen_edu = set()
        for result in results:
            for edu in result.get("education", []):
                institution = edu.get("universityName", "").strip()
                degree = edu.get("degreeLevel", "").strip()
                key = (institution.lower(), degree.lower())

                if key not in seen_edu and institution and degree:
                    seen_edu.add(key)
                    merged["education"].append(edu)

        merged["education"].sort(
            key=lambda x: x.get("startDateOfStudy", ""), reverse=True
        )

        # Projects - deduplicate by name
        seen_projects = set()
        for result in results:
            for proj in result.get("workProjects", []):
                proj_name = proj.get("projectName", "").strip()
                if proj_name and proj_name.lower() not in seen_projects:
                    seen_projects.add(proj_name.lower())
                    merged["workProjects"].append(proj)

        # Links - deduplicate by URL
        seen_links = set()
        for result in results:
            for link in result.get("links", {}).get("socialMedias", []):
                link_url = link.get("link", "").strip().lower()
                if link_url and link_url not in seen_links:
                    seen_links.add(link_url)
                    merged["links"]["socialMedias"].append(link)

        # Languages - deduplicate by name
        seen_langs = set()
        for result in results:
            for lang in result.get("language", {}).get("languages", []):
                lang_name = lang.get("langName", "").strip()
                if lang_name and lang_name.lower() not in seen_langs:
                    seen_langs.add(lang_name.lower())
                    merged["language"]["languages"].append(lang)

        # Job Preferences - take first non-empty
        for result in results:
            prefs = result.get("jobPreferences", [])
            if prefs and any(p.get("jobCategory") for p in prefs):
                merged["jobPreferences"] = prefs
                break

        # # Benefits - merge all unique
        # all_benefits = set()
        # for result in results:
        #     for benefit in result.get("preferredJobBenefits", []):
        #         for b in benefit.get("benefits", []):
        #             if b:
        #                 all_benefits.add(b.strip())

        # if all_benefits:
        #     merged["preferredJobBenefits"] = [{"benefits": sorted(all_benefits)}]

        # Achievements - deduplicate by award name
        seen_achievements = set()
        for result in results:
            for achievement in result.get("jobAchievements", []):
                award_name = achievement.get("AwardName", "").strip()
                if award_name and award_name.lower() not in seen_achievements:
                    seen_achievements.add(award_name.lower())
                    merged["jobAchievements"].append(achievement)

        # Filters - take most specific (non-"any" values)
        for result in results:
            filters = result.get("filters", {})
            for key, value in filters.items():
                if value != "any" and merged["filters"].get(key) == "any":
                    merged["filters"][key] = value

        # Tags - merge and deduplicate (case-insensitive)
        tags_map = {}
        for result in results:
            for tag in result.get("tags", []):
                tag_clean = tag.strip()
                tag_lower = tag_clean.lower()
                if tag_lower not in tags_map and tag_clean:
                    tags_map[tag_lower] = tag_clean

        merged["tags"] = sorted(tags_map.values())

        # Ensure minimum tags
        if not merged["tags"]:
            merged["tags"] = ["Professional"]

        return merged

    def _validate_fast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fast validation"""
        try:
            validated = ResumeData(**data)
            return validated.model_dump()
        except ValidationError:
            # Quick fix for critical fields
            if not data.get("tags"):
                data["tags"] = ["Professional"]

            # Ensure required objects
            for key in [
                "personalInfo",
                "aboutMe",
                "professionalSkills",
                "links",
                "language",
                "filters",
            ]:
                if key not in data or not data[key]:
                    data[key] = {}

            # Ensure required arrays
            for key in [
                "workExperience",
                "education",
                "workProjects",
                "jobPreferences",
                # "preferredJobBenefits",
                "jobAchievements",
            ]:
                if key not in data:
                    data[key] = []

            return data

    def _quick_cleanup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Quick cleanup"""
        # Clean skills
        if data.get("professionalSkills", {}).get("skills"):
            data["professionalSkills"]["skills"] = [
                s for s in data["professionalSkills"]["skills"] if s and s.strip()
            ]

        # Ensure tags
        if not data.get("tags"):
            data["tags"] = ["Professional"]

        return data

    def _empty_result(self) -> Dict[str, Any]:
        """Empty result template"""
        return ResumeData().model_dump()

    def _calculate_cost(self) -> float:
        """Calculate cost"""
        input_cost = (self.input_tokens / 1000) * self.INPUT_PRICE_PER_1K
        output_cost = (self.output_tokens / 1000) * self.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost
