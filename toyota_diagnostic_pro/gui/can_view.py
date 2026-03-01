import streamlit as st
import time
import pandas as pd
import plotly.express as px
from toyota_diagnostic_pro.core.can_reader import CANReader
from toyota_diagnostic_pro.database.vehicle_manager import VehicleManager

vehicle_mgr = VehicleManager()

def render_live_can():
    st.header("📡 Live CAN Bus Data")
    
    # Select Vehicle
    vehicles = vehicle_mgr.get_user_vehicles(st.session_state.user['id'])
    if not vehicles:
        st.warning("กรุณาเพิ่มข้อมูลรถก่อนเริ่มการวินิจฉัย")
        return
        
    v_options = {f"{v['model']} ({v['vin']})": v for v in vehicles}
    selected_label = st.selectbox("เลือกรถที่กำลังตรวจเช็ค (CAN)", list(v_options.keys()))
    selected_vehicle = v_options[selected_label]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 เริ่มการเชื่อมต่อ CAN"):
            st.session_state.can_active = True
            st.session_state.can_reader = CANReader()
            st.session_state.can_reader.connect()
    with col2:
        if st.button("🛑 หยุดการเชื่อมต่อ CAN"):
            st.session_state.can_active = False

    if st.session_state.get('can_active', False):
        # Data history for graphing
        if 'can_history' not in st.session_state:
            st.session_state.can_history = pd.DataFrame()

        placeholder = st.empty()
        graph_placeholder = st.empty()
        
        # Simple loop for live update
        for _ in range(50): # Run for 50 iterations
            if not st.session_state.get('can_active', False):
                break
                
            # Get data from reader
            data = st.session_state.can_reader.get_live_can_data()
            
            # Update history
            new_row = pd.DataFrame([data])
            new_row['Time'] = pd.to_datetime('now')
            st.session_state.can_history = pd.concat([st.session_state.can_history, new_row]).tail(50)

            with placeholder.container():
                st.subheader("📊 Decoded CAN Signals")
                
                # Display metrics in columns
                cols = st.columns(len(data))
                for i, (key, value) in enumerate(data.items()):
                    cols[i].metric(key, f"{value}")

                st.markdown("---")
                
            with graph_placeholder.container():
                st.subheader("📈 CAN Signal Analysis")
                
                # Plot Wheel Speeds
                wheel_cols = [c for c in data.keys() if "WheelSpeed" in c]
                if wheel_cols:
                    fig1 = px.line(st.session_state.can_history, x='Time', y=wheel_cols, 
                                  title='Wheel Speeds (Decoded from CAN)',
                                  labels={'value': 'Speed (km/h)', 'variable': 'Wheel'})
                    st.plotly_chart(fig1, use_container_width=True)

                # Plot Steering Angle
                if "SteeringAngle" in data:
                    fig2 = px.line(st.session_state.can_history, x='Time', y='SteeringAngle',
                                  title='Steering Angle (Decoded from CAN)',
                                  labels={'value': 'Angle (deg)'})
                    st.plotly_chart(fig2, use_container_width=True)
            
            time.sleep(1)
