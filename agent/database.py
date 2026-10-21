import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "mgi_session.db")


def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS session
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY,
                     messages
                     TEXT,
                     awaiting_approval
                     INTEGER,
                     ticket_status
                     TEXT,
                     ticket_data
                     TEXT
                 )''')
    conn.commit()
    conn.close()


def load_session():
    """读取上次的状态"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT messages, awaiting_approval, ticket_status, ticket_data FROM session WHERE id = 1")
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "messages": json.loads(row[0]) if row[0] else [],
            "awaiting_approval": bool(row[1]),
            "ticket_status": row[2],
            "ticket_data": json.loads(row[3]) if row[3] else {}
        }
    return None


def save_session(messages, awaiting_approval, ticket_status, ticket_data):
    """保存当前状态（防刷新丢失）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO session (id, messages, awaiting_approval, ticket_status, ticket_data)
                 VALUES (1, ?, ?, ?, ?)''',
              (json.dumps(messages, ensure_ascii=False),
               int(awaiting_approval),
               ticket_status,
               json.dumps(ticket_data, ensure_ascii=False)))
    conn.commit()
    conn.close()


def clear_session():
    """清空当前会话，用于重新开始"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM session WHERE id = 1")
    conn.commit()
    conn.close()