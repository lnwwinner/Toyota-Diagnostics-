import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_ecu_tuner():
    st.header("🎛️ ECU Map Tuner (Real-time)")
    
    if 'simulator' not in st.session_state or not st.session_state.get('obd_active', False):
        st.warning("⚠️ กรุณาเชื่อมต่อ OBD ในเมนู 'Live OBD' ก่อนเริ่มการจูน")
        return

    simulator = st.session_state.simulator
    
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

    tab1, tab2 = st.tabs(["⛽ Fuel Map (Injection Multiplier)", "🔥 Ignition Map (Timing Advance)"])

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
    
    c5, c6 = st.columns(2)
    c5.metric("STFT (Fuel Trim)", f"{data.get('FUEL_TRIM_ST', 0):.1f} %", 
             delta_color="inverse" if abs(data.get('FUEL_TRIM_ST', 0)) > 10 else "normal")
    
    st.info("💡 ลองปรับค่าในตารางแล้วกด Apply เพื่อดูผลลัพธ์ที่เปลี่ยนไปทันที")
