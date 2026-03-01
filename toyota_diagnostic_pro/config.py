# การตั้งค่าพื้นฐานสำหรับ Toyota Diagnostic Pro (TDP)

# พอร์ตสำหรับการเชื่อมต่อ OBD-II (เช่น COM3 บน Windows หรือ /dev/ttyUSB0 บน Linux)
PORT = "AUTO"  # ใช้ "AUTO" เพื่อค้นหาอัตโนมัติ

# ความเร็วในการส่งข้อมูล (Baudrate)
BAUDRATE = 500000  # 500kbps สำหรับ CAN Bus ทั่วไป

# เส้นทางไปยังไฟล์ DBC (Database CAN)
DBC_PATH = "dbc/toyota_can.dbc"

# ภาษาเริ่มต้น
LANGUAGE = "th"

# ธีมเริ่มต้น (light หรือ dark)
THEME = "dark"

# การตั้งค่าการบันทึกข้อมูล (Logging)
LOG_INTERVAL = 1.0  # บันทึกทุก 1 วินาที
LOG_DIR = "logs"

# การตั้งค่า Simulator
SIMULATOR_MODE = True  # เปิดโหมดจำลองเมื่อไม่มีอุปกรณ์จริง
