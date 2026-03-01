# Toyota Diagnostic Pro (TDP)

ระบบวินิจฉัยปัญหารถยนต์ Toyota แบบมืออาชีพ รองรับ OBD-II และ CAN Bus พร้อมระบบจำลอง (Simulator) และวิเคราะห์ปัญหาด้วย Rule Engine ภาษาไทย

## คุณสมบัติหลัก
- **Live OBD-II Data**: อ่านค่าเซนเซอร์แบบเรียลไทม์ (RPM, Speed, Fuel Trim, VVT ฯลฯ)
- **CAN Bus Analysis**: รองรับการถอดรหัสข้อมูลจาก CAN Bus ด้วยไฟล์ DBC
- **Rule Engine**: วิเคราะห์ปัญหาอัตโนมัติด้วยกฎมากกว่า 30 ข้อสำหรับ Toyota
- **Simulator**: จำลองการทำงานของรถยนต์และฉีดความผิดปกติ (Fault Injection)
- **User Authentication**: ระบบสมาชิกและจัดการข้อมูลรถ
- **Report Generation**: สร้างรายงาน PDF ภาษาไทยสำหรับการซ่อมบำรุง

## วิธีการติดตั้ง
1. ติดตั้ง Python 3.12+
2. ติดตั้งไลบรารีที่จำเป็น:
   ```bash
   pip install -r requirements.txt
   ```

## วิธีการใช้งาน
1. รันโปรแกรมด้วยคำสั่ง:
   ```bash
   streamlit run main.py
   ```
2. ลงทะเบียนและเข้าสู่ระบบ
3. เพิ่มข้อมูลรถของคุณในเมนู "จัดการข้อมูลรถ"
4. ไปที่เมนู "Live OBD" เพื่อเริ่มการวินิจฉัย

## โครงสร้างโปรเจกต์
- `core/`: ตัวอ่านข้อมูล OBD และ CAN
- `analyzer/`: ระบบวิเคราะห์ปัญหาและฐานข้อมูล DTC
- `simulator/`: ตัวจำลองข้อมูลรถยนต์
- `gui/`: ส่วนแสดงผล Streamlit
- `database/`: จัดการข้อมูลผู้ใช้และรถยนต์

---
พัฒนาโดย Senior Automotive Software Engineer
