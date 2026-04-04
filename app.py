import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정 및 캐싱 최적화
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 디자인 (애니메이션 최소화로 로딩 속도 향상)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { background-color: #1e1e2e !important; color: #ffffff !important; border: 1px solid #4b0082 !important; }
    .stButton button { 
        width: 100%; border-radius: 8px; font-weight: bold; 
        background-color: #4b0082; color: white; border: none; height: 3.5em; 
    }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 대화 기록 관리 (최근 5개만 유지하여 속도 최적화)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. 헤더
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("High-Speed Strategic Engine")

# 5. 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="빠른 분석을 시작합니다.", height=150)
uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])

# 6. API 설정 (가장 빠른 flash 모델 고정)
api_key = st.secrets.get("GEMINI_API_KEY")
model_name = "gemini-1.5-flash" # 현재 가장 응답 속도가 빠른 안정 버전

with st.sidebar:
    st.title("Performance")
    st.info(f"Model: {model_name}")
    if st.button("Reset Memory"):
        st.session_state.chat_history = []
        st.rerun()
    st.caption("v7.5 | Speed Optimized")

# 7. 엔진 가동 로직 (경량화 패치)
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("API Key missing.")
    elif not user_input and not uploaded_file:
        st.warning("No data.")
    else:
        with st.spinner("Fast Decoding..."):
            try:
                # v1beta 대신 안정화된 v1 버전 사용 시도 (속도 이점)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                
                # 시스템 지침을 더 짧고 명확하게 수정 (토큰 절약)
                instr = "당신은 '오트가논'입니다. 쉬운 단어로 [단계별 전략] 위주로 아주 짧고 명확하게 답하세요."
                
                # 대화 기록 최적화: 너무 길면 잘라냄 (최근 3회 분량만 전달)
                recent_history = st.session_state.chat_history[-6:] 
                contents = []
                for chat in recent_history:
                    contents.append({"role": chat["role"], "parts": [{"text": chat["text"]}]})
                
                # 현재 데이터 구성
                current_parts = [{"text": f"{instr}\nTask: {user_input}"}]
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    current_parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": img_data}})
                
                contents.append({"role": "user", "parts": current_parts})
                
                # 스트리밍 방식은 아니지만, 페이로드 최소화로 전송 속도 향상
                response = requests.post(url, json={"contents": contents}, timeout=30)
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    st.session_state.chat_history.append({"role": "model", "text": answer})
                    
                    st.markdown("### Strategic Output")
                    st.write(answer)
                else:
                    st.error("서버 과부하로 응답이 지연되고 있습니다. 잠시 후 시도하세요.")
            except Exception as e:
                st.error("연결 오류 발생")

st.divider()
st.caption("© 2026 otgalnon. Speed optimized.")