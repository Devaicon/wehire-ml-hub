import fitz  # PyMuPDF
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path) -> None:
    """
    Extracts text from a PDF using PyMuPDF and saves it as a .txt file in the same directory.
    """

    pdf_path = Path(pdf_path)

    # output_txt_path = pdf_path.with_suffix(".txt")

    with fitz.open(pdf_path) as doc:
        full_text = ""
        for page in doc:
            full_text += page.get_text()

    # with open(output_txt_path, "w", encoding="utf-8") as f:
    #     f.write(full_text)

    # print(f"Saved: {output_txt_path}")
    print("Extracted text from PDF")

    return full_text
