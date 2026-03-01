import random
import time
from threading import Thread, Event

class OBDSimulator:
    def __init__(self):
        self.data = {
            "RPM": 800,
            "SPEED": 0,
            "COOLANT_TEMP": 90,
            "FUEL_TRIM_ST": 0.0,
            "FUEL_TRIM_LT": 0.0,
            "MAF": 3.5,
            "THROTTLE_POS": 12.0,
            "VOLTAGE": 14.1,
            "MISFIRE_CYL1": 0,
            "MISFIRE_CYL2": 0,
            "MISFIRE_CYL3": 0,
            "MISFIRE_CYL4": 0,
            "VVT_INTAKE_ANGLE_DIFF": 0.0,
            "VVT_EXHAUST_ANGLE_DIFF": 0.0,
            "INJECTOR_PW": 2.5 # ms
        }
        self.stop_event = Event()
        self.thread = None

    def start(self):
        self.stop_event.clear()
        self.thread = Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _update_loop(self):
        while not self.stop_event.is_set():
            # จำลองการเปลี่ยนแปลงของค่าต่างๆ
            self.data["RPM"] += random.randint(-50, 50)
            self.data["RPM"] = max(700, min(6000, self.data["RPM"]))
            
            self.data["SPEED"] += random.randint(-2, 2)
            self.data["SPEED"] = max(0, min(180, self.data["SPEED"]))
            
            self.data["FUEL_TRIM_ST"] += random.uniform(-0.5, 0.5)
            self.data["FUEL_TRIM_ST"] = max(-20, min(20, self.data["FUEL_TRIM_ST"]))

            self.data["INJECTOR_PW"] = (self.data["RPM"] / 1000.0) * 1.5 + random.uniform(-0.1, 0.1)
            self.data["INJECTOR_PW"] = max(1.0, min(15.0, self.data["INJECTOR_PW"]))
            
            time.sleep(0.5)

    def get_data(self):
        return self.data.copy()

    def inject_fault(self, fault_type):
        if fault_type == "HIGH_FUEL_TRIM":
            self.data["FUEL_TRIM_LT"] = 26.0
            self.data["FUEL_TRIM_ST"] = 5.0
        elif fault_type == "MISFIRE":
            self.data["MISFIRE_CYL1"] = 15
        elif fault_type == "OVERHEAT":
            self.data["COOLANT_TEMP"] = 110
        elif fault_type == "LOW_VOLTAGE":
            self.data["VOLTAGE"] = 11.5
        elif fault_type == "VVT_ERROR":
            self.data["VVT_INTAKE_ANGLE_DIFF"] = 8.5
            self.data["VVT_EXHAUST_ANGLE_DIFF"] = 7.2
        elif fault_type == "INJECTOR_FAULT":
            self.data["INJECTOR_PW"] = 12.0
