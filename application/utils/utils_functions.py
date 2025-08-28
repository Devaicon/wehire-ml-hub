import fitz  # PyMuPDF

def is_pdf_text_based(file_path, min_words=20):
    doc = fitz.open(file_path)
    total_words = 0
    
    for page in doc:
        text = page.get_text()
        words = text.strip().split()
        total_words += len(words)
        
        if total_words >= min_words:
            return True  # Enough text found — likely text-based

    return False  # Too little text — likely image-based



def save_text_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)
