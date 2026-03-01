import obd
import time
import random
from toyota_diagnostic_pro.config import PORT, BAUDRATE

class OBDReader:
    def __init__(self, port=PORT, simulator=True):
        self.port = port
        self.simulator = simulator
        self.connection = None
        self.is_connected = False

    def connect(self):
        if self.simulator:
            # ในโหมดจำลอง เราจะคืนค่า True เสมอ
            self.is_connected = True
            return True
        
        try:
            if self.port == "AUTO":
                self.connection = obd.OBD()
            else:
                self.connection = obd.OBD(self.port, baudrate=BAUDRATE)
            
            if self.connection.is_connected():
                self.is_connected = True
                return True
        except Exception as e:
            print(f"OBD Connection Error: {e}")
        
        return False

    def get_live_data(self):
        """
        ดึงข้อมูลเซนเซอร์แบบเรียลไทม์
        """
        if not self.is_connected:
            return {}

        if self.simulator:
            return self._get_mock_data()

        data = {}
        commands = [
            obd.commands.RPM,
            obd.commands.SPEED,
            obd.commands.COOLANT_TEMP,
            obd.commands.THROTTLE_POS,
            obd.commands.ENGINE_LOAD,
            obd.commands.SHORT_FUEL_TRIM_1,
            obd.commands.LONG_FUEL_TRIM_1,
            obd.commands.MAF,
            obd.commands.INTAKE_TEMP,
            obd.commands.O2_B1S1,
        ]

        for cmd in commands:
            response = self.connection.query(cmd)
            if not response.is_null():
                # แปลงค่าเป็นตัวเลข (float/int)
                data[cmd.name] = response.value.magnitude
            else:
                data[cmd.name] = 0

        return data

    def _get_mock_data(self):
        """
        สร้างข้อมูลจำลองสำหรับโหมด Simulator
        """
        return {
            "RPM": random.randint(750, 3000),
            "SPEED": random.randint(0, 120),
            "COOLANT_TEMP": random.randint(85, 98),
            "THROTTLE_POS": random.uniform(5, 40),
            "ENGINE_LOAD": random.uniform(15, 60),
            "FUEL_TRIM_ST": random.uniform(-5, 5),
            "FUEL_TRIM_LT": random.uniform(-2, 2),
            "MAF": random.uniform(2, 50),
            "INTAKE_TEMP": random.randint(35, 50),
            "VOLTAGE": random.uniform(13.5, 14.2),
            "VVT_INTAKE_ANGLE_DIFF": random.uniform(0, 2),
            "VVT_EXHAUST_ANGLE_DIFF": random.uniform(0, 2),
            "INJECTOR_PW": random.uniform(2.0, 4.0),
            "MISFIRE_CYL1": 0,
            "MISFIRE_CYL2": 0,
            "MISFIRE_CYL3": 0,
            "MISFIRE_CYL4": 0,
        }

    def get_dtc(self):
        if self.simulator:
            return ["P0171", "P0300"] if random.random() > 0.8 else []
        
        if not self.is_connected:
            return []
            
        response = self.connection.query(obd.commands.GET_DTC)
        return response.value if not response.is_null() else []

    def clear_dtc(self):
        if self.simulator:
            return True
        if self.is_connected:
            self.connection.query(obd.commands.CLEAR_DTC)
            return True
        return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
        self.is_connected = False
