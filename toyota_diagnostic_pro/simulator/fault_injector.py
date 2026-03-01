class FaultInjector:
    def __init__(self, simulator):
        self.simulator = simulator

    def inject_high_fuel_trim(self):
        """
        จำลองส่วนผสมบาง (Lean) ทำให้ Fuel Trim สูง
        """
        self.simulator.inject_fault("HIGH_FUEL_TRIM")

    def inject_misfire(self):
        """
        จำลองการจุดระเบิดผิดพลาด
        """
        self.simulator.inject_fault("MISFIRE")

    def inject_overheat(self):
        """
        จำลองเครื่องยนต์ร้อนจัด
        """
        self.simulator.inject_fault("OVERHEAT")

    def inject_low_voltage(self):
        """
        จำลองแรงดันแบตเตอรี่ต่ำ
        """
        self.simulator.inject_fault("LOW_VOLTAGE")

    def inject_vvt_error(self):
        """
        จำลองระบบ VVT ทำงานผิดปกติ
        """
        self.simulator.inject_fault("VVT_ERROR")

    def inject_injector_fault(self):
        """
        จำลองหัวฉีดค้างหรือฉีดมากเกินไป
        """
        self.simulator.inject_fault("INJECTOR_FAULT")

    def clear_faults(self):
        """
        ล้างค่าความผิดปกติทั้งหมด
        """
        self.simulator.data["FUEL_TRIM_LT"] = 0.0
        self.simulator.data["FUEL_TRIM_ST"] = 0.0
        self.simulator.data["MISFIRE_CYL1"] = 0
        self.simulator.data["COOLANT_TEMP"] = 90
        self.simulator.data["VOLTAGE"] = 14.1
        self.simulator.data["VVT_INTAKE_ANGLE_DIFF"] = 0.0
