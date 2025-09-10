import requests
import json

# Konfiguration für den Zugriff auf Trello
API_KEY = "593c8bb8870cabd552a0fa5dfdee8134"
TOKEN = "ATTAe454a07adf7b439855d8e029d60c2ab86f3ca5780cb4883c8226071bb27e7d2e2044EDF9"
BOARD_ID = "U7scKrGd"

# API Request: Tickets werden vom Board aufgerufen mit bestimmten relevanten Feldern
url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
params = {
    "key": API_KEY,
    "token": TOKEN,
    "fields": "id,name,desc"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    cards = response.json()

    # Liste mit relevanten Infos bauen
    tickets = []
    for card in cards:
        tickets.append({
            "id": card["id"],
            "name": card["name"],
            "description": card["desc"]
        })

    # In JSON speichern
    with open("trello_tickets.json", "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=4)

    print(f"✅ {len(tickets)} Tickets erfolgreich in trello_tickets.json gespeichert.")
else:
    print("❌ Fehler beim Abrufen der Daten:", response.status_code, response.text)
