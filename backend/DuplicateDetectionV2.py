# backend/DuplicateDetection.py
import json, os
from pathlib import Path
import mysql.connector
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

# ----------------------- Konfiguration -----------------------
load_dotenv()
SOURCE = os.getenv("SOURCE", "json").lower()  # "json" oder "db"
JSON_CANDIDATES = [Path("data/trello_tickets.json"), Path("trello_tickets.json")]

# SBERT-Modell in das Skript laden
model = SentenceTransformer("all-MiniLM-L6-v2")

# ----------------------- FastAPI-App -------------------------
app = FastAPI(title="Duplicate Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------- Datenquellen ------------------------
def load_data():
    return load_from_db() if SOURCE == "db" else load_from_json()

# ----------------------- JSON-Datenquelle --------------------
def load_from_json():
    for p in JSON_CANDIDATES:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                return json.load(f)
    return []  # kein File gefunden

# ----------------------- Datenbank-Datenquelle --------------
def load_from_db():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "simple_tickets"),
        port=int(os.getenv("DB_PORT", "3306")),
    )
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, title AS name, description AS `desc` FROM ticket ORDER BY id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


# ----------------------- Duplicate Detection -----------------
@app.get("/api/Duplicates")

# Methode zur Duplikaterkennung
def detect_duplicates():
    data = load_data()
    # Vorbereitung der Ticketdaten
    tickets = [
        (
            item["id"],
            (item.get("name") or "").strip() or f"[NO-TITLE-{item['id']}]",
            (item.get("desc") or "").strip() or f"[EMPTY-{item['id']}]",
        )
        for item in data
    ]

    if not tickets:
        return []

    ids, titles, descs = zip(*tickets)
    texts = [f"{t}. {d}" for t, d in zip(titles, descs)]
    if len(texts) < 2:
        return []

    # Embeddings erzeugen
    embeddings = model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)
    
    # Kosinus-Ähnlichkeiten zwischen den Tickets berechnen
    similarities = util.cos_sim(embeddings, embeddings)

    # Duplikate basierend auf einem Ähnlichkeitsschwellenwert identifizieren und herausfiltern
    threshold = 0.40
    duplicates = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            score = similarities[i][j].item()
            if score >= threshold:
                duplicates.append({
                    "id1": ids[i], "id2": ids[j],
                    "title1": titles[i], "title2": titles[j],
                    "desc1": descs[i], "desc2": descs[j],
                    "similarity": round(score * 100, 2)
                })
    return duplicates

# ----------------------- Testausgabe im Terminal ----------------------------
if __name__ == "__main__":
    print("Testlauf… Quelle:", SOURCE)
    for d in detect_duplicates():
        print(f"{d['title1']} ↔ {d['title2']} | Ähnlichkeit: {d['similarity']}%")