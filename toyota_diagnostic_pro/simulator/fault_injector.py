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

    def inject_evap_leak_small(self):
        """
        จำลองระบบ EVAP รั่วไหลขนาดเล็ก (P0442)
        """
        with self._lock:
            self.simulator.data["TANK_PRESSURE"] = -0.5 # แรงดันตกเล็กน้อย
            self.simulator.data["FUEL_TRIM_ST"] = 5.0
            self.active_faults["EVAP_LEAK_SMALL"] = True

    def inject_evap_leak_large(self):
        """
        จำลองระบบ EVAP รั่วไหลขนาดใหญ่ (P0455)
        """
        with self._lock:
            self.simulator.data["TANK_PRESSURE"] = -2.0 # แรงดันตกมาก
            self.simulator.data["FUEL_TRIM_ST"] = 12.0
            self.active_faults["EVAP_LEAK_LARGE"] = True

    def inject_catalyst_efficiency_low(self):
        """
        จำลองประสิทธิภาพแคทาลิติกต่ำ (P0420)
        O2 Sensor 2 จะแกว่งตาม Sensor 1
        """
        stop_event = threading.Event()
        
        def cat_loop():
            while not stop_event.is_set():
                with self._lock:
                    # ทำให้ O2 Sensor 2 แกว่งตาม Sensor 1 (สัญญาณว่าแคทพัง)
                    self.simulator.data["O2_B1S2"] = self.simulator.data["O2_B1S1"] + random.uniform(-0.05, 0.05)
                time.sleep(0.5)
        
        thread = threading.Thread(target=cat_loop, daemon=True)
        thread.start()
        
        with self._lock:
            self.intermittent_threads["CATALYST_EFFICIENCY"] = (thread, stop_event)
            self.active_faults["CATALYST_EFFICIENCY"] = True

    def inject_iat_sensor_high(self):
        """
        จำลองเซนเซอร์ IAT ค่าสูงผิดปกติ (P0113)
        """
        with self._lock:
            self.simulator.data["INTAKE_TEMP"] = 150 # สูงเกินจริง
            self.active_faults["IAT_SENSOR_HIGH"] = True

    def inject_iat_sensor_low(self):
        """
        จำลองเซนเซอร์ IAT ค่าต่ำผิดปกติ (P0112)
        """
        with self._lock:
            self.simulator.data["INTAKE_TEMP"] = -40 # ต่ำเกินจริง
            self.active_faults["IAT_SENSOR_LOW"] = True

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
            self.simulator.data["INTAKE_TEMP"] = 35
            self.simulator.data["O2_B1S2"] = 0.6
            self.simulator.data["TANK_PRESSURE"] = 0.5
            
            self.active_faults = {}
