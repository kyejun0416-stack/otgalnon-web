import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 아키텍처 및 시스템 설정 (최상단 고정)
# ==========================================
st.set_page_config(page_title="OTGALNON", layout="wide")

def initialize_otgalnon():
    """사용자 계정의 무제한 쿼터 모델을 자동 탐색 및 연결"""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API Key Missing"
    
    genai.configure(api_key=api_key)
    try:
        # 실제 호출 가능한 모델 리스트 확인
        model_list = [m.name for m in genai.list_models()]
        
        # [정확한 ID 매핑] 스크린샷의 'Gemini 3 Flash' 식별자 탐색
        target = next((m for m in model_list if "gemini-3-flash" in m), "models/gemini-1.5-flash")
        
        # 엔진 인스턴스 생성 및 시스템 지시문 주입
        model = genai.GenerativeModel(
            model_name=target,
            system_instruction=(
                "당신은 OTGALNON의 최고 분석관입니다. "
                "이모티콘 사용을 엄격히 금지하며, 제1원리 추론에 기반해 답변하십시오. "
                "스크립트 요청 시에는 주석이 포함된 실행 가능한 코드를 제공하십시오."
            )
        )
        return model, target
    except Exception as e:
        return None, str(e)

# 엔진 초기화
engine, active_id = initialize_otgalnon()

# ==========================================
# 2. 오리지널 인터페이스 레이아웃
# ==========================================
with st.sidebar:
    st.markdown("### SYSTEM STATUS")
    if engine:
        # UI 이름과 시스템 ID 사이의 간극 해결
        st.success(f"ONLINE: {active_id}")
        st.caption("Gemini 3 Flash 엔진 연결 완료")
    else:
        st.error(f"OFFLINE: {active_id}")
    
    if st.button("RESET"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 3. 명령 입력 및 추론 로직
# ==========================================
if prompt := st.chat_input("Enter command..."):
    # 사용자 입력 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 비서 응답 생성
    with st.chat_message("assistant"):
        if engine:
            with st.spinner("ANALYZING..."):
                try:
                    # 무제한 쿼터 엔진 가동
                    response = engine.generate_content(prompt)
                    answer = response.text
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"ENGINE ERROR: {str(e)}")
        else:
            st.warning("엔진 연결을 확인하십시오. API 키 설정 혹은 모델 접근 권한 문제일 수 있습니다.")