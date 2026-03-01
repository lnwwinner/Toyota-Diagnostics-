import pandas as pd
import os

class RuleEngine:
    def __init__(self, rules_path="toyota_diagnostic_pro/database/toyota_rules.xlsx"):
        self.rules_path = rules_path
        self.rules_df = None
        self._ensure_rules_exist()
        self.load_rules()

    def _ensure_rules_exist(self):
        """
        Creates the rules Excel file if it doesn't exist.
        """
        if not os.path.exists(self.rules_path):
            # Create directory if needed
            os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
            
            # Sample Rules for Toyota
            data = [
                # Fuel System
                {"RuleID": "R001", "Condition": "FUEL_TRIM_LT + FUEL_TRIM_ST > 25", "DTC": "P0171", "Symptom_TH": "ส่วนผสมบางเกินไป (Lean)", "Recommendation_TH": "ตรวจสอบรอยรั่วท่อไอดี, MAF Sensor, แรงดันน้ำมันตก"},
                {"RuleID": "R002", "Condition": "FUEL_TRIM_LT + FUEL_TRIM_ST < -25", "DTC": "P0172", "Symptom_TH": "ส่วนผสมหนาเกินไป (Rich)", "Recommendation_TH": "ตรวจสอบหัวฉีดรั่ว, ไส้กรองอากาศตัน, O2 Sensor เสื่อม"},
                # Misfire
                {"RuleID": "R003", "Condition": "MISFIRE_CYL1 > 10", "DTC": "P0301", "Symptom_TH": "สูบ 1 จุดระเบิดผิดพลาด", "Recommendation_TH": "เช็คหัวเทียนสูบ 1, คอยล์จุดระเบิดสูบ 1, กำลังอัดสูบ 1"},
                {"RuleID": "R004", "Condition": "MISFIRE_CYL2 > 10", "DTC": "P0302", "Symptom_TH": "สูบ 2 จุดระเบิดผิดพลาด", "Recommendation_TH": "เช็คหัวเทียนสูบ 2, คอยล์จุดระเบิดสูบ 2"},
                {"RuleID": "R005", "Condition": "MISFIRE_CYL3 > 10", "DTC": "P0303", "Symptom_TH": "สูบ 3 จุดระเบิดผิดพลาด", "Recommendation_TH": "เช็คหัวเทียนสูบ 3, คอยล์จุดระเบิดสูบ 3"},
                {"RuleID": "R006", "Condition": "MISFIRE_CYL4 > 10", "DTC": "P0304", "Symptom_TH": "สูบ 4 จุดระเบิดผิดพลาด", "Recommendation_TH": "เช็คหัวเทียนสูบ 4, คอยล์จุดระเบิดสูบ 4"},
                # Cooling System
                {"RuleID": "R007", "Condition": "COOLANT_TEMP > 105", "DTC": "P0217", "Symptom_TH": "เครื่องยนต์ร้อนจัด (Overheat)", "Recommendation_TH": "ตรวจสอบระดับน้ำหล่อเย็น, พัดลมหม้อน้ำ, วาล์วน้ำ"},
                {"RuleID": "R008", "Condition": "COOLANT_TEMP < 70 and RUN_TIME > 600", "DTC": "P0128", "Symptom_TH": "อุณหภูมิน้ำต่ำผิดปกติ (วาล์วน้ำเปิดค้าง)", "Recommendation_TH": "เปลี่ยนวาล์วน้ำ (Thermostat)"},
                # Battery/Charging
                {"RuleID": "R009", "Condition": "VOLTAGE < 12.0 and RPM > 1000", "DTC": "P0562", "Symptom_TH": "ไฟชาร์จต่ำ (Alternator ไม่ทำงาน)", "Recommendation_TH": "ตรวจสอบไดชาร์จ, สายพานหน้าเครื่อง, แบตเตอรี่"},
                {"RuleID": "R010", "Condition": "VOLTAGE > 15.0", "DTC": "P0563", "Symptom_TH": "ไฟชาร์จสูงเกิน (Overcharge)", "Recommendation_TH": "ตรวจสอบ Regulator ของไดชาร์จ"},
                # MAF/Air
                {"RuleID": "R011", "Condition": "MAF < 2.0 and RPM > 600 and RPM < 800", "DTC": "P0101", "Symptom_TH": "ค่า MAF ต่ำผิดปกติที่รอบเดินเบา", "Recommendation_TH": "ทำความสะอาด MAF Sensor, เช็ครอยรั่วหลังลิ้นปีกผีเสื้อ"},
                {"RuleID": "R012", "Condition": "MAF > 100 and RPM < 2000", "DTC": "P0101", "Symptom_TH": "ค่า MAF สูงผิดปกติ", "Recommendation_TH": "เช็คสายไฟ MAF, เช็คกราวด์"},
                # Throttle
                {"RuleID": "R013", "Condition": "THROTTLE_POS > 5 and RPM < 600", "DTC": "P0506", "Symptom_TH": "รอบเดินเบาต่ำกว่าเป้าหมาย", "Recommendation_TH": "ล้างลิ้นปีกผีเสื้อ, เช็คระบบ ISC"},
                {"RuleID": "R014", "Condition": "THROTTLE_POS < 1 and RPM > 1000", "DTC": "P0507", "Symptom_TH": "รอบเดินเบาสูงกว่าเป้าหมาย", "Recommendation_TH": "เช็ครอยรั่วท่อไอดี, เช็ควาล์ว PCV"},
                # O2 Sensor
                {"RuleID": "R015", "Condition": "O2_B1S1 < 0.1 and FUEL_TRIM_ST > 10", "DTC": "P0130", "Symptom_TH": "O2 Sensor ค้างที่ค่าบาง (Lean Stuck)", "Recommendation_TH": "เปลี่ยน O2 Sensor ตัวหน้า"},
                {"RuleID": "R016", "Condition": "O2_B1S1 > 0.9 and FUEL_TRIM_ST < -10", "DTC": "P0130", "Symptom_TH": "O2 Sensor ค้างที่ค่าหนา (Rich Stuck)", "Recommendation_TH": "เปลี่ยน O2 Sensor ตัวหน้า"},
                # VVT (Variable Valve Timing) - Specific to Toyota
                {"RuleID": "R017", "Condition": "VVT_INTAKE_ANGLE_DIFF > 5", "DTC": "P0011", "Symptom_TH": "องศา VVT ฝั่งไอดีผิดปกติ (Over-advanced)", "Recommendation_TH": "เช็ค OCV Valve, กรอง VVT, แรงดันน้ำมันเครื่อง"},
                {"RuleID": "R018", "Condition": "VVT_EXHAUST_ANGLE_DIFF > 5", "DTC": "P0014", "Symptom_TH": "องศา VVT ฝั่งไอเสียผิดปกติ (Over-advanced)", "Recommendation_TH": "เช็ค OCV Valve ฝั่งไอเสีย"},
                # Injector
                {"RuleID": "R031", "Condition": "INJECTOR_PW > 10 and RPM < 1000", "DTC": "P0200", "Symptom_TH": "หัวฉีดฉีดน้ำมันนานผิดปกติที่รอบต่ำ", "Recommendation_TH": "เช็คหัวฉีดรั่ว, เช็คแรงดันน้ำมันเชื้อเพลิง"},
                {"RuleID": "R032", "Condition": "INJECTOR_PW < 1 and RPM > 2000", "DTC": "P0200", "Symptom_TH": "หัวฉีดฉีดน้ำมันน้อยผิดปกติ", "Recommendation_TH": "เช็คปลั๊กหัวฉีด, เช็คกล่อง ECU"},
                # Catalyst
                {"RuleID": "R019", "Condition": "CAT_TEMP_B1S1 > 900", "DTC": "P0420", "Symptom_TH": "แคตตาไลติกร้อนจัด", "Recommendation_TH": "ระวังไฟไหม้, เช็คหัวฉีดรั่ว, เช็คระบบจุดระเบิด"},
                # Engine Load
                {"RuleID": "R020", "Condition": "ENGINE_LOAD > 90 and RPM < 1000", "DTC": "-", "Symptom_TH": "ภาระเครื่องยนต์สูงที่รอบต่ำ", "Recommendation_TH": "เช็คระบบเกียร์, เบรกติด"},
                # Intake Air Temp
                {"RuleID": "R021", "Condition": "INTAKE_TEMP > 70", "DTC": "P0110", "Symptom_TH": "อุณหภูมิไอดีสูงเกินไป", "Recommendation_TH": "เช็คระบบระบายความร้อน Intercooler (ถ้ามี), เช็คตำแหน่งกรองอากาศ"},
                # Speed
                {"RuleID": "R022", "Condition": "SPEED == 0 and RPM > 2000 and ENGINE_LOAD > 50", "DTC": "P0500", "Symptom_TH": "เร่งเครื่องแต่รถไม่วิ่ง (หรือ Speed Sensor เสีย)", "Recommendation_TH": "เช็คเกียร์, เช็ค Speed Sensor"},
                # Fuel Pressure
                {"RuleID": "R023", "Condition": "FUEL_PRESSURE < 300", "DTC": "P0087", "Symptom_TH": "แรงดันรางน้ำมันต่ำ (Commonrail/Direct Injection)", "Recommendation_TH": "เช็คกรองโซล่า, ปั๊มแรงดันสูง, SCV Valve"},
                 # Generic
                {"RuleID": "R024", "Condition": "BAROMETRIC_PRESSURE < 90", "DTC": "-", "Symptom_TH": "แรงดันบรรยากาศต่ำ (ขึ้นเขา)", "Recommendation_TH": "ปกติหากขับขี่บนที่สูง"},
                {"RuleID": "R025", "Condition": "CONTROL_MODULE_VOLTAGE < 11", "DTC": "P0560", "Symptom_TH": "ไฟเลี้ยงกล่อง ECU ต่ำ", "Recommendation_TH": "เช็คแบตเตอรี่, เช็คขั้วต่อ ECU"},
                {"RuleID": "R026", "Condition": "AMBIENT_AIR_TEMP > 50", "DTC": "-", "Symptom_TH": "อุณหภูมิภายนอกสูงมาก", "Recommendation_TH": "ระวังความร้อนขึ้น"},
                {"RuleID": "R027", "Condition": "OIL_TEMP > 120", "DTC": "-", "Symptom_TH": "น้ำมันเครื่องร้อนจัด", "Recommendation_TH": "จอดพัก, เช็คระบบระบายความร้อนน้ำมันเครื่อง"},
                {"RuleID": "R028", "Condition": "THROTTLE_POS > 90 and ENGINE_LOAD < 20", "DTC": "-", "Symptom_TH": "เหยียบคันเร่งสุดแต่โหลดต่ำ", "Recommendation_TH": "เช็คคลัตช์ลื่น (เกียร์ธรรมดา) หรือ Torque Converter"},
                {"RuleID": "R029", "Condition": "EQUIV_RATIO > 1.2", "DTC": "-", "Symptom_TH": "ส่วนผสมหนามาก (Lambda)", "Recommendation_TH": "เช็คหัวฉีด, O2 Sensor"},
                {"RuleID": "R030", "Condition": "EQUIV_RATIO < 0.8", "DTC": "-", "Symptom_TH": "ส่วนผสมบางมาก (Lambda)", "Recommendation_TH": "เช็คปั๊มติ๊ก, กรองเบนซิน"},
            ]
            df = pd.DataFrame(data)
            df.to_excel(self.rules_path, index=False)
            print(f"Created default rules at {self.rules_path}")

    def load_rules(self):
        """
        Loads rules from the Excel file.
        """
        if os.path.exists(self.rules_path):
            self.rules_df = pd.read_excel(self.rules_path)
        else:
            self.rules_df = pd.DataFrame()

    def evaluate(self, sensor_data):
        """
        Evaluate sensor data against rules.
        :param sensor_data: Dict of sensor values e.g. {'RPM': 800, 'COOLANT_TEMP': 90}
        :return: List of dicts with issues found
        """
        issues = []
        if self.rules_df is None or self.rules_df.empty:
            return issues

        # Prepare local variables for eval
        context = sensor_data.copy()
        
        for index, row in self.rules_df.iterrows():
            condition = row['Condition']
            try:
                # Use python eval to check condition
                # We assume sensor_data contains keys used in condition
                if eval(condition, {}, context):
                    issues.append({
                        "RuleID": row['RuleID'],
                        "DTC": row['DTC'],
                        "Symptom": row['Symptom_TH'],
                        "Recommendation": row['Recommendation_TH']
                    })
            except NameError:
                # Variable not found in sensor data, skip rule
                continue
            except Exception as e:
                # Ignore other errors during evaluation
                continue
                
        return issues
