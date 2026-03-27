# -*- coding: utf-8 -*-
import os
import lancedb
import anthropic
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def search_modules(query, n=3):
    db = lancedb.connect("./lancedb_store")
    table = db.open_table("module")
    vector = model.encode(query).tolist()
    return table.search(vector).limit(n).to_list()

def search_documents(query, n=3):
    db = lancedb.connect("./lancedb_store")
    table = db.open_table("dokumente")
    vector = model.encode(query).tolist()
    return table.search(vector).limit(n).to_list()

def build_context(query):
    modules = search_modules(query)
    docs = search_documents(query)
    context = "RELEVANTE MODULE:\n\n"
    for r in modules:
        context += f"# {r['name']}\n{r['text']}\n\n"
    context += "---\nRELEVANTE DOKUMENTE:\n\n"
    for r in docs:
        context += f"# {r['name']} (Chunk {r['chunk']}) [{r['tags']}]\n{r['text']}\n\n"
    return context

def ask(frage):
    print(f"\nFrage: {frage}")
    print("Suche relevante Inhalte...")
    context = build_context(frage)
    print("Claude wird befragt...")
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": f"""Du bist ein Beratungsassistent fuer KI-Compliance und Sicherheit.
Nutze ausschliesslich die folgenden Inhalte als Grundlage fuer deine Antwort.
Antworte praezise, substanziell und ohne Beraterfloskeln.

{context}

Frage: {frage}"""
            }
        ]
    )
    return message.content[0].text

if __name__ == "__main__":
    antwort = ask("Welche Massnahmen braucht ein mittelstaendisches Unternehmen fuer KI-Compliance?")
    print("\n" + "="*60)
    print("ANTWORT:")
    print("="*60)
    print(antwort)
