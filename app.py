import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 보라색 테마 디자인
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { background-color: #1e1e2e !important; color: #ffffff !important; border: 1px solid #4b0082 !important; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #4b0082; color: white; border: none; height: 3.5em; }
    .stButton button:hover { background-color: #6a0dad; box-shadow: 0 0 20px #6a0dad; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    [data-testid="stImage"] { margin-bottom: -35px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태(대화 기록) 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. 헤더 섹션
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("Strategic Insight & Memory Engine")

st.divider()

# 5. 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="이전 대화 내용을 기억합니다. 이어서 질문해 보세요.", height=150)
uploaded_file = st.file_uploader("이미지 데이터 업로드", type=["jpg", "jpeg", "png"])

# 6. API 및 모델 설정
api_key = st.secrets.get("GEMINI_API_KEY")
model_name = "gemini-flash-latest"

# 사이드바: 대화 초기화 버튼 추가
with st.sidebar:
    st.title("Memory Control")
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.success("대화 기록이 초기화되었습니다.")
    st.divider()
    st.caption(f"Model: {model_name}")
    st.caption("v7.0 | Long-term Memory Mode")

# 7. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("시스템 오류: API Key가 없습니다.")
    elif not user_input and not uploaded_file:
        st.warning("데이터를 입력하십시오.")
    else:
        with st.spinner("Accessing Memory & Logic..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                
                system_instruction = (
                    "당신은 '오트가논' 엔진입니다. "
                    "쉬운 단어를 사용해 논리적으로 설명하며, 이모티콘은 사용하지 마세요. "
                    "이전 대화 맥락이 주어지면 이를 참고하여 답변하십시오."
                )
                
                # [핵심] 대화 기록 구조화 (Gemini API 형식)
                contents = []
                
                # 1. 과거 기록 추가
                for chat in st.session_state.chat_history:
                    contents.append({"role": chat["role"], "parts": [{"text": chat["text"]}]})
                
                # 2. 현재 사용자 입력 추가 (시스템 지침 포함)
                current_parts = [{"text": f"{system_instruction}\n\nTask: {user_input}"}]
                
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    current_parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": img_data}})
                
                contents.append({"role": "user", "parts": current_parts})
                
                # API 호출
                response = requests.post(url, json={"contents": contents}, timeout=60)
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    # [핵심] 세션 상태에 대화 내용 저장
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    st.session_state.chat_history.append({"role": "model", "text": answer})
                    
                    st.markdown("### Strategic Output")
                    st