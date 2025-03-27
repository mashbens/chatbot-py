from flask import Flask, request, jsonify
import requests
import logging
from PyPDF2 import PdfReader

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

PDF_PATH = "/home/bens/project/mygit/chatbot-py/docs/PPM.pdf"
OLLAMA_URL = "http://10.60.2.15:31130/api/generate"

# Ekstrak teks dari PDF berdasarkan modul
def extract_text_by_module(pdf_path, module_name):
    reader = PdfReader(pdf_path)
    
    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text and module_name in page_text:
            logging.info(f"Modul '{module_name}' ditemukan di halaman {page_number + 1}")
            return page_text  # Langsung return saat modul ditemukan
    
    logging.warning(f"Modul '{module_name}' tidak ditemukan dalam dokumen.")
    return None

# Query Ollama
def query_ollama(prompt):
    cleaned_string = prompt.replace('\n', '')
    payload = {"model": "gemma3:4b", "prompt": cleaned_string, "stream": False}
    print("payload>>>",payload)
    with requests.Session() as session:
        try:
            response = session.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            response_data = response.json()
            # return response.json()
            filtered_data = {key: value for key, value in response_data.items() if key != "context"}
            return filtered_data
        
        except requests.RequestException as e:
            logging.error(f"Error querying Ollama: {e}")
            return {"error": str(e)}

@app.route("/ask", methods=["POST"])
def ask():

    data = request.json
    user_question = data.get("question")
    module_name = data.get("module")
    
    if not user_question or not module_name:
        return jsonify({"error": "Pertanyaan dan modul harus disediakan"}), 400

    pdf_text = extract_text_by_module(PDF_PATH, module_name)
    if not pdf_text:
        return jsonify({"error": f"Modul {module_name} tidak ditemukan"}), 404

    combined_prompt = f"""
    Berikut adalah konten dari {module_name}:
    {pdf_text}
    
    Jawab pertanyaan ini berdasarkan konten di atas

    Pertanyaan: {user_question}
    """
    
    response = query_ollama(combined_prompt)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
