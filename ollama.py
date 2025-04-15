from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import requests
import logging
import re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

PDF_PATH = "/home/bens/project/mygit/chatbot-py/docs/PPM.pdf"
OLLAMA_URL = "http://10.60.2.15:31130/api/generate"

# Ekstrak teks dari PDF berdasarkan modul
# def extract_text_by_module(pdf_path, keywords):
    # reader = PdfReader(pdf_path)
    # module_pattern = re.compile(rf"\b{re.escape(keywords)}\b", re.IGNORECASE)
    
    # for page_number, page in enumerate(reader.pages):
    #     page_text = page.extract_text()
    #     if page_text and module_pattern.search(page_text):
    #         logging.info(f"Modul '{keywords}' ditemukan di halaman {page_number + 1}")
    #         return page_text  # Langsung return saat modul ditemukan
    
    # logging.warning(f"Modul '{keywords}' tidak ditemukan dalam dokumen.")
    # return None

def extract_text_multiple_keywords(pdf_path, keywords, max_pages=10):
    reader = PdfReader(pdf_path)
    keyword_list = keywords.split()  # Pisahkan kata kunci menjadi list
    found_texts = []  # Simpan hasil pencarian
    pages_found = set()  # Simpan halaman yang sudah ditemukan agar tidak duplikat

    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if not page_text:
            continue  # Lewati halaman kosong

        for keyword in keyword_list:
            pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            if pattern.search(page_text):
                if page_number not in pages_found:
                    logging.info(f"Keyword '{keyword}' ditemukan di halaman {page_number + 1}")
                    found_texts.append(f"--- Halaman {page_number + 1} ---\n{page_text}")
                    pages_found.add(page_number)

        if len(pages_found) >= max_pages:
            break  # Hentikan jika sudah cukup halaman

    if found_texts:
        return "\n\n".join(found_texts)

    logging.warning(f"Tidak ada keyword yang ditemukan dalam dokumen.")
    return None

# Query Ollama
def query_ollama(prompt):
    cleaned_string = prompt.replace('\n', '')
    payload = {"model": "gemma3:4b", "prompt": cleaned_string, "stream": False}
    print("payload>>>", payload)
    with requests.Session() as session:
        try:
            response = session.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            filtered_data = {key: value for key, value in response_data.items() if key != "context"}
            return filtered_data
        except requests.RequestException as e:
            logging.error(f"Error querying Ollama: {e}")
            return {"error": str(e)}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question")
    print("user_question>>>", user_question, len(user_question))

    words = user_question.split()

    if len(words) < 3:
        return jsonify({"error": "Pertanyaan harus lebih dari 3 kata"}), 400

    combined_prompt = f"""
    Berikan saya kata inti dari pertanyaan ini. kata kunci ini untuk saya cari di pdf saya sebagai keyword. jawab hanya kata kuncinya saja tanpa koma!!
    Pertanyaan: {user_question}
    """

    response = query_ollama1(combined_prompt)
    print("response>>>", response.get("response"))
    keywords = response.get("response")

    pdf_text = extract_text_multiple_keywords(PDF_PATH, keywords)
    if not pdf_text:
        return jsonify({"error": f"Keyword {keywords} tidak ditemukan"}), 404

    combined_prompt = f"""
    Berikut adalah data dari {keywords}:
    {pdf_text}
    
    Jawablah sejelas dan seakurat mungkin berdasarkan data di atas. Jangan gunakan informasi lain selain data tersebut.
    
    Pertanyaan: {user_question}

    """
    
    response = query_ollama(combined_prompt)
    return jsonify(response)

def query_ollama1(prompt):
    cleaned_string = prompt.replace('\n', '')
    payload = {"model": "gemma3:4b", "prompt": cleaned_string, "stream": False}
    print("payload>>>", payload)
    with requests.Session() as session:
        try:
            response = session.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            filtered_data = {key: value for key, value in response_data.items() if key != "context"}
            return filtered_data
        except requests.RequestException as e:
            logging.error(f"Error querying Ollama: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)