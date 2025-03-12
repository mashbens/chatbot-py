from flask import Flask, request, jsonify
import requests
from PyPDF2 import PdfReader

app = Flask(__name__)

# Path ke PDF yang disimpan di server
PDF_PATH = "/home/bens/project/test/research-chatbot-phi4/data/bumn.pdf"

# Fungsi untuk ekstrak teks dari PDF berdasarkan modul
def extract_text_by_module(pdf_path, module_name):
    reader = PdfReader(pdf_path)
    text = ""
    print(f"Memulai ekstraksi teks dari {pdf_path} untuk modul: {module_name}")
    
    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text and module_name in page_text:  # Cari modul berdasarkan kata kunci
            text += page_text
            print(f"Modul ditemukan di halaman {page_number + 1}: {page_text[:50]}...")  # Menampilkan 50 karakter pertama dari teks yang ditemukan

    if not text:
        print(f"Modul '{module_name}' tidak ditemukan dalam dokumen.")
    else:
        print(f"Ekstraksi selesai. Teks untuk modul '{module_name}' berhasil diekstrak.")

    return text


# Fungsi untuk query Ollama
def query_ollama(prompt):
    print(f"Memulai query ke Ollama dengan prompt:")
    url = "http://localhost:11435/api/generate"
    modifi_string = prompt.replace("\n", "\\n")
    print("modifi_string ------------------->",modifi_string)
    data = {
    "model": "llama3.2:3b",
    "prompt":modifi_string,
    "stream": False
    }

    try:
        response = requests.post(url, json=data)

        # Memeriksa status kode respons
        response.raise_for_status()  # Akan memicu exception untuk status kode 4xx atau 5xx

        # Menampilkan konten respons
        print("Response Content:", response.json())
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Menangani kesalahan HTTP
        return {"error": str(http_err)}
    except Exception as err:
        print(f"An error occurred: {err}")  # Menangani kesalahan lainnya
        return {"error": str(err)}
    # response = request.post(url, json=payload)
    # return response.json()

    # response = requests.post(url, json=payload)

    # # Memeriksa status kode respons
    # response.raise_for_status()  # Akan memicu exception untuk status kode 4xx atau 5xx

    # # Menampilkan konten respons
    # print("Response Content:", response.json())  # Mengonversi respons ke JSON dan mencetaknya
    # return response.json()



# Endpoint untuk menerima pertanyaan
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question")
    module_name = data.get("module")  # Misalnya: "Modul A"

    if not user_question or not module_name:
        return jsonify({"error": "Pertanyaan dan modul harus disediakan"}), 400

    # Ekstrak teks yang relevan dari PDF
    pdf_text = extract_text_by_module(PDF_PATH, module_name)
    if not pdf_text:
        return jsonify({"error": f"Modul {module_name} tidak ditemukan"}), 404

    # Gabungkan teks PDF dengan pertanyaan pengguna
    print("---- start extract text from pdf ----")
    combined_prompt = f"""
    Berikut adalah konten dari {module_name}:
    {pdf_text}

    Pertanyaan: {user_question}
    """

    # Kirim ke Ollama
    response = query_ollama(combined_prompt)
    print("---- start query ollama ----",combined_prompt )
    return jsonify(response)

# Jalankan server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)