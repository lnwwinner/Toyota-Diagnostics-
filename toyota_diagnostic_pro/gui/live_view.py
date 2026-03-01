import streamlit as st
import time
import pandas as pd
from toyota_diagnostic_pro.simulator.obd_simulator import OBDSimulator
from toyota_diagnostic_pro.simulator.fault_injector import FaultInjector
from toyota_diagnostic_pro.analyzer.rule_engine import RuleEngine
from toyota_diagnostic_pro.core.data_logger import DataLogger
from toyota_diagnostic_pro.gui.report_generator import ReportGenerator
from toyota_diagnostic_pro.database.vehicle_manager import VehicleManager

rules = RuleEngine()
vehicle_mgr = VehicleManager()
report_gen = ReportGenerator()

def render_live_obd():
    st.header("📈 Live OBD Data")
    
    # Select Vehicle
    vehicles = vehicle_mgr.get_user_vehicles(st.session_state.user['id'])
    if not vehicles:
        st.warning("กรุณาเพิ่มข้อมูลรถก่อนเริ่มการวินิจฉัย")
        return
        
    v_options = {f"{v['model']} ({v['vin']})": v for v in vehicles}
    selected_label = st.selectbox("เลือกรถที่กำลังตรวจเช็ค", list(v_options.keys()))
    selected_vehicle = v_options[selected_label]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 เริ่มการเชื่อมต่อ"):
            st.session_state.obd_active = True
            st.session_state.simulator = OBDSimulator()
            st.session_state.simulator.start()
            st.session_state.logger = DataLogger(selected_vehicle['vin'])
            st.session_state.injector = FaultInjector(st.session_state.simulator)
    with col2:
        if st.button("🛑 หยุดการเชื่อมต่อ"):
            if 'simulator' in st.session_state:
                st.session_state.simulator.stop()
            st.session_state.obd_active = False

    if st.session_state.get('obd_active', False):
        st.sidebar.subheader("🛠️ Fault Injection")
        if st.sidebar.button("ฉีด: Fuel Trim สูง"):
            st.session_state.injector.inject_high_fuel_trim()
        if st.sidebar.button("ฉีด: Misfire"):
            st.session_state.injector.inject_misfire()
        if st.sidebar.button("ฉีด: Overheat"):
            st.session_state.injector.inject_overheat()
        if st.sidebar.button("ฉีด: VVT Error"):
            st.session_state.injector.inject_vvt_error()
        if st.sidebar.button("ฉีด: Injector Fault"):
            st.session_state.injector.inject_injector_fault()
        if st.sidebar.button("ล้าง Fault ทั้งหมด"):
            st.session_state.injector.clear_faults()

        # Data history for graphing
        if 'history' not in st.session_state:
            st.session_state.history = pd.DataFrame()

        placeholder = st.empty()
        graph_placeholder = st.empty()
        
        # Simple loop for live update
        for _ in range(50): # Run for 50 iterations
            if not st.session_state.get('obd_active', False):
                break
                
            data = st.session_state.simulator.get_data()
            issues = rules.evaluate(data)
            st.session_state.logger.log(data)
            
            # Update history
            new_row = pd.DataFrame([data])
            new_row['Time'] = pd.to_datetime('now')
            st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(50)

            with placeholder.container():
                st.subheader("📊 Real-time Metrics")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("RPM", f"{data.get('RPM', 0)}")
                c2.metric("Speed", f"{data.get('SPEED', 0)} km/h")
                c3.metric("Temp", f"{data.get('COOLANT_TEMP', 0)} °C")
                c4.metric("Load", f"{data.get('ENGINE_LOAD', 0):.1f} %")
                
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("STFT", f"{data.get('FUEL_TRIM_ST', 0):.1f} %")
                c6.metric("LTFT", f"{data.get('FUEL_TRIM_LT', 0):.1f} %")
                c7.metric("Voltage", f"{data.get('VOLTAGE', 0):.1f} V")
                c8.metric("MAF", f"{data.get('MAF', 0):.1f} g/s")

                st.markdown("---")
                st.subheader("🔧 Advanced Toyota PIDs")
                a1, a2, a3 = st.columns(3)
                a1.metric("VVT Intake Diff", f"{data.get('VVT_INTAKE_ANGLE_DIFF', 0):.2f} °")
                a2.metric("VVT Exhaust Diff", f"{data.get('VVT_EXHAUST_ANGLE_DIFF', 0):.2f} °")
                a3.metric("Injector PW", f"{data.get('INJECTOR_PW', 0):.2f} ms")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Misfire Cyl 1", f"{data.get('MISFIRE_CYL1', 0)}")
                m2.metric("Misfire Cyl 2", f"{data.get('MISFIRE_CYL2', 0)}")
                m3.metric("Misfire Cyl 3", f"{data.get('MISFIRE_CYL3', 0)}")
                m4.metric("Misfire Cyl 4", f"{data.get('MISFIRE_CYL4', 0)}")

                st.markdown("---")
                st.subheader("🚩 Active DTC Codes")
                dtc_list = list(set([issue['DTC'] for issue in issues if issue['DTC'] != "-"]))
                if dtc_list:
                    cols = st.columns(len(dtc_list) if len(dtc_list) < 5 else 5)
                    for i, dtc in enumerate(dtc_list):
                        cols[i % 5].warning(f"**{dtc}**")
                else:
                    st.info("No active DTCs detected.")
                
                if issues:
                    st.error("⚠️ ตรวจพบความผิดปกติ!")
                    for issue in issues:
                        dtc_display = f"[{issue['DTC']}] " if issue['DTC'] != "-" else ""
                        st.write(f"- **{dtc_display}{issue['Symptom']}**: {issue['Recommendation']}")
                else:
                    st.success("✅ ระบบทำงานปกติ")

            with graph_placeholder.container():
                st.markdown("---")
                st.subheader("📈 Real-time Analysis Charts")
                
                # Plot RPM and Speed
                fig1 = px.line(st.session_state.history, x='Time', y=['RPM', 'SPEED'], 
                              title='Engine Speed & Vehicle Speed',
                              labels={'value': 'Value', 'variable': 'Parameter'})
                st.plotly_chart(fig1, use_container_width=True)

                # Plot VVT and Injector PW
                fig2 = px.line(st.session_state.history, x='Time', y=['VVT_INTAKE_ANGLE_DIFF', 'VVT_EXHAUST_ANGLE_DIFF', 'INJECTOR_PW'],
                              title='VVT Timing & Injection Pulse Width',
                              labels={'value': 'Value', 'variable': 'Parameter'})
                st.plotly_chart(fig2, use_container_width=True)
                    
                if st.button("📄 สร้างรายงาน PDF"):
                    pdf_path = report_gen.generate_pdf(selected_vehicle, data, issues)
                    summary = ", ".join([i['Symptom'] for i in issues]) if issues else "ระบบทำงานปกติ"
                    vehicle_mgr.add_session(selected_vehicle['id'], pdf_path, summary)
                    st.success(f"สร้างรายงานสำเร็จและบันทึกประวัติแล้ว: {pdf_path}")
                    with open(pdf_path, "rb") as f:
                        st.download_button("ดาวน์โหลดรายงาน", f, file_name=f"report_{selected_vehicle['vin']}.pdf")
            
            time.sleep(1)
