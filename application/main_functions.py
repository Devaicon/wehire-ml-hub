import os
from utils.utils_functions import is_pdf_text_based
from ocr_module.pymupdf_txt import extract_text_from_pdf
from ocr_module.pytesseract_txt import get_text_pytesseract


results_dir = "results"
os.makedirs(results_dir, exist_ok=True)


def get_resume_text(pdf_path):
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]

    result = is_pdf_text_based(pdf_path)

    if result:
        print("Pdf contains digital text (at least 20 words)")
        pdf_text = extract_text_from_pdf(pdf_path)

    else:
        print("PDF likely contains scanned images or very little text.")

        pdf_text = get_text_pytesseract(pdf_path)

    # file_path = f"{results_dir}/cvs_txt/{file_name}.txt"
    # save_text_to_file(pdf_text, file_path)

    os.remove(pdf_path)

    return pdf_text
