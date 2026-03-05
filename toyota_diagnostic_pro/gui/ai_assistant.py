import streamlit as st
import os
import base64
from google import genai
from google.genai import types

def render_ai_assistant():
    st.header("🤖 AI Diagnostic Assistant")
    st.write("สอบถามข้อมูลการซ่อม วิเคราะห์อาการเสีย หรือขอคำแนะนำจาก AI ผู้เชี่ยวชาญ")

    # Initialize Gemini Client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ ไม่พบ GEMINI_API_KEY ในระบบ กรุณาตรวจสอบการตั้งค่า")
        return

    client = genai.Client(api_key=api_key)

    # Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "audio" in message:
                st.audio(message["audio"], format="audio/wav")

    # Chat Input
    if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("AI กำลังคิด..."):
                try:
                    # Text Response
                    response = client.models.generate_content(
                        model="gemini-3.1-pro-preview",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="คุณคือผู้เชี่ยวชาญด้านการซ่อมรถยนต์ Toyota โดยเฉพาะระบบ OBD-II และ CAN Bus ให้คำแนะนำที่แม่นยำและเป็นมืออาชีพ"
                        )
                    )
                    assistant_text = response.text
                    st.markdown(assistant_text)

                    # TTS Response
                    with st.spinner("กำลังสร้างเสียง..."):
                        tts_response = client.models.generate_content(
                            model="gemini-2.5-flash-preview-tts",
                            contents=f"Say cheerfully in Thai: {assistant_text[:200]}", # Limit length for TTS demo
                            config=types.GenerateContentConfig(
                                response_modalities=["AUDIO"],
                                speech_config=types.SpeechConfig(
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                                    )
                                )
                            )
                        )
                        
                        audio_data = None
                        for part in tts_response.candidates[0].content.parts:
                            if part.inline_data:
                                audio_data = part.inline_data.data
                                break
                        
                        if audio_data:
                            audio_bytes = base64.b64decode(audio_data)
                            st.audio(audio_bytes, format="audio/wav")
                            st.session_state.chat_history.append({
                                "role": "assistant", 
                                "content": assistant_text,
                                "audio": audio_bytes
                            })
                        else:
                            st.session_state.chat_history.append({
                                "role": "assistant", 
                                "content": assistant_text
                            })

                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {str(e)}")

    # Clear Chat
    if st.button("🗑️ ล้างการสนทนา"):
        st.session_state.chat_history = []
        st.rerun()
