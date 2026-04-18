import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. 시스템 설정 및 테마 (이모티콘 완전 배제)
# ==========================================
st.set_page_config(
    page_title="OTGALNON v4.1 - Hyper Intelligence",
    layout="wide"
)

# OTGALNON 전용 다크 보라 테마
st.markdown("""
    <style>
    .main { background-color: #0b091a; color: #d1d1d1; }
    [data-testid="stSidebar"] { background-color: #0e0c1f; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid #4b3d8f; border-radius: 12px !important; }
    .stButton>button { background: linear-gradient(45deg, #4b3d8f, #6d5dfc); color: white; border: none; font-weight: 600; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 세션 및 메모리 관리
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 3. Gemini 3 Flash 추론 엔진
# ==========================================
def run_gemini3_engine(user_input):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "CRITICAL ERROR: API Key가 감지되지 않았습니다. Secrets를 확인하십시오."

    try:
        genai.configure(api_key=api_key)
        
        # 사용자님의 요청에 따라 Gemini 3 Flash 모델 강제 지정
        # 최신 SDK에서는 'gemini-3-flash' 명칭을 사용합니다.
        model = genai.GenerativeModel(
            model_name='gemini-3-flash',
            system_instruction=(
                "당신은 OTGALNON의 하이퍼 분석 엔진입니다. "
                "텍스트에서 모든 이모티콘을 엄격히 배제하십시오. "
                "사용자의 질문에 대해 제1원리 추론을 바탕으로 전문적이고 구조적인 해답을 제시하십시오. "
                "답변은 보고서 형식(분석-추론-결론)으로 출력하십시오."
            )
        )
        
        # 추론 실행
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        # 모델명 호환성 체크 (과도기적 명칭 대응)
        if "404" in str(e):
            return "ERROR: 현재 API 버전에서 'gemini-3-flash' 모델명을 찾을 수 없습니다. SDK 업데이트를 확인하십시오."
        return f"ENGINE ERROR: {str(e)}"

# ==========================================
# 4. 메인 컨트롤 인터페이스
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    st.markdown("<h3 style='text-align: center;'>OTGALNON v4.1</h3>", unsafe_allow_html=True)
    st.write("CORE: **Gemini 3 Flash**")
    st.divider()
    if st.button("RESET WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

# 히스토리 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력 처리
if prompt := st.chat_input("Enter research command..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("PERFORMING NEURAL ANALYSIS..."):
            answer = run_gemini3_engine(prompt)
            st.markdown(answer)
            # 전문가용 데이터 복사 코드 블록
            st.code(answer, language="markdown")

    st.session_state.messages.append({"role": "assistant", "content": answer})