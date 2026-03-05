import pandas as pd
import os
import threading
import time
from datetime import datetime
from toyota_diagnostic_pro.config import LOG_DIR

class DataLogger:
    def __init__(self, vehicle_vin="unknown", obd_simulator=None, can_reader=None):
        self.vehicle_vin = vehicle_vin
        self.obd_simulator = obd_simulator
        self.can_reader = can_reader
        self.log_dir = LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_file = self._generate_filename()
        self.data_buffer = []
        self.is_running = False
        self.thread = None
        self._lock = threading.Lock()

    def _generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"log_{self.vehicle_vin}_{timestamp}.csv")

    def start_logging(self, filepath=None):
        if self.is_running:
            return
        
        if filepath:
            self.current_file = filepath
            os.makedirs(os.path.dirname(self.current_file), exist_ok=True)
            
        self.is_running = True
        self.thread = threading.Thread(target=self._logging_loop, daemon=True)
        self.thread.start()

    def stop_logging(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.save_to_csv()

    def _logging_loop(self):
        while self.is_running:
            data = {}
            
            # Collect OBD Data
            if self.obd_simulator:
                obd_data = self.obd_simulator.get_data()
                for k, v in obd_data.items():
                    data[f"OBD_{k}"] = v
            
            # Collect CAN Data
            if self.can_reader:
                can_data = self.can_reader.get_live_can_data()
                for k, v in can_data.items():
                    data[f"CAN_{k}"] = v
            
            if data:
                data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with self._lock:
                    self.data_buffer.append(data)
                
                # Auto-save every 10 records
                if len(self.data_buffer) >= 10:
                    self.save_to_csv()
            
            time.sleep(1.0) # Log every second

    def get_log_path(self):
        return self.current_file

    def save_to_csv(self):
        with self._lock:
            if not self.data_buffer:
                return
                
            df = pd.DataFrame(self.data_buffer)
            file_exists = os.path.isfile(self.current_file)
            
            # Append mode
            df.to_csv(self.current_file, mode='a', index=False, header=not file_exists)
            self.data_buffer = []
            return self.current_file
