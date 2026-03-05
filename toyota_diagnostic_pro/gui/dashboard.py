import streamlit as st
import pandas as pd
from toyota_diagnostic_pro.database.vehicle_manager import VehicleManager

vehicle_mgr = VehicleManager()

def render_dashboard():
    st.sidebar.title(f"👤 {st.session_state.user['username']}")
    menu = st.sidebar.radio("เมนูหลัก", ["หน้าแรก", "Live OBD", "Live CAN", "ECU Tuner", "จัดการข้อมูลรถ", "รายงาน", "ออกจากระบบ"])
    
    if menu == "หน้าแรก":
        st.title("ยินดีต้อนรับสู่ Toyota Diagnostic Pro")
        st.write("ระบบวิเคราะห์และวินิจฉัยปัญหารถยนต์ Toyota แบบมืออาชีพ")
        st.image("https://picsum.photos/seed/toyota/800/400", caption="Toyota Diagnostic Engine")
        
        st.info("💡 เคล็ดลับ: เริ่มต้นด้วยการเพิ่มข้อมูลรถในเมนู 'จัดการข้อมูลรถ' ก่อนเริ่มการวินิจฉัย")
        
    elif menu == "Live OBD":
        from toyota_diagnostic_pro.gui.live_view import render_live_obd
        render_live_obd()
        
    elif menu == "Live CAN":
        from toyota_diagnostic_pro.gui.can_view import render_live_can
        render_live_can()
        
    elif menu == "ECU Tuner":
        from toyota_diagnostic_pro.gui.ecu_tuner import render_ecu_tuner
        render_ecu_tuner()
        
    elif menu == "จัดการข้อมูลรถ":
        render_vehicle_management()
        
    elif menu == "รายงาน":
        st.header("📊 รายงานการตรวจเช็ค")
        st.write("ประวัติการตรวจเช็คย้อนหลัง")
        # List sessions from DB
        user_id = st.session_state.user['id']
        vehicles = vehicle_mgr.get_user_vehicles(user_id)
        if vehicles:
            v_map = {f"{v['model']} ({v['vin']})": v for v in vehicles}
            selected_v_label = st.selectbox("เลือกรถเพื่อดูประวัติ", list(v_map.keys()))
            selected_v = v_map[selected_v_label]
            
            sessions = vehicle_mgr.get_vehicle_sessions(selected_v['id'])
            if sessions:
                for s in sessions:
                    with st.expander(f"📅 {s['session_date']}"):
                        st.write(f"**สรุปผล:** {s['summary']}")
                        if s['log_file_path']:
                            st.write(f"**ไฟล์ Log:** `{s['log_file_path']}`")
            else:
                st.info("ยังไม่มีประวัติการตรวจเช็คสำหรับรถคันนี้")
        else:
            st.warning("กรุณาเพิ่มข้อมูลรถก่อน")
        
    elif menu == "ออกจากระบบ":
        del st.session_state.user
        st.rerun()

def render_vehicle_management():
    st.header("📋 จัดการข้อมูลรถ")
    user_id = st.session_state.user['id']
    
    with st.expander("➕ เพิ่มรถใหม่"):
        vin = st.text_input("เลขตัวถัง (VIN)")
        model = st.text_input("รุ่นรถ (เช่น Camry, Hilux Revo)")
        year = st.number_input("ปีรถ", min_value=1990, max_value=2026, value=2020)
        engine = st.selectbox("ประเภทเครื่องยนต์", ["เบนซิน", "ดีเซล", "ไฮบริด"])
        if st.button("บันทึกข้อมูลรถ"):
            success, msg = vehicle_mgr.add_vehicle(user_id, vin, model, year, engine)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
                
    st.subheader("รายการรถของคุณ")
    vehicles = vehicle_mgr.get_user_vehicles(user_id)
    if vehicles:
        df_v = pd.DataFrame(vehicles)
        st.dataframe(df_v[['vin', 'model', 'year', 'engine_type']])
        
        st.subheader("🛠️ แก้ไข/ลบ ข้อมูลรถ")
        selected_vin = st.selectbox("เลือกรถเพื่อจัดการ", [v['vin'] for v in vehicles])
        selected_v = next(v for v in vehicles if v['vin'] == selected_vin)
        
        with st.expander(f"📝 แก้ไขข้อมูล: {selected_v['model']}"):
            new_model = st.text_input("รุ่นรถ", value=selected_v['model'], key="edit_model")
            new_year = st.number_input("ปีรถ", min_value=1990, max_value=2026, value=selected_v['year'], key="edit_year")
            engine_options = ["เบนซิน", "ดีเซล", "ไฮบริด"]
            current_engine_idx = engine_options.index(selected_v['engine_type']) if selected_v['engine_type'] in engine_options else 0
            new_engine = st.selectbox("ประเภทเครื่องยนต์", engine_options, index=current_engine_idx, key="edit_engine")
            
            if st.button("💾 บันทึกการแก้ไข"):
                vehicle_mgr.update_vehicle(selected_v['id'], new_model, new_year, new_engine)
                st.success("อัปเดตข้อมูลสำเร็จ")
                st.rerun()

        if st.button("🗑️ ลบข้อมูลรถที่เลือก"):
            vehicle_mgr.delete_vehicle(selected_v['id'])
            st.success("ลบข้อมูลสำเร็จ")
            st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลรถในระบบ")
