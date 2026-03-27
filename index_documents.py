# -*- coding: utf-8 -*-
import os
import lancedb
import pymupdf
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

DOKUMENTE_PFAD = os.getenv("DOKUMENTE_PFAD")
PDF_PFAD = os.path.join(DOKUMENTE_PFAD, "pdf")

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def index_pdfs():
    print("PDFs werden geladen und indexiert...")
    data = []
    for filename in os.listdir(PDF_PFAD):
        if filename.endswith(".pdf"):
            filepath = os.path.join(PDF_PFAD, filename)
            print(f"  Verarbeite: {filename}")
            text = extract_text_from_pdf(filepath)
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                vector = model.encode(chunk).tolist()
                data.append({
                    "name": filename,
                    "chunk": i,
                    "text": chunk,
                    "vector": vector
                })
    print(f"{len(data)} Chunks aus {len(os.listdir(PDF_PFAD))} PDFs erstellt.")
    db = lancedb.connect("./lancedb_store")
    if "dokumente" in db.list_tables():
        db.drop_table("dokumente")
    db.create_table("dokumente", data=data)
    print("Indexierung abgeschlossen.")

def search(query, n=3):
    db = lancedb.connect("./lancedb_store")
    table = db.open_table("dokumente")
    query_vector = model.encode(query).tolist()
    results = table.search(query_vector).limit(n).to_list()
    return results

if __name__ == "__main__":
    index_pdfs()
    print("\nTest-Suche: 'Welche Massnahmen braucht ein Unternehmen fuer KI-Compliance?'")
    results = search("Welche Massnahmen braucht ein Unternehmen fuer KI-Compliance?")
    for r in results:
        print(f"\n--- {r['name']} (Chunk {r['chunk']}) ---")
        print(r["text"][:300])
