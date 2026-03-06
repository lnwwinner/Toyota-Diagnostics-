import random
import time
import pandas as pd
import numpy as np
from threading import Thread, Event
from toyota_diagnostic_pro.database.ecu_defaults import get_default_maps

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
            "ENGINE_LOAD": 20.0,
            "VOLTAGE": 14.1,
            "MISFIRE_CYL1": 0,
            "MISFIRE_CYL2": 0,
            "MISFIRE_CYL3": 0,
            "MISFIRE_CYL4": 0,
            "VVT_INTAKE_ANGLE_DIFF": 0.0,
            "VVT_EXHAUST_ANGLE_DIFF": 0.0,
            "VVT_INTAKE_TARGET": 0.0,
            "VVT_EXHAUST_TARGET": 0.0,
            "INJECTOR_PW": 2.5, # ms
            "IGNITION_TIMING": 10.0, # deg
            "O2_B1S1": 0.5, # V
            "O2_B1S2": 0.5, # V
            "RUN_TIME": 0, # s
            "INTAKE_TEMP": 35, # C
            "FUEL_PRESSURE": 400, # kPa
            "BAROMETRIC_PRESSURE": 101, # kPa
            "CONTROL_MODULE_VOLTAGE": 14.0, # V
            "AMBIENT_AIR_TEMP": 30, # C
            "OIL_TEMP": 95, # C
            "EQUIV_RATIO": 1.0, # Lambda
            "CAT_TEMP_B1S1": 450, # C
            "TANK_PRESSURE": 0.5 # kPa
        }
        self.start_time = time.time()
        self.stop_event = Event()
        self.pause_event = Event()
        self.thread = None
        self.simulation_speed = 1.0 # Multiplier for delay (0.5s / speed)
        
        # VVT Configuration
        self.vvt_response_speed = 0.5 # 0.1 to 1.0
        self.vvt_intake_offset = 0.0
        self.vvt_exhaust_offset = 0.0
        
        # Initialize ECU Maps (5x5 Grid)
        self.rpm_points = [1000, 2000, 3000, 4000, 5000]
        self.load_points = [20, 40, 60, 80, 100]
        
        self.reset_to_defaults()

    def reset_to_defaults(self):
        # Default to a generic Toyota profile
        self.load_vehicle_defaults("Generic", "Gasoline")

    def load_vehicle_defaults(self, model, engine_type):
        """
        Loads default maps for a specific vehicle model.
        """
        defaults = get_default_maps(model, engine_type)
        self.fuel_map = defaults["fuel_map"]
        self.ignition_map = defaults["ignition_map"]
        self.vvt_intake_map = defaults["vvt_intake_map"]
        self.vvt_exhaust_map = defaults["vvt_exhaust_map"]
        self.simulation_speed = 1.0
        self.pause_event.clear()

    def start(self):
        self.stop_event.clear()
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self._update_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.stop_event.set()

    def pause(self):
        self.pause_event.set()

    def resume(self):
        self.pause_event.clear()

    def set_speed(self, speed):
        self.simulation_speed = max(0.1, min(10.0, speed))

    def step(self):
        """Perform a single simulation step manually."""
        self._perform_step()

    def update_fuel_map(self, new_map_df):
        self.fuel_map = new_map_df

    def update_ignition_map(self, new_map_df):
        self.ignition_map = new_map_df

    def update_vvt_intake_map(self, new_map_df):
        self.vvt_intake_map = new_map_df

    def update_vvt_exhaust_map(self, new_map_df):
        self.vvt_exhaust_map = new_map_df

    def _get_map_value(self, map_df, rpm, load):
        # Find nearest RPM index
        rpm_idx = min(range(len(self.rpm_points)), key=lambda i: abs(self.rpm_points[i]-rpm))
        target_rpm = self.rpm_points[rpm_idx]
        
        # Find nearest Load index
        load_idx = min(range(len(self.load_points)), key=lambda i: abs(self.load_points[i]-load))
        target_load = self.load_points[load_idx]
        
        return map_df.loc[target_rpm, target_load]

    def _perform_step(self):
        # Simulate RPM and Load changes
        self.data["RPM"] += random.randint(-50, 50)
        self.data["RPM"] = max(800, min(5500, self.data["RPM"]))
        
        self.data["ENGINE_LOAD"] += random.randint(-5, 5)
        self.data["ENGINE_LOAD"] = max(10, min(100, self.data["ENGINE_LOAD"]))
        
        # Get Map Values
        fuel_mult = self._get_map_value(self.fuel_map, self.data["RPM"], self.data["ENGINE_LOAD"])
        ign_timing = self._get_map_value(self.ignition_map, self.data["RPM"], self.data["ENGINE_LOAD"])
        vvt_in = self._get_map_value(self.vvt_intake_map, self.data["RPM"], self.data["ENGINE_LOAD"])
        vvt_ex = self._get_map_value(self.vvt_exhaust_map, self.data["RPM"], self.data["ENGINE_LOAD"])
        
        # Apply Map Values to Simulation
        base_pw = 2.0
        self.data["INJECTOR_PW"] = base_pw * (self.data["RPM"]/2000) * (self.data["ENGINE_LOAD"]/50) * fuel_mult
        self.data["IGNITION_TIMING"] = ign_timing + random.uniform(-0.5, 0.5)
        self.data["VVT_INTAKE_ANGLE_DIFF"] = vvt_in + random.uniform(-0.2, 0.2)
        self.data["VVT_EXHAUST_ANGLE_DIFF"] = vvt_ex + random.uniform(-0.2, 0.2)

        self.data["FUEL_TRIM_ST"] = (1.0 - fuel_mult) * 20.0 
        self.data["SPEED"] = self.data["RPM"] * 0.02 
        
        # Update new PIDs
        self.data["RUN_TIME"] = int(time.time() - self.start_time)
        self.data["O2_B1S1"] = 0.45 + (0.4 * np.sin(time.time() * 2)) + (self.data["FUEL_TRIM_ST"] / 100)
        self.data["O2_B1S1"] = max(0.1, min(0.9, self.data["O2_B1S1"]))
        
        # O2 Sensor 2 should be more stable if catalyst is working
        self.data["O2_B1S2"] = 0.6 + (0.05 * np.sin(time.time() * 0.5))
        self.data["O2_B1S2"] = max(0.1, min(0.9, self.data["O2_B1S2"]))
        
        self.data["TANK_PRESSURE"] = 0.5 + (0.1 * np.sin(time.time() * 0.1))
        
        self.data["CAT_TEMP_B1S1"] = 400 + (self.data["RPM"] / 10) + (self.data["ENGINE_LOAD"] * 2)
        self.data["OIL_TEMP"] = 80 + (self.data["COOLANT_TEMP"] * 0.2) + (self.data["ENGINE_LOAD"] * 0.1)
        self.data["EQUIV_RATIO"] = 1.0 / fuel_mult if fuel_mult > 0 else 1.0

    def _update_loop(self):
        while not self.stop_event.is_set():
            if not self.pause_event.is_set():
                self._perform_step()
            
            delay = 0.5 / self.simulation_speed
            time.sleep(delay)

    def get_data(self):
        return self.data.copy()
