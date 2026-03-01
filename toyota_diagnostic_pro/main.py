import streamlit as st
import time
from toyota_diagnostic_pro.database.auth_manager import AuthManager
from toyota_diagnostic_pro.gui.dashboard import render_dashboard

auth = AuthManager()

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://picsum.photos/seed/toyota_tech/400/200", caption="Toyota Diagnostic Pro", use_container_width=True)
        st.title("🔐 เข้าสู่ระบบ")
        
        tab1, tab2 = st.tabs(["เข้าสู่ระบบ", "ลงทะเบียน"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("ชื่อผู้ใช้")
                password = st.text_input("รหัสผ่าน", type="password")
                submit = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True)
                
                if submit:
                    if username and password:
                        success, res = auth.login_user(username, password)
                        if success:
                            st.session_state.user = res
                            st.success(f"ยินดีต้อนรับคุณ {username}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res)
                    else:
                        st.warning("กรุณากรอกชื่อผู้ใช้และรหัสผ่าน")
                    
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("ชื่อผู้ใช้ใหม่")
                new_pass = st.text_input("รหัสผ่านใหม่", type="password")
                confirm_pass = st.text_input("ยืนยันรหัสผ่าน", type="password")
                new_email = st.text_input("อีเมล (ไม่บังคับ)")
                submit_reg = st.form_submit_button("ลงทะเบียน", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass and confirm_pass:
                        if new_pass != confirm_pass:
                            st.error("รหัสผ่านไม่ตรงกัน")
                        elif len(new_pass) < 4:
                            st.error("รหัสผ่านต้องมีความยาวอย่างน้อย 4 ตัวอักษร")
                        else:
                            success, msg = auth.register_user(new_user, new_pass, new_email)
                            if success:
                                st.success(msg)
                                st.info("กรุณาเข้าสู่ระบบด้วยบัญชีใหม่ของคุณ")
                            else:
                                st.error(msg)
                    else:
                        st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

def main():
    st.set_page_config(page_title="Toyota Diagnostic Pro", layout="wide")
    
    if 'user' not in st.session_state:
        login_page()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
