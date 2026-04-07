import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 보라색 테마 및 UI 최적화
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { background-color: #1e1e2e !important; color: #ffffff !important; border: 1px solid #4b0082 !important; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #4b0082; color: white; border: none; height: 3.5em; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태 초기화 (메모리 관리용)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 4. 헤더
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("Performance & Logic Optimized")

# 5. 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="전략적 핵심을 입력하십시오.", height=150)
uploaded_file = st.file_uploader("데이터 업로드 (이미지)", type=["jpg", "jpeg", "png"])

# 6. API 및 모델 설정 (안정성 우선)
api_key = st.secrets.get("GEMINI_API_KEY")
model_name = "gemini-1.5-flash" # 가장 가볍고 빠른 모델로 고정

with st.sidebar:
    st.title("System Monitor")
    # 현재 메모리에 쌓인 대화 수 표시
    st.write(f"Stored Memory: {len(st.session_state.chat_history) // 2} turns")
    if st.button("Purge Memory"):
        st.session_state.chat_history = []
        st.rerun()
    st.divider()
    st.caption("v8.0 | Zero-Latency Patch")

# 7. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("API Key Missing.")
    elif not user_input and not uploaded_file:
        st.warning("Input required.")
    else:
        with st.spinner("Processing with High-Speed Core..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                
                # 시스템 지침 경량화 (AI의 사고 프로세스 단축)
                instr = "당신은 '오트가논'입니다. 쉽고 명확한 [단계별 전략]으로 핵심만 답하세요."
                
                # [해결책 1] 슬라이딩 윈도우: 최근 4개 대화(유저2, 모델2)만 서버로 전송
                # 이를 통해 페이로드를 줄여 타임아웃을 근본적으로 방지합니다.
                optimized_history = st.session_state.chat_history[-4:]
                
                contents = []
                for chat in optimized_history:
                    contents.append({"role": chat["role"], "parts": [{"text": chat["text"]}]})
                
                # [해결책 2] 현재 요청 구성
                current_parts = [{"text": f"{instr}\nTask: {user_input}"}]
                
                # 이미지는 현재 요청에만 포함 (과거 기록의 이미지는 전송 안 함)
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    current_parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": img_data}})
                
                contents.append({"role": "user", "parts": current_parts})
                
                # API 호출 (최적화된 페이로드 전송)
                response = requests.post(url, json={"contents": contents}, timeout=45)
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    # 메모리 저장
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    st.session_state.chat_history.append({"role": "model", "text": answer})
                    
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    st.divider()
                    st.code(re.sub(r'[*#\-`>]', '', answer).strip(), language=None)
                else:
                    st.error("서버 응답 오류: 데이터량을 줄여 다시 시도해 주세요.")
                    
            except Exception as e:
                st.error(f"Engine Failure: {e}")

st.divider()
st.caption("© 2026 otgalnon. Performance architecture applied.")