import sqlite3
import os

class DTCDatabase:
    def __init__(self, db_path="toyota_diagnostic_pro/database/dtc_thai.db"):
        """
        Inits the DTC Database manager.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """
        Creates the database and table if they don't exist, and populates with sample data.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dtc_codes (
                code TEXT PRIMARY KEY,
                description_en TEXT,
                description_th TEXT,
                recommendation_th TEXT
            )
        ''')
        
        # Check if empty, if so, populate with sample data
        cursor.execute('SELECT count(*) FROM dtc_codes')
        if cursor.fetchone()[0] == 0:
            self._populate_sample_data(cursor)
            
        conn.commit()
        conn.close()

    def _populate_sample_data(self, cursor):
        """
        Inserts sample Toyota DTC codes into the database.
        """
        sample_data = [
            ("P0101", "Mass or Volume Air Flow Circuit Range/Performance", "ค่าการไหลของอากาศผิดปกติ (MAF Sensor)", "ตรวจสอบไส้กรองอากาศ, ทำความสะอาด MAF Sensor, ตรวจสอบรอยรั่วท่อไอดี"),
            ("P0171", "System Too Lean (Bank 1)", "ส่วนผสมบางเกินไป (Bank 1)", "ตรวจสอบรอยรั่วท่อไอดี, ตรวจสอบแรงดันน้ำมันเชื้อเพลิง, ตรวจสอบ O2 Sensor"),
            ("P0172", "System Too Rich (Bank 1)", "ส่วนผสมหนาเกินไป (Bank 1)", "ตรวจสอบหัวฉีดรั่ว, ตรวจสอบไส้กรองอากาศตัน, ตรวจสอบ MAF Sensor"),
            ("P0300", "Random/Multiple Cylinder Misfire Detected", "ตรวจพบการจุดระเบิดผิดพลาดหลายสูบ", "ตรวจสอบหัวเทียน, คอยล์จุดระเบิด, แรงดันน้ำมันเชื้อเพลิง"),
            ("P0301", "Cylinder 1 Misfire Detected", "จุดระเบิดผิดพลาดสูบ 1", "ตรวจสอบหัวเทียนสูบ 1, คอยล์สูบ 1, หัวฉีดสูบ 1"),
            ("P0302", "Cylinder 2 Misfire Detected", "จุดระเบิดผิดพลาดสูบ 2", "ตรวจสอบหัวเทียนสูบ 2, คอยล์สูบ 2, หัวฉีดสูบ 2"),
            ("P0303", "Cylinder 3 Misfire Detected", "จุดระเบิดผิดพลาดสูบ 3", "ตรวจสอบหัวเทียนสูบ 3, คอยล์สูบ 3, หัวฉีดสูบ 3"),
            ("P0304", "Cylinder 4 Misfire Detected", "จุดระเบิดผิดพลาดสูบ 4", "ตรวจสอบหัวเทียนสูบ 4, คอยล์สูบ 4, หัวฉีดสูบ 4"),
            ("P0420", "Catalyst System Efficiency Below Threshold (Bank 1)", "ประสิทธิภาพแคตตาไลติกต่ำกว่าเกณฑ์ (Bank 1)", "ตรวจสอบ O2 Sensor ตัวหลัง, ตรวจสอบรอยรั่วท่อไอเสีย, เปลี่ยนแคตตาไลติก"),
            ("P0442", "Evaporative Emission Control System Leak Detected (Small Leak)", "ตรวจพบการรั่วในระบบ EVAP (รั่วเล็กน้อย)", "ตรวจสอบฝาถังน้ำมัน, ตรวจสอบท่อ EVAP"),
            ("P0500", "Vehicle Speed Sensor", "เซนเซอร์ความเร็วรถยนต์ผิดปกติ", "ตรวจสอบเซนเซอร์ความเร็ว, ตรวจสอบสายไฟ"),
            ("P0113", "Intake Air Temperature Sensor 1 Circuit High", "วงจรเซนเซอร์อุณหภูมิอากาศเข้าสูง (IAT)", "ตรวจสอบปลั๊ก IAT, ตรวจสอบสายไฟขาด"),
            ("P0120", "Throttle/Pedal Position Sensor/Switch A Circuit", "วงจรเซนเซอร์ตำแหน่งลิ้นปีกผีเสื้อ A ผิดปกติ", "ตรวจสอบ TPS Sensor, ทำความสะอาดลิ้นปีกผีเสื้อ"),
            ("P0135", "O2 Sensor Heater Circuit (Bank 1 Sensor 1)", "วงจรฮีตเตอร์ O2 Sensor ผิดปกติ (ตัวหน้า)", "ตรวจสอบฟิวส์, ตรวจสอบ O2 Sensor"),
            ("P0335", "Crankshaft Position Sensor A Circuit", "วงจรเซนเซอร์เพลาข้อเหวี่ยงผิดปกติ", "ตรวจสอบเซนเซอร์เพลาข้อเหวี่ยง, ตรวจสอบสายไฟ"),
            ("P0340", "Camshaft Position Sensor Circuit", "วงจรเซนเซอร์เพลาลูกเบี้ยวผิดปกติ", "ตรวจสอบเซนเซอร์เพลาลูกเบี้ยว, ตรวจสอบมาร์คสายพานราวลิ้น"),
            ("P0505", "Idle Control System", "ระบบควบคุมรอบเดินเบาผิดปกติ", "ทำความสะอาดลิ้นปีกผีเสื้อ, ตรวจสอบมอเตอร์รอบเดินเบา"),
            ("P0106", "Manifold Absolute Pressure/Barometric Pressure Circuit Range/Performance", "เซนเซอร์ MAP ทำงานผิดปกติ", "ตรวจสอบท่อสุญญากาศ, เปลี่ยน MAP Sensor"),
            ("P0118", "Engine Coolant Temperature Circuit High", "วงจรเซนเซอร์อุณหภูมิน้ำหล่อเย็นสูง", "ตรวจสอบปลั๊ก ECT, ตรวจสอบระดับน้ำหล่อเย็น"),
            ("P0401", "Exhaust Gas Recirculation Flow Insufficient Detected", "การไหลเวียนไอเสีย (EGR) ไม่เพียงพอ", "ทำความสะอาดวาล์ว EGR, ตรวจสอบท่อ EGR อุดตัน"),
            ("P0440", "Evaporative Emission Control System", "ระบบควบคุมไอระเหยน้ำมันเชื้อเพลิงผิดปกติ", "ตรวจสอบฝาถังน้ำมัน, ตรวจสอบถังดักไอเบนซิน"),
            ("P0455", "Evaporative Emission Control System Leak Detected (Gross Leak)", "ตรวจพบการรั่วในระบบ EVAP (รั่วมาก)", "ตรวจสอบฝาถังน้ำมันปิดสนิทหรือไม่, ตรวจสอบท่อ EVAP หลุด"),
            ("P0138", "O2 Sensor Circuit High Voltage (Bank 1 Sensor 2)", "แรงดันไฟ O2 Sensor สูงเกินไป (ตัวหลัง)", "ตรวจสอบ O2 Sensor ตัวหลัง, ตรวจสอบสายไฟช็อต"),
            ("P0141", "O2 Sensor Heater Circuit (Bank 1 Sensor 2)", "วงจรฮีตเตอร์ O2 Sensor ผิดปกติ (ตัวหลัง)", "ตรวจสอบฟิวส์, ตรวจสอบ O2 Sensor ตัวหลัง"),
            ("P0325", "Knock Sensor 1 Circuit", "วงจร Knock Sensor ผิดปกติ", "ตรวจสอบ Knock Sensor, ตรวจสอบสายไฟ"),
            ("P0125", "Insufficient Coolant Temperature for Closed Loop Fuel Control", "อุณหภูมิน้ำหล่อเย็นไม่เพียงพอสำหรับการควบคุมเชื้อเพลิงแบบ Closed Loop", "ตรวจสอบวาล์วน้ำ, ตรวจสอบเซนเซอร์อุณหภูมิน้ำ"),
            ("P0174", "System Too Lean (Bank 2)", "ส่วนผสมบางเกินไป (Bank 2)", "ตรวจสอบรอยรั่วท่อไอดี, ตรวจสอบแรงดันน้ำมันเชื้อเพลิง"),
            ("P0175", "System Too Rich (Bank 2)", "ส่วนผสมหนาเกินไป (Bank 2)", "ตรวจสอบหัวฉีดรั่ว, ตรวจสอบไส้กรองอากาศ"),
            ("P0430", "Catalyst System Efficiency Below Threshold (Bank 2)", "ประสิทธิภาพแคตตาไลติกต่ำกว่าเกณฑ์ (Bank 2)", "ตรวจสอบ O2 Sensor, เปลี่ยนแคตตาไลติก"),
            ("P0507", "Idle Control System RPM Higher Than Expected", "รอบเดินเบาสูงกว่าปกติ", "ตรวจสอบรอยรั่วท่อไอดี, ล้างลิ้นปีกผีเสื้อ"),
        ]
        cursor.executemany('INSERT INTO dtc_codes VALUES (?, ?, ?, ?)', sample_data)

    def get_dtc_description(self, code):
        """
        ดึงข้อมูล DTC จากฐานข้อมูล
        :param code: รหัส DTC (เช่น P0101)
        :return: Dictionary ข้อมูล DTC หรือ None ถ้าไม่พบ
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dtc_codes WHERE code = ?', (code,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "code": row[0],
                "description_en": row[1],
                "description_th": row[2],
                "recommendation_th": row[3]
            }
        return None

    def get_all_dtcs(self):
        """
        ดึงข้อมูล DTC ทั้งหมด
        :return: List of tuples
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dtc_codes')
        rows = cursor.fetchall()
        conn.close()
        return rows
