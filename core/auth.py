"""用户认证：注册、登录、密码哈希（SQLite 版）"""
import hashlib
import secrets
from core.database import _connect


def _hash_password(password: str, salt: str = None) -> tuple:
    """PBKDF2 密码哈希"""
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000,
    )
    return pwd_hash.hex(), salt


def register(username: str, password: str) -> tuple:
    """注册新用户。返回 (成功?, 消息)"""
    username = username.strip()
    if not username:
        return False, "用户名不能为空"
    if len(username) < 2:
        return False, "用户名至少 2 个字符"
    if len(password) < 4:
        return False, "密码至少 4 个字符"

    conn = _connect()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        conn.close()
        return False, "用户名已存在"

    pwd_hash, salt = _hash_password(password)
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?,?,?)",
            (username, pwd_hash, salt),
        )
        conn.commit()
        conn.close()
        return True, "注册成功"
    except Exception as e:
        conn.close()
        return False, f"注册失败：{e}"


def login(username: str, password: str) -> tuple:
    """登录验证。返回 (成功?, user_id 或 错误消息, username)"""
    username = username.strip()
    if not username or not password:
        return False, "用户名和密码不能为空", None

    conn = _connect()
    row = conn.execute(
        "SELECT id, password_hash, salt FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if not row:
        return False, "用户名不存在", None

    user_id, stored_hash, salt = row
    input_hash, _ = _hash_password(password, salt)

    if input_hash == stored_hash:
        return True, user_id, username
    else:
        return False, "密码错误", None