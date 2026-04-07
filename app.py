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
    code { color: #bf94ff !important; background-color: #16161d !important; }
    </style>
    """, unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 3. 헤더
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("Strategic Insight & Multi-Model Engine")

st.divider()

# 4. 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="내용을 입력하세요.", height=150)
uploaded_file = st.file_uploader("이미지 데이터", type=["jpg", "jpeg", "png"])

# 5. API 및 모델 라우팅 (중요!)
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.title("Fuel Gauge (Quota)")
    # 대시보드에서 확인한 할당량 넉넉한 모델들 추가
    model_choice = st.selectbox(
        "Select Engine", 
        ["gemini-2.5-flash", "gemini-2-flash", "gemini-3-flash", "gemini-1.5-flash"],
        index=0,
        help="특정 모델의 할당량(RPD)이 소진되면 다른 모델로 변경하세요."
    )
    if st.button("Clear Memory"):
        st.session_state.chat_history = []
        st.rerun()
    st.divider()
    st.caption(f"Active Engine: {model_choice}")
    st.caption("v9.0 | Multi-Model Routing")

# 6. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("API Key missing.")
    elif not user_input and not uploaded_file:
        st.warning("No input data.")
    else:
        with st.spinner(f"Refueling with {model_choice}..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
                instr = "당신은 '오트가논'입니다. 쉬운 단어로 [단계별 전략]을 명확히 답하세요."
                
                # 최적화된 대화 기록 (최근 2회분)
                contents = []
                for chat in st.session_state.chat_history[-4:]:
                    contents.append({"role": chat["role"], "parts": [{"text": chat["text"]}]})
                
                current_parts = [{"text": f"{instr}\nTask: {user_input}"}]
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    current_parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": img_data}})
                
                contents.append({"role": "user", "parts": current_parts})
                
                # API 호출
                response = requests.post(url, json={"contents": contents}, timeout=60)
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    st.session_state.chat_history.append({"role": "model", "text": answer})
                    
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    st.divider()
                    st.code(re.sub(r'[*#\-`>]', '', answer).strip(), language=None)
                else:
                    err_msg = res_json.get('error', {}).get('message', 'Quota Exceeded')
                    st.error(f"Engine Out of Fuel: {err_msg}")
                    st.info("💡 사이드바에서 다른 모델(Gemini 2.5 등)을 선택해 보세요.")
            except Exception as e:
                st.error(f"Critical System Failure: {e}")

st.divider()
st.caption("© 2026 otgalnon. Resilience optimized.")