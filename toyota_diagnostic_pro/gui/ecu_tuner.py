import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from toyota_diagnostic_pro.database.tuning_manager import TuningManager
from toyota_diagnostic_pro.database.vehicle_manager import VehicleManager

tuning_mgr = TuningManager()
vehicle_mgr = VehicleManager()

def render_ecu_tuner():
    st.header("🎛️ ECU Map Tuner (Real-time)")
    
    if 'simulator' not in st.session_state or not st.session_state.get('obd_active', False):
        st.warning("⚠️ กรุณาเชื่อมต่อ OBD ในเมนู 'Live OBD' ก่อนเริ่มการจูน")
        return

    simulator = st.session_state.simulator
    user_id = st.session_state.user['id']
    
    # Version Control Section in Sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("📁 Version Control")
        
        vehicles = vehicle_mgr.get_user_vehicles(user_id)
        if vehicles:
            v_options = {f"{v['model']} ({v['vin']})": v for v in vehicles}
            selected_v_label = st.selectbox("เลือกรถสำหรับการจูน", list(v_options.keys()))
            selected_vehicle = v_options[selected_v_label]
            vehicle_id = selected_vehicle['id']
            
            st.info(f"🚗 **ข้อมูลรถ:**\n- รุ่น: {selected_vehicle['model']}\n- เครื่องยนต์: {selected_vehicle['engine_type']}\n- ปี: {selected_vehicle['year']}")
            
            if st.button("🚀 Load Model Defaults", help="โหลดค่าเริ่มต้นสำหรับรุ่นรถนี้"):
                simulator.load_vehicle_defaults(selected_vehicle['model'], selected_vehicle['engine_type'])
                st.success(f"โหลดค่าเริ่มต้นของ {selected_vehicle['model']} สำเร็จ!")
                st.rerun()

            # Save Current Version
            with st.expander("💾 Save New Version"):
                v_name = st.text_input("ชื่อเวอร์ชัน (เช่น Stage 1, Eco Mode)")
                if st.button("บันทึกเวอร์ชันปัจจุบัน"):
                    if v_name:
                        success, msg = tuning_mgr.save_version(
                            vehicle_id, 
                            v_name, 
                            simulator.fuel_map, 
                            simulator.ignition_map, 
                            simulator.vvt_intake_map, 
                            simulator.vvt_exhaust_map
                        )
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("กรุณาระบุชื่อเวอร์ชัน")
            
            # Load Previous Versions
            st.markdown("---")
            st.subheader("📜 Version History")
            versions = tuning_mgr.get_versions(vehicle_id)
            if versions:
                for v in versions:
                    col_v1, col_v2 = st.columns([3, 1])
                    col_v1.write(f"**{v['version_name']}**\n{v['created_at']}")
                    if col_v2.button("📂", key=f"load_{v['id']}", help="Load this version"):
                        loaded_maps = tuning_mgr.load_version(v['id'])
                        if loaded_maps:
                            simulator.update_fuel_map(loaded_maps['fuel_map'])
                            simulator.update_ignition_map(loaded_maps['ignition_map'])
                            simulator.update_vvt_intake_map(loaded_maps['vvt_intake_map'])
                            simulator.update_vvt_exhaust_map(loaded_maps['vvt_exhaust_map'])
                            st.success(f"โหลดเวอร์ชัน '{v['version_name']}' สำเร็จ!")
                            st.rerun()
                    
                    if st.button("🗑️", key=f"del_{v['id']}", help="Delete this version"):
                        tuning_mgr.delete_version(v['id'])
                        st.success("ลบเวอร์ชันแล้ว")
                        st.rerun()
            else:
                st.info("ยังไม่มีประวัติการจูน")
        else:
            st.warning("กรุณาเพิ่มข้อมูลรถก่อนเริ่มการจูน")

    # Simulation Controls
    with st.sidebar:
        st.markdown("---")
        st.subheader("🕹️ Simulation Controls")
        
        # Speed Control
        sim_speed = st.slider("Simulation Speed", 0.1, 5.0, simulator.simulation_speed, 0.1)
        simulator.set_speed(sim_speed)
        
        # Play/Pause
        is_paused = simulator.pause_event.is_set()
        if st.button("⏸️ Pause" if not is_paused else "▶️ Resume"):
            if is_paused:
                simulator.resume()
            else:
                simulator.pause()
            st.rerun()
            
        # Step Control (Only if paused)
        if is_paused:
            if st.button("⏭️ Step Frame"):
                simulator.step()
                st.rerun()
                
        # Reset to Defaults
        if st.button("🔄 Reset to Defaults"):
            simulator.reset_to_defaults()
            st.success("รีเซ็ตค่าเริ่มต้นเรียบร้อยแล้ว")
            st.rerun()

    # Get current maps from simulator
    current_fuel_map = simulator.fuel_map
    current_ign_map = simulator.ignition_map
    current_vvt_in_map = simulator.vvt_intake_map
    current_vvt_ex_map = simulator.vvt_exhaust_map

    tab1, tab2, tab3, tab4 = st.tabs([
        "⛽ Fuel Map", 
        "🔥 Ignition Map", 
        "🌀 VVT Intake", 
        "🌀 VVT Exhaust"
    ])

    with tab1:
        st.subheader("Fuel Map Tuning")
        st.write("ปรับแต่งค่าสัมประสิทธิ์การฉีดน้ำมัน (1.0 = ปกติ, >1.0 = หนา, <1.0 = บาง)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Editable Dataframe
            edited_fuel_map = st.data_editor(
                current_fuel_map,
                use_container_width=True,
                key="fuel_map_editor"
            )
            
            if st.button("💾 Apply Fuel Map", key="apply_fuel"):
                simulator.update_fuel_map(edited_fuel_map)
                st.success("อัปเดต Fuel Map ไปยัง ECU แล้ว!")

        with col2:
            # 3D Surface Plot
            fig = go.Figure(data=[go.Surface(
                z=edited_fuel_map.values, 
                x=edited_fuel_map.columns, 
                y=edited_fuel_map.index,
                colorscale='Viridis'
            )])
            fig.update_layout(
                title='Fuel Map Surface', 
                scene=dict(
                    xaxis_title='Load (%)',
                    yaxis_title='RPM',
                    zaxis_title='Multiplier'
                ),
                margin=dict(l=0, r=0, b=0, t=30)
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Ignition Map Tuning")
        st.write("ปรับแต่งองศาจุดระเบิด (Degrees Advance)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Editable Dataframe
            edited_ign_map = st.data_editor(
                current_ign_map,
                use_container_width=True,
                key="ign_map_editor"
            )
            
            if st.button("💾 Apply Ignition Map", key="apply_ign"):
                simulator.update_ignition_map(edited_ign_map)
                st.success("อัปเดต Ignition Map ไปยัง ECU แล้ว!")

        with col2:
            # 3D Surface Plot
            fig_ign = go.Figure(data=[go.Surface(
                z=edited_ign_map.values, 
                x=edited_ign_map.columns, 
                y=edited_ign_map.index,
                colorscale='Hot'
            )])
            fig_ign.update_layout(
                title='Ignition Map Surface', 
                scene=dict(
                    xaxis_title='Load (%)',
                    yaxis_title='RPM',
                    zaxis_title='Advance (Deg)'
                ),
                margin=dict(l=0, r=0, b=0, t=30)
            )
            st.plotly_chart(fig_ign, use_container_width=True)

    with tab3:
        st.subheader("VVT Intake Map Tuning")
        st.write("ปรับแต่งองศาแคมชาร์ฟฝั่งไอดี (Intake Cam Advance)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            edited_vvt_in_map = st.data_editor(
                current_vvt_in_map,
                use_container_width=True,
                key="vvt_in_map_editor"
            )
            
            if st.button("💾 Apply VVT Intake Map", key="apply_vvt_in"):
                simulator.update_vvt_intake_map(edited_vvt_in_map)
                st.success("อัปเดต VVT Intake Map เรียบร้อย!")

        with col2:
            fig_vvt_in = go.Figure(data=[go.Surface(
                z=edited_vvt_in_map.values, 
                x=edited_vvt_in_map.columns, 
                y=edited_vvt_in_map.index,
                colorscale='YlGnBu'
            )])
            fig_vvt_in.update_layout(
                title='VVT Intake Map Surface', 
                scene=dict(xaxis_title='Load (%)', yaxis_title='RPM', zaxis_title='Advance (Deg)'),
                margin=dict(l=0, r=0, b=0, t=30)
            )
            st.plotly_chart(fig_vvt_in, use_container_width=True)

    with tab4:
        st.subheader("VVT Exhaust Map Tuning")
        st.write("ปรับแต่งองศาแคมชาร์ฟฝั่งไอเสีย (Exhaust Cam Retard)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            edited_vvt_ex_map = st.data_editor(
                current_vvt_ex_map,
                use_container_width=True,
                key="vvt_ex_map_editor"
            )
            
            if st.button("💾 Apply VVT Exhaust Map", key="apply_vvt_ex"):
                simulator.update_vvt_exhaust_map(edited_vvt_ex_map)
                st.success("อัปเดต VVT Exhaust Map เรียบร้อย!")

        with col2:
            fig_vvt_ex = go.Figure(data=[go.Surface(
                z=edited_vvt_ex_map.values, 
                x=edited_vvt_ex_map.columns, 
                y=edited_vvt_ex_map.index,
                colorscale='Portland'
            )])
            fig_vvt_ex.update_layout(
                title='VVT Exhaust Map Surface', 
                scene=dict(xaxis_title='Load (%)', yaxis_title='RPM', zaxis_title='Retard (Deg)'),
                margin=dict(l=0, r=0, b=0, t=30)
            )
            st.plotly_chart(fig_vvt_ex, use_container_width=True)

    # Real-time Feedback Section
    st.markdown("---")
    st.subheader("📊 Real-time Feedback")
    
    # Live data display to see effect
    data = simulator.get_data()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RPM", f"{data.get('RPM', 0)}")
    c2.metric("Load", f"{data.get('ENGINE_LOAD', 0):.1f} %")
    c3.metric("Injector PW", f"{data.get('INJECTOR_PW', 0):.2f} ms")
    c4.metric("Ignition Timing", f"{data.get('IGNITION_TIMING', 0):.1f} °")
    
    c5, c6, c7 = st.columns(3)
    c5.metric("STFT (Fuel Trim)", f"{data.get('FUEL_TRIM_ST', 0):.1f} %", 
             delta_color="inverse" if abs(data.get('FUEL_TRIM_ST', 0)) > 10 else "normal")
    c6.metric("VVT Intake", f"{data.get('VVT_INTAKE_ANGLE_DIFF', 0):.1f} °")
    c7.metric("VVT Exhaust", f"{data.get('VVT_EXHAUST_ANGLE_DIFF', 0):.1f} °")
    
    st.info("💡 ลองปรับค่าในตารางแล้วกด Apply เพื่อดูผลลัพธ์ที่เปลี่ยนไปทันที")
