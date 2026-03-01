import sqlite3
import os

class VehicleManager:
    def __init__(self, db_path="toyota_diagnostic_pro/database/vehicles.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                vin TEXT UNIQUE,
                make TEXT DEFAULT 'Toyota',
                model TEXT,
                year INTEGER,
                engine_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for diagnostic sessions associated with vehicles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                log_file_path TEXT,
                summary TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_vehicle(self, user_id, vin, model, year, engine_type):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vehicles (user_id, vin, model, year, engine_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, vin, model, year, engine_type))
            conn.commit()
            conn.close()
            return True, "เพิ่มข้อมูลรถสำเร็จ"
        except sqlite3.IntegrityError:
            return False, "เลขตัวถัง (VIN) นี้มีอยู่ในระบบแล้ว"
        except Exception as e:
            return False, str(e)

    def get_user_vehicles(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE user_id = ?', (user_id,))
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        conn.close()
        return results

    def update_vehicle(self, vehicle_id, model, year, engine_type):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE vehicles SET model = ?, year = ?, engine_type = ?
            WHERE id = ?
        ''', (model, year, engine_type, vehicle_id))
        conn.commit()
        conn.close()
        return True

    def delete_vehicle(self, vehicle_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
        conn.commit()
        conn.close()
        return True

    def add_session(self, vehicle_id, log_path, summary):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostic_sessions (vehicle_id, log_file_path, summary)
            VALUES (?, ?, ?)
        ''', (vehicle_id, log_path, summary))
        conn.commit()
        conn.close()
        return True

    def get_vehicle_sessions(self, vehicle_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM diagnostic_sessions WHERE vehicle_id = ? ORDER BY session_date DESC', (vehicle_id,))
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        conn.close()
        return results
