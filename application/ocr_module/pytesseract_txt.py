from pdf2image import convert_from_path
import pytesseract
from pathlib import Path
import os

def get_text_pytesseract(pdf_path: str) -> None:

    pdf_path = Path(pdf_path)

    output_txt_path = pdf_path.with_suffix(".txt")

    images = convert_from_path(pdf_path)
    full_text = ""

    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, config="--psm 6")
        full_text += f"\n\n--- Page {i+1} ---\n{text}"

    # with open(output_txt_path, "w", encoding="utf-8") as f:
    #     f.write(full_text)

    
    return full_text
