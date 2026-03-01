import can
import cantools
import os
import glob
from toyota_diagnostic_pro.config import DBC_PATH

class CANReader:
    def __init__(self, interface='socketcan', channel='vcan0'):
        self.interface = interface
        self.channel = channel
        self.db = cantools.database.Database()
        self.bus = None
        self.is_connected = False
        self._load_dbcs()

    def _load_dbcs(self):
        """
        โหลดไฟล์ .dbc ทั้งหมดจากโฟลเดอร์ dbc/
        """
        dbc_files = glob.glob("toyota_diagnostic_pro/dbc/*.dbc")
        for f in dbc_files:
            try:
                self.db.add_dbc_file(f)
                print(f"Loaded DBC: {f}")
            except Exception as e:
                print(f"Error loading DBC {f}: {e}")

    def connect(self):
        try:
            # ในสภาพแวดล้อมจริงต้องระบุ interface และ channel
            # self.bus = can.interface.Bus(interface=self.interface, channel=self.channel)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"CAN Connection Error: {e}")
            return False

    def decode_message(self, msg_id, data):
        """
        ถอดรหัสข้อความ CAN ตามไฟล์ DBC
        """
        try:
            return self.db.decode_message(msg_id, data)
        except KeyError:
            return None

    def get_live_can_data(self):
        """
        จำลองการอ่านข้อมูลจาก CAN Bus
        """
        if not self.is_connected:
            return {}
            
        import random
        # ในโหมดจำลอง เราจะคืนค่าตัวอย่างที่สอดคล้องกับ DBC
        base_speed = 40.0 + random.uniform(-2, 2)
        return {
            "SteeringAngle": random.uniform(-30, 30),
            "WheelSpeed_FL": base_speed + random.uniform(-0.5, 0.5),
            "WheelSpeed_FR": base_speed + random.uniform(-0.5, 0.5),
            "WheelSpeed_RL": base_speed + random.uniform(-0.5, 0.5),
            "WheelSpeed_RR": base_speed + random.uniform(-0.5, 0.5),
            "BrakePressure": random.choice([0, 0, 0, 5, 10]),
            "GearPosition": random.choice(["P", "R", "N", "D", "S"])
        }
