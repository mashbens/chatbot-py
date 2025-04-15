import requests
import logging
from utils import clean_prompt, truncate_prompt  # Import truncate_prompt

OLLAMA_URL = "http://10.60.2.15:31130/api/generate"
MODEL_NAME = "gemma3:4b"

def query_ollama(prompt):
    # Truncate prompt jika terlalu panjang
    cleaned_prompt = truncate_prompt(clean_prompt(prompt))
    
    payload = {
        "model": MODEL_NAME,
        "prompt": cleaned_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return {k: v for k, v in response.json().items() if k != "context"}
    except requests.RequestException as e:
        logging.error(f"Error querying Ollama: {e}")
        return {"error": str(e)}

def extract_keywords_from_question(question):
    prompt = f"""
    Berikan saya kata inti dari pertanyaan ini. kata kunci ini untuk saya cari di pdf saya sebagai keyword. jawab hanya kata kuncinya saja tanpa koma!!
    Pertanyaan: {question}
    """
    result = query_ollama(prompt)
    return result.get("response", "")
import requests
import logging
from utils import clean_prompt, truncate_prompt  # Import truncate_prompt

OLLAMA_URL = "http://10.60.2.15:31130/api/generate"
MODEL_NAME = "gemma3:4b"

def query_ollama(prompt):
    # Truncate prompt jika terlalu panjang
    cleaned_prompt = truncate_prompt(clean_prompt(prompt))
    
    payload = {
        "model": MODEL_NAME,
        "prompt": cleaned_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return {k: v for k, v in response.json().items() if k != "context"}
    except requests.RequestException as e:
        logging.error(f"Error querying Ollama: {e}")
        return {"error": str(e)}

