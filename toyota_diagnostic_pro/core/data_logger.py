import pandas as pd
import os
from datetime import datetime
from toyota_diagnostic_pro.config import LOG_DIR

class DataLogger:
    def __init__(self, vehicle_vin="unknown"):
        self.vehicle_vin = vehicle_vin
        self.log_dir = LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_file = self._generate_filename()
        self.data_buffer = []

    def _generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_dir, f"log_{self.vehicle_vin}_{timestamp}.csv")

    def log(self, data_dict):
        """
        บันทึกข้อมูลลงใน Buffer และเขียนลงไฟล์
        """
        data_dict['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data_buffer.append(data_dict)
        
        # เขียนลงไฟล์ทุกๆ 10 เรคคอร์ด หรือเมื่อจบเซสชัน
        if len(self.data_buffer) >= 10:
            self.save_to_csv()

    def save_to_csv(self):
        if not self.data_buffer:
            return
            
        df = pd.DataFrame(self.data_buffer)
        file_exists = os.path.isfile(self.current_file)
        
        # Append mode
        df.to_csv(self.current_file, mode='a', index=False, header=not file_exists)
        self.data_buffer = []
        return self.current_file
