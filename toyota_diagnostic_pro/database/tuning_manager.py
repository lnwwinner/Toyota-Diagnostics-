import sqlite3
import os
import json
import pandas as pd

class TuningManager:
    def __init__(self, db_path="toyota_diagnostic_pro/database/vehicles.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ecu_map_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                version_name TEXT NOT NULL,
                fuel_map_json TEXT,
                ignition_map_json TEXT,
                vvt_intake_map_json TEXT,
                vvt_exhaust_map_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
            )
        ''')
        conn.commit()
        conn.close()

    def save_version(self, vehicle_id, version_name, fuel_map, ignition_map, vvt_intake_map, vvt_exhaust_map):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            fuel_json = fuel_map.to_json()
            ign_json = ignition_map.to_json()
            vvt_in_json = vvt_intake_map.to_json()
            vvt_ex_json = vvt_exhaust_map.to_json()
            
            cursor.execute('''
                INSERT INTO ecu_map_versions 
                (vehicle_id, version_name, fuel_map_json, ignition_map_json, vvt_intake_map_json, vvt_exhaust_map_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (vehicle_id, version_name, fuel_json, ign_json, vvt_in_json, vvt_ex_json))
            
            conn.commit()
            conn.close()
            return True, f"บันทึกเวอร์ชัน '{version_name}' สำเร็จ"
        except Exception as e:
            return False, str(e)

    def get_versions(self, vehicle_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, version_name, created_at 
            FROM ecu_map_versions 
            WHERE vehicle_id = ? 
            ORDER BY created_at DESC
        ''', (vehicle_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "version_name": row[1],
                "created_at": row[2]
            })
        conn.close()
        return results

    def load_version(self, version_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ecu_map_versions WHERE id = ?', (version_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
            
        columns = [column[0] for column in cursor.description]
        data = dict(zip(columns, row))
        
        # Convert JSON back to DataFrames
        def load_df(json_str):
            df = pd.read_json(json_str)
            # Ensure index and columns are integers for simulator compatibility
            df.index = df.index.astype(int)
            df.columns = df.columns.astype(int)
            return df

        maps = {
            "fuel_map": load_df(data["fuel_map_json"]),
            "ignition_map": load_df(data["ignition_map_json"]),
            "vvt_intake_map": load_df(data["vvt_intake_map_json"]),
            "vvt_exhaust_map": load_df(data["vvt_exhaust_map_json"]),
            "version_name": data["version_name"]
        }
        
        conn.close()
        return maps

    def delete_version(self, version_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ecu_map_versions WHERE id = ?', (version_id,))
        conn.commit()
        conn.close()
        return True
