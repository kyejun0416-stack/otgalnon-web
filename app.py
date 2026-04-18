import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 아키텍처 설정
# ==========================================
st.set_page_config(page_title="OTGALNON v4.5", layout="wide")

# 사이드바에서 현재 사용 가능한 모델 리스트 확인 기능 추가
def get_available_models():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return []
    genai.configure(api_key=api_key)
    return [m.name.replace('models/', '') for m in genai.list_models()]

# ==========================================
# 2. 하이퍼 추론 엔진 (Gemini 3.1 Flash)
# ==========================================
def run_otgalnon_engine(user_input, selected_model):
    api_key = st.secrets.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    try:
        # 정확한 모델명으로 인스턴스 생성
        model = genai.GenerativeModel(
            model_name=selected_model,
            system_instruction=(
                "당신은 OTGALNON의 최고 분석관입니다. "
                "이모티콘을 금지하며, 제1원리 추론(First Principles Thinking)에 기반해 답변하십시오. "
                "모든 분석은 논리적 근거와 함께 데이터 중심으로 서술하십시오."
            )
        )
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"CRITICAL ENGINE FAILURE: {str(e)}"

# ==========================================
# 3. 메인 인터페이스
# ==========================================
with st.sidebar:
    st.markdown("### SYSTEM MONITOR")
    # 모델 자동 감지 및 선택
    available_models = get_available_models()
    # 스크린샷의 모델이 있으면 우선 선택, 없으면 최신 Flash 선택
    default_model = 'gemini-3.1-flash-preview'
    if 'gemini-3.1-flash-live-preview' in available_models:
        default_model = 'gemini-3.1-flash-live-preview'
        
    target_model = st.selectbox("ACTIVE MODEL", available_models, index=available_models.index(default_model) if default_model in available_models else 0)
    st.info(f"QUOTA TYPE: UNLIMITED (Detected)")
    
    if st.button("REBOOT SYSTEM"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter research command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("PROCESSING THROUGH HYPER-NEURAL NETWORK..."):
            answer = run_otgalnon_engine(prompt, target_model)
            st.markdown(answer)
            st.code(answer, language="markdown")
            st.session_state.messages.append({"role": "assistant", "content": answer})