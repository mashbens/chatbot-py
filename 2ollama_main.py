from flask import Flask, request, jsonify
import requests
import logging
from PyPDF2 import PdfReader

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

PDF_PATH_BUMN = "/home/bens/project/mygit/chatbot-py/docs/BUMN.pdf"
PDF_PATH_BRI_PRODUK = "/home/bens/project/mygit/chatbot-py/docs/BRI_PRODUK.pdf"
OLLAMA_URL = "http://localhost:11435/api/generate"

# Ekstrak teks dari PDF berdasarkan modul
def extract_text_by_module(pdf_path, module_name, keyword):
    reader = PdfReader(pdf_path)
    
    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text and keyword in page_text:
            logging.info(f"Modul '{keyword}' ditemukan di halaman {page_number + 1}")
            return page_text  # Langsung return saat modul ditemukan
    
    logging.warning(f"Modul '{module_name}' atau kata kunci '{keyword}' tidak ditemukan dalam dokumen.")
    return None

# Query Ollama
def query_ollama(prompt):
    payload = {"model": "llama3.2:3b", "prompt": prompt.replace("\n", "\\n"), "stream": False}
    
    with requests.Session() as session:
        try:
            response = session.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error querying Ollama: {e}")
            return {"error": str(e)}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question")
    module_name = data.get("module")
    keyword = data.get("module")


    if not user_question or not module_name:
        return jsonify({"error": "Pertanyaan dan modul harus disediakan"}), 400


    if module_name == "BRI_PRODUK":
        pdf_text = extract_text_by_module(PDF_PATH_BRI_PRODUK, module_name, keyword)
    elif module_name == "BUMN":
        pdf_text = extract_text_by_module(PDF_PATH_BUMN, module_name, keyword)

    if not pdf_text:
        return jsonify({"error": f"Modul {module_name} or kata kunci {keyword} tidak ditemukan"}), 404

    combined_prompt = f"""
    Berikut adalah konten dari {module_name}:
    {pdf_text}
    
    Jawab hanya berdasarkan modul tersebut, Jika tidak ada jawaban di modul tersebut, jawab "Maaf ya Kakak, aku hanya bisa menjawab seputar modul BUMN dan BRI PRODUK".
    Pertanyaan: {user_question}
    """
    print("combined_prompt>>>",combined_prompt)
    response = query_ollama(combined_prompt)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
