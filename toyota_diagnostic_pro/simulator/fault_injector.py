import threading
import time
import random

class FaultInjector:
    def __init__(self, simulator):
        self.simulator = simulator
        self.active_faults = {}
        self.intermittent_threads = {}
        self._lock = threading.Lock()

    def inject_high_fuel_trim(self):
        """
        จำลองส่วนผสมบาง (Lean) ทำให้ Fuel Trim สูง
        """
        with self._lock:
            self.simulator.data["FUEL_TRIM_LT"] = 26.0
            self.simulator.data["FUEL_TRIM_ST"] = 5.0
            self.active_faults["HIGH_FUEL_TRIM"] = True

    def inject_misfire(self):
        """
        จำลองการจุดระเบิดผิดพลาด
        """
        with self._lock:
            self.simulator.data["MISFIRE_CYL1"] = 15
            self.active_faults["MISFIRE"] = True

    def inject_overheat(self):
        """
        จำลองเครื่องยนต์ร้อนจัด
        """
        with self._lock:
            self.simulator.data["COOLANT_TEMP"] = 110
            self.active_faults["OVERHEAT"] = True

    def inject_low_voltage(self):
        """
        จำลองแรงดันแบตเตอรี่ต่ำ
        """
        with self._lock:
            self.simulator.data["VOLTAGE"] = 11.5
            self.active_faults["LOW_VOLTAGE"] = True

    def inject_vvt_error(self):
        """
        จำลองระบบ VVT ทำงานผิดปกติ
        """
        with self._lock:
            self.simulator.data["VVT_INTAKE_ANGLE_DIFF"] = 8.5
            self.simulator.data["VVT_EXHAUST_ANGLE_DIFF"] = 7.2
            self.active_faults["VVT_ERROR"] = True

    def inject_injector_fault(self):
        """
        จำลองหัวฉีดค้างหรือฉีดมากเกินไป
        """
        with self._lock:
            self.simulator.data["INJECTOR_PW"] = 12.0
            self.active_faults["INJECTOR_FAULT"] = True

    def inject_complex_lean_condition(self):
        """
        จำลองสภาวะส่วนผสมบางแบบซับซ้อน (Low MAF + High Fuel Trim)
        """
        with self._lock:
            self.simulator.data["MAF"] = 1.2  # MAF ต่ำผิดปกติ
            self.simulator.data["FUEL_TRIM_LT"] = 28.0
            self.simulator.data["FUEL_TRIM_ST"] = 12.0
            self.active_faults["COMPLEX_LEAN"] = True

    def inject_intermittent_misfire(self, frequency=0.3):
        """
        จำลองอาการ Misfire แบบเป็นระยะๆ (Intermittent)
        """
        stop_event = threading.Event()
        
        def misfire_loop():
            while not stop_event.is_set():
                if random.random() < frequency:
                    with self._lock:
                        self.simulator.data["MISFIRE_CYL1"] += 1
                time.sleep(1)
        
        thread = threading.Thread(target=misfire_loop, daemon=True)
        thread.start()
        
        with self._lock:
            self.intermittent_threads["INTERMITTENT_MISFIRE"] = (thread, stop_event)
            self.active_faults["INTERMITTENT_MISFIRE"] = True

    def clear_faults(self):
        """
        ล้างค่าความผิดปกติทั้งหมด
        """
        with self._lock:
            # Stop all intermittent threads
            for name, (thread, stop_event) in self.intermittent_threads.items():
                stop_event.set()
            self.intermittent_threads = {}
            
            # Reset simulator data to normal ranges
            self.simulator.data["FUEL_TRIM_LT"] = 0.0
            self.simulator.data["FUEL_TRIM_ST"] = 0.0
            self.simulator.data["MISFIRE_CYL1"] = 0
            self.simulator.data["COOLANT_TEMP"] = 90
            self.simulator.data["VOLTAGE"] = 14.1
            self.simulator.data["VVT_INTAKE_ANGLE_DIFF"] = 0.0
            self.simulator.data["VVT_EXHAUST_ANGLE_DIFF"] = 0.0
            self.simulator.data["MAF"] = 3.5
            self.simulator.data["INJECTOR_PW"] = 2.5
            
            self.active_faults = {}
