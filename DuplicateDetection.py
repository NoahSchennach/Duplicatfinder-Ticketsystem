import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util

# Modell laden (einmalig beim Start)
model = SentenceTransformer("all-MiniLM-L6-v2")

# FastAPI-App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später besser auf die Frontend-Domain eingrenzen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/trelloTickets")

def detect_duplicates():
    # JSON-Datei einlesen (später evtl. direkt Trello-API)
    with open("trello_tickets.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Texte vorbereiten
    sentences = [
        (
            item["id"], 
            item.get("name", "").strip() or f"[NO-TITLE-{item['id']}]",
            item.get("desc", "").strip() or f"[EMPTY-{item['id']}]"
        )
        for item in data
    ]
    
    ids, titles, texts = zip(*sentences)

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
                "title1" : titles[i],
                "title2" : titles[j],
                "desc1" : titles[i],
                "desc2" : titles[j],
                "similarity": round(score * 100, 2)  # in %
            }
            duplicates.append(duplicate)
                
    return duplicates
    # API-Response zurückgeben
    # return JSONResponse(content=duplicates)

# Testausgabe auf der Konsole
if __name__ == "__main__":
    test_duplicates = detect_duplicates()  # Funktion aufrufen
    print("\nGefundene mögliche Duplikate:")
    for d in test_duplicates:
        print(f"{d['title1']} ↔ {d['title2']} | Ähnlichkeit: {d['similarity']}%")