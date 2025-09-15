import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer, util

# Modell laden (einmalig beim Start)
model = SentenceTransformer("all-MiniLM-L6-v2")

# FastAPI-App
app = FastAPI()

@app.get("/api/trelloTickets")

def detect_duplicates():
    # JSON-Datei einlesen (später evtl. direkt Trello-API)
    with open("trello_tickets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Texte vorbereiten
    sentences = [
        (item["id"], item.get("desc", "").strip() or f"[EMPTY-{item['id']}]")
        for item in data
    ]
    
    ids, texts = zip(*sentences)

    # Embeddings berechnen
    embeddings = model.encode(texts, convert_to_tensor=True, normalize_embeddings=False)

    # Paarweise Ähnlichkeiten berechnen
    cosine_scores = util.cos_sim(embeddings, embeddings)

    # Ergebnisse sammeln
    threshold = 0.7
    duplicates = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            score = cosine_scores[i][j].item()
            if score >= threshold:
                duplicate = {
                "id1": ids[i],
                "id2": ids[j],
                "similarity": round(score * 100, 2)  # in %
            }
            duplicates.append(duplicate)
                
    return duplicates
    # API-Response zurückgeben
    # return JSONResponse(content=duplicates)

# Am Ende deiner Datei
if __name__ == "__main__":
    test_duplicates = detect_duplicates()  # Funktion aufrufen
    print("\nGefundene mögliche Duplikate:")
    for d in test_duplicates:
        print(f"{d['id1']} ↔ {d['id2']} | Ähnlichkeit: {d['similarity']}%")
