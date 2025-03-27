from PyPDF2 import PdfReader
import requests
import logging
import re


def extract_text_by_keywords(pdf_path, keywords):
    reader = PdfReader(pdf_path)
    keyword_list = keywords.split()
    
    matched_texts = []
    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if not page_text:
            continue
        
        found = all(re.search(rf"\b{re.escape(word)}\b", page_text, re.IGNORECASE) for word in keyword_list)
        if found:
            print(f"Semua kata ditemukan di halaman {page_number + 1}")
            matched_texts.append(page_text)
    
    if matched_texts:
        return "\n".join(matched_texts)
    
    logging.warning(f"Kata-kata '{keywords}' tidak ditemukan dalam dokumen.")
    return None


def main():
    print("test serching pdf:")
    keywords= "PPM"

    PDF_PATH = "/home/bens/project/mygit/chatbot-py/docs/PPM.pdf"
    pdf_text = extract_text_by_keywords(PDF_PATH, keywords)
    if not pdf_text:
        print("error Keyword {keywords} tidak ditemukan")

    combined_prompt = f"""
    Berikut adalah konten dari {keywords}:
    {pdf_text}
    """

    cleaned_string = combined_prompt.replace('\n', '')
    print(cleaned_string)
    print("length>>>", len(cleaned_string))

    
if __name__ == "__main__":
    main()