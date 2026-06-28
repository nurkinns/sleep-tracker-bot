from zoneinfo import ZoneInfo
import sqlite3
import os
from datetime import datetime

if not os.path.exists("/data"):
    os.makedirs("/data")

connect = sqlite3.connect("/data/sleep_tracker.db")
cursor = connect.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS sleep_records (
    tg_user_id INTEGER,
    tg_sleep_start TEXT,
    tg_sleep_end TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    tg_user_id INTEGER UNIQUE,
    language TEXT DEFAULT 'EN'
)
""")
connect.commit()
connect.close()

def add_user(user_id):
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO sleep_records (tg_user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def save_sleep_start(user_id):
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sleep_records (tg_user_id, tg_sleep_start) VALUES (?, ?)", 
        (user_id, time_string)
    )
    conn.commit()
    conn.close()

def set_user_language(user_id, lang):
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (tg_user_id, language) 
        VALUES (?, ?)
        ON CONFLICT(tg_user_id) DO UPDATE SET language = excluded.language
    """, (user_id, lang))
    conn.commit()
    conn.close()

def save_sleep_end(user_id):
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE sleep_records 
        SET tg_sleep_end = ? 
        WHERE tg_user_id = ? AND tg_sleep_end IS NULL
    """, (time_string, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT tg_sleep_start, tg_sleep_end 
        FROM sleep_records 
        WHERE tg_user_id = ? 
          AND tg_sleep_start IS NOT NULL 
          AND tg_sleep_end IS NOT NULL
    """, (user_id,))
    
    records = cur.fetchall()
    conn.close()
    
    if not records:
        return []
        
    stats_list = []
    for start_str, end_str in records:
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        
        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        date_display = start_time.strftime("%Y.%m.%d")
        start_display = start_time.strftime("%H:%M")
        end_display = end_time.strftime("%H:%M")
        
        stats_list.append((date_display, start_display, end_display, hours, minutes))
        
    return stats_list

def get_user_language(user_id):
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute("SELECT language FROM users WHERE tg_user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return "EN"

def delete_user_stats(user_id):
    conn = sqlite3.connect("/data/sleep_tracker.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM sleep_records WHERE tg_user_id = ?", (user_id,))
    conn.commit()
    conn.close()

#made by "nurkinns" on GitHub with using AI.