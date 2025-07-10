import sqlite3
from datetime import datetime
import pandas as pd


DB_PATH = "predictions.db"

import sqlite3


def init_db():
    conn = sqlite3.connect("predictions.db")  # ✅ Consistent DB name
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            sequence TEXT,
            known_mutations TEXT,
            rising_mutations TEXT,
            predictions TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()



import sqlite3
import json

def save_prediction(username, sequence, known, rising, preds_dict):
    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions (username, sequence, known_mutations, rising_mutations, predictions)
    VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        sequence,
        ",".join(known),
        ",".join(rising),
        json.dumps(preds_dict)  # Serialize predictions as JSON
    ))

    conn.commit()
    conn.close()


def get_user_history(username):
    conn = sqlite3.connect("predictions.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, sequence, known_mutations, rising_mutations, predictions
        FROM predictions
        WHERE username = ?
    """, (username,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        return pd.DataFrame(rows, columns=["id", "sequence", "known_mutations", "rising_mutations", "predictions"])
    else:
        return pd.DataFrame()


def delete_prediction(prediction_id):
    conn = sqlite3.connect("data/predictions.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    conn.commit()
    conn.close()
