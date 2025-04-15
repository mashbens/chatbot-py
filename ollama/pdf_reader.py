from PyPDF2 import PdfReader
import logging
import re
from mongo_client import pdf_cache_collection  # koneksi MongoDB dari mongo_client.py

def extract_text_multiple_keywords(pdf_path, keywords, max_pages=15):
    keyword_key = keywords.strip().lower()

    # Cek cache MongoDB
    cached_data = pdf_cache_collection.find_one({"keyword": keyword_key})
    if cached_data:
        logging.info(f"[MongoCache] Data ditemukan di cache untuk keyword: '{keyword_key}'")
        return cached_data["content"]  # Gunakan data dari MongoDB jika sudah ada

    # Kalau tidak ditemukan di cache, cari di PDF
    reader = PdfReader(pdf_path)
    keyword_list = keyword_key.split()  # pecah keyword menjadi list
    found_texts = []
    pages_found = set()

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
            break  # Hentikan pencarian jika sudah cukup halaman ditemukan

    if found_texts:
        combined_text = "\n\n".join(found_texts)

        # Simpan hasil ke MongoDB untuk keyword yang dicari
        try:
            pdf_cache_collection.insert_one({
                "keyword": keyword_key,
                "content": combined_text
            })
            logging.info(f"[MongoCache] Data cache disimpan untuk keyword: '{keyword_key}'")
        except Exception as e:
            logging.error(f"[MongoCache] Gagal menyimpan ke MongoDB: {e}")

        return combined_text

    logging.warning(f"Tidak ada keyword yang ditemukan dalam dokumen.")
    return None