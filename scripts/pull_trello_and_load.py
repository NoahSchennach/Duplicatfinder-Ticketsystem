# scripts/pull_trello_and_load.py
import os, json, requests
from dotenv import load_dotenv
import mysql.connector
from typing import List, Dict

load_dotenv()

# ---------------- Trello Config aus .env ----------------
API_KEY  = os.getenv("TRELLO_API_KEY")
TOKEN    = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

JSON_OUT = "data/trello_tickets.json"

def fetch_trello_cards() -> List[Dict]:
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    params = {"key": API_KEY, "token": TOKEN, "fields": "id,name,desc"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()

def save_to_json(tickets: List[Dict]) -> None:
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=4)
    print(f"📄 JSON gespeichert: {JSON_OUT} ({len(tickets)} Einträge)")

def save_to_mysql(tickets: List[Dict]) -> None:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "simple_tickets"),
        port=int(os.getenv("DB_PORT", "3306")),
    )
    cur = conn.cursor()
    # einfache Synchronisation: leeren + neu befüllen
    cur.execute("TRUNCATE TABLE ticket")
    sql = "INSERT INTO ticket (title, description, ext_id) VALUES (%s, %s, %s)"
    rows = [(t.get("name") or "(ohne Titel)", t.get("desc"), t.get("id")) for t in tickets]
    cur.executemany(sql, rows)
    conn.commit()
    cur.close()
    conn.close()
    print(f"🗄️  DB befüllt: {len(rows)} Einträge in simple_tickets.ticket")

if __name__ == "__main__":
    print("Hole Karten von Trello …")
    cards = fetch_trello_cards()
    print(f"Karten geladen: {len(cards)}")
    save_to_json(cards)
    if os.getenv("LOAD_TO_DB", "true").lower() == "true":
        save_to_mysql(cards)