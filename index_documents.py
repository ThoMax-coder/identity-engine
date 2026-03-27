# -*- coding: utf-8 -*-
import os
import lancedb
import pymupdf
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

DOKUMENTE_PFAD = os.getenv("DOKUMENTE_PFAD")
PDF_PFAD = os.path.join(DOKUMENTE_PFAD, "pdf")

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

TAG_REGELN = {
    "EU AI Act": ["ai act", "eu ai", "hochrisiko", "risikoklassifizierung", "konformität"],
    "Haftung": ["haftung", "haftungsrisiko", "haftungsentlastung", "verantwortung"],
    "Compliance": ["compliance", "nachweispflicht", "audit", "prüfung", "zertifizierung"],
    "Sicherheit": ["sicherheit", "cybersicherheit", "nis-2", "kritis", "informationssicherheit"],
    "Organisation": ["organisation", "governance", "strukturell", "maßnahmen", "tom"],
    "Schulung": ["schulung", "qualifizierung", "kompetenz", "zertifikat", "weiterbildung"],
    "Risiko": ["risiko", "risikoanalyse", "risikobewertung", "gefährdung", "bedrohung"],
}

def auto_tag(text):
    text_lower = text.lower()
    tags = []
    for tag, begriffe in TAG_REGELN.items():
        if any(begriff in text_lower for begriff in begriffe):
            tags.append(tag)
    return tags if tags else ["Allgemein"]

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
                tags = auto_tag(chunk)
                vector = model.encode(chunk).tolist()
                data.append({
                    "name": filename,
                    "chunk": i,
                    "text": chunk,
                    "tags": ", ".join(tags),
                    "vector": vector
                })
                print(f"    Chunk {i}: {tags}")
    print(f"\n{len(data)} Chunks indexiert.")
    db = lancedb.connect("./lancedb_store")
    try:
        db.drop_table("dokumente")
    except:
        pass
    db.create_table("dokumente", data=data)
    print("Indexierung abgeschlossen.")

def search(query, tag_filter=None, n=3):
    db = lancedb.connect("./lancedb_store")
    table = db.open_table("dokumente")
    query_vector = model.encode(query).tolist()
    results = table.search(query_vector).limit(n).to_list()
    if tag_filter:
        results = [r for r in results if tag_filter in r["tags"]]
    return results

if __name__ == "__main__":
    index_pdfs()

    print("\nTest 1 — Semantische Suche:")
    results = search("Welche Massnahmen braucht ein Unternehmen fuer KI-Compliance?")
    for r in results:
        print(f"\n  [{r['tags']}] {r['name']} (Chunk {r['chunk']})")
        print(f"  {r['text'][:200]}")

    print("\nTest 2 — Suche mit Tag-Filter 'Haftung':")
    results = search("Wer haftet fuer KI-Entscheidungen?", tag_filter="Haftung")
    for r in results:
        print(f"\n  [{r['tags']}] {r['name']} (Chunk {r['chunk']})")
        print(f"  {r['text'][:200]}")
