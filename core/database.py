"""设计方案的 SQLite 存储（多用户版）"""
import sqlite3
import os
import json

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_PATH = os.path.join(DB_DIR, 'designs.db')


def _connect():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # 用户表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # 方案表（加 user_id）
    conn.execute("""
        CREATE TABLE IF NOT EXISTS designs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            input_params TEXT NOT NULL,
            result_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    return conn


def init_db():
    _connect().close()


# ---------- 方案（带 user_id）----------

def save_design(user_id, name, input_params, result):
    conn = _connect()
    cursor = conn.execute(
        "INSERT INTO designs (user_id, name, input_params, result_data) VALUES (?,?,?,?)",
        (user_id, name,
         json.dumps(input_params, ensure_ascii=False),
         json.dumps(result, ensure_ascii=False))
    )
    conn.commit()
    did = cursor.lastrowid
    conn.close()
    return did


def list_designs(user_id):
    """只列出当前用户的方案"""
    conn = _connect()
    rows = conn.execute(
        "SELECT id, name, created_at FROM designs WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def get_design(design_id, user_id):
    """只能取自己的方案"""
    conn = _connect()
    row = conn.execute(
        "SELECT id, name, input_params, result_data, created_at "
        "FROM designs WHERE id=? AND user_id=?",
        (design_id, user_id)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "name": row[1],
        "input_params": json.loads(row[2]),
        "result_data": json.loads(row[3]),
        "created_at": row[4],
    }


def delete_design(design_id, user_id):
    conn = _connect()
    conn.execute(
        "DELETE FROM designs WHERE id=? AND user_id=?",
        (design_id, user_id)
    )
    conn.commit()
    conn.close()


def clear_all(user_id):
    """只清空自己的方案"""
    conn = _connect()
    conn.execute("DELETE FROM designs WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()