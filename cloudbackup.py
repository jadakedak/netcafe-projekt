from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "mysupersecretkey"
CORS(app)

BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

def create_tables(cur):
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, userid TEXT, admin BOOLEAN,
            fornavn TEXT, efternavn TEXT, email TEXT,
            brugernavn TEXT, adgangskode TEXT, credits INTEGER
        );
        CREATE TABLE IF NOT EXISTS menuitems (
            id INTEGER PRIMARY KEY, item_id TEXT, navn TEXT,
            beskrivelse TEXT, billede_sti TEXT, pris REAL
        );
        CREATE TABLE IF NOT EXISTS computers (
            id INTEGER PRIMARY KEY, pcid TEXT, pcname TEXT,
            user TEXT, connection_date TEXT, last_seen TEXT
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY, transaction_id TEXT, user_id TEXT,
            item TEXT, amount INTEGER, total INTEGER, purchased_at TEXT
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY, userid TEXT, pc_id INTEGER,
            booking_start TEXT, booking_end TEXT, creation_date TEXT
        );
    """)

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data received"}), 400

    db_path = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        create_tables(cur)

        for id, u in data.get("users", {}).items():
            cur.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?)",
                (int(id), u["userid"], u["admin"], u["fornavn"], u["efternavn"],
                 u["email"], u["brugernavn"], u["adgangskode"], u["credits"]))

        for id, m in data.get("menuitems", {}).items():
            cur.execute("INSERT OR REPLACE INTO menuitems VALUES (?,?,?,?,?,?)",
                (int(id), m["itemid"], m["navn"], m["beskrivelse"], m["billede_sti"], m["pris"]))

        for id, c in data.get("computers", {}).items():
            cur.execute("INSERT OR REPLACE INTO computers VALUES (?,?,?,?,?,?)",
                (int(id), c["pcid"], c["pcname"], c["user"], c["connection_date"], c["last_seen"]))

        for id, t in data.get("transactions", {}).items():
            cur.execute("INSERT OR REPLACE INTO transactions VALUES (?,?,?,?,?,?,?)",
                (int(id), t["transaction_id"], t["user_id"], t["item"],
                 t["amount"], t["total"], t["purchased_at"]))

        for id, b in data.get("bookings", {}).items():
            cur.execute("INSERT OR REPLACE INTO bookings VALUES (?,?,?,?,?,?)",
                (int(id), b["userid"], b["pc_id"],
                 b["booking_start"], b["booking_end"], b["creation_date"]))

        conn.commit()
        conn.close()
        print(f"Backup saved to {db_path}")
        return jsonify({"success": True}), 200

    except Exception as e:
        if conn:
            conn.close()
        os.remove(db_path)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)