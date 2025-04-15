from flask import Flask, request, jsonify
from ollama_client import query_ollama, extract_keywords_from_question
from pdf_reader import extract_text_multiple_keywords
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

PDF_PATH = "/home/bens/project/mygit/chatbot-py/ollama/docs/PPM.pdf"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question")

    if not user_question or len(user_question.split()) < 3:
        return jsonify({"error": "Pertanyaan harus lebih dari 3 kata"}), 400

    keywords = extract_keywords_from_question(user_question)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)