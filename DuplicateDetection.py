import json
from sentence_transformers import SentenceTransformer, util

# Modell laden
model = SentenceTransformer("all-MiniLM-L6-v2")

# JSON-Datei einlesen
with open("trello_tickets.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Textquelle für Embeddings bestimmen (z.B. Kombination aus name + description)
sentences = [
    (item["id"], (item.get("desc", "")).strip())
    for item in data
]

ids, texts = zip(*sentences)

# Embeddings berechnen
embeddings = model.encode(texts, convert_to_tensor=True)

# Paarweise Ähnlichkeiten berechnen
cosine_scores = util.cos_sim(embeddings, embeddings)

# Ergebnisse ausgeben (z.B. nur Duplikate über einem Schwellenwert)
threshold = 0.7  # kann angepasst werden
for i in range(len(ids)):
    for j in range(i + 1, len(ids)):
        score = cosine_scores[i][j].item()
        if score >= threshold:
            print(f"⚠️ Möglicher Duplicate gefunden:")
            print(f"  {ids[i]} ↔ {ids[j]} | Ähnlichkeit: {score:.3f}")
