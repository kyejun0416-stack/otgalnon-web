import streamlit as st
from google import genai
import os

# ==========================================
# 1. 아키텍처 설정
# ==========================================
st.set_page_config(page_title="OTGALNON v5.2", layout="wide")

# 사이드바: 모델 자동 탐지 로직
def initialize_engine():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API 키가 없습니다."
    
    try:
        client = genai.Client(api_key=api_key)
        # 현재 접근 가능한 모든 모델 리스트 확보
        available_models = [m.name for m in client.models.list()]
        
        # 'gemini-3-flash'가 포함된 가장 정확한 ID 찾기
        target_id = next((m for m in available_models if "gemini-3-flash" in m), None)
        
        if not target_id:
            # 3버전이 없으면 1.5 버전이라도 탐색
            target_id = next((m for m in available_models if "gemini-1.5-flash" in m), "gemini-1.5-flash")
            
        return client, target_id
    except Exception as e:
        return None, str(e)

client, active_model_id = initialize_engine()

# ==========================================
# 2. 메인 컨트롤 센터 UI
# ==========================================
with st.sidebar:
    st.markdown("### SYSTEM STATUS")
    if client:
        st.success(f"ACTIVE ID: {active_model_id}")
        st.caption("시스템이 정확한 식별자를 자동으로 탐지했습니다.")
    else:
        st.error("엔진 연결 실패")
    
    if st.button("RESET WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 로그 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력 처리
if prompt := st.chat_input("연구 명령을 입력하십시오..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if client:
            with st.spinner("HYPER-ANALYSIS IN PROGRESS..."):
                try:
                    response = client.models.generate_content(
                        model=active_model_id,
                        contents=prompt,
                        config={"system_instruction": "당신은 OTGALNON의 분석관입니다. 이모티콘 금지, 논리적 답변 필수."}
                    )
                    answer = response.text
                    st.markdown(answer)
                    st.code(answer, language="markdown")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"RUNTIME ERROR: {str(e)}")
        else:
            st.warning("엔진이 준비되지 않았습니다. API 설정을 확인하십시오.")

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