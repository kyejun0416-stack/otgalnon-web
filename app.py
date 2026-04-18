import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 아키텍처 설정 (함수 선언을 최상단으로 이동)
# ==========================================
st.set_page_config(page_title="OTGALNON v5.5", layout="wide")

def get_accurate_engine():
    """사용자 계정에서 사용 가능한 Gemini 3 모델 ID를 자동 탐색"""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API Key Missing"
    
    genai.configure(api_key=api_key)
    try:
        # 사용 가능한 모델 리스트 확보
        model_list = [m.name for m in genai.list_models()]
        
        # 1순위: 스크린샷의 Gemini 3 Flash Live 모델 검색
        # 시스템 내부 ID는 보통 'models/gemini-3-flash-live' 형태입니다.
        target = next((m for m in model_list if "gemini-3-flash" in m), None)
        
        if not target:
            target = "models/gemini-1.5-flash" # 대비용
            
        return genai.GenerativeModel(
            model_name=target,
            system_instruction="당신은 OTGALNON 분석 엔진입니다. 이모티콘 금지, 논리적 답변만 제공하십시오."
        ), target
    except Exception as e:
        return None, str(e)

# ==========================================
# 2. 엔진 초기화 (NameError 방지)
# ==========================================
engine, active_id = get_accurate_engine()

# ==========================================
# 3. UI 구성
# ==========================================
with st.sidebar:
    st.markdown("### SYSTEM STATUS")
    if engine:
        st.success(f"ONLINE: {active_id}")
        st.caption("UI의 'Gemini 3 Flash'를 시스템 ID로 변환 완료")
    else:
        st.error(f"OFFLINE: {active_id}")
    
    if st.button("RESET"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if engine:
            with st.spinner("ANALYZING..."):
                try:
                    response = engine.generate_content(prompt)
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"ENGINE ERROR: {str(e)}")
        else:
            st.warning("엔진 연결을 확인하십시오.")