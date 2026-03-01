import sqlite3
import hashlib
import os

class AuthManager:
    def __init__(self, db_path="toyota_diagnostic_pro/database/users.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email=None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = self._hash_password(password)
            cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                           (username, password_hash, email))
            conn.commit()
            conn.close()
            return True, "ลงทะเบียนสำเร็จ"
        except sqlite3.IntegrityError:
            return False, "ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว"
        except Exception as e:
            return False, str(e)

    def login_user(self, username, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        password_hash = self._hash_password(password)
        cursor.execute('SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
                       (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        if user:
            return True, {"id": user[0], "username": user[1]}
        return False, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"

    def update_password(self, username, new_password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        new_hash = self._hash_password(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (new_hash, username))
        conn.commit()
        conn.close()
        return True
