import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 페이지 및 테마 설정
# ==========================================
st.set_page_config(page_title="OTGALNON", page_icon="logo.png", layout="wide")

# UI/UX 최적화 커스텀 CSS (아바타 강제 숨김 및 여백 완벽 제거)
st.markdown("""
    <style>
    /* 1. 아바타 관련 모든 요소를 추적하여 강제로 숨기고 영역을 0으로 만듦 */
    [data-testid="stChatMessageAvatar"],
    .stChatMessageAvatar,
    div[data-testid="chatAvatarIcon-user"],
    div[data-testid="chatAvatarIcon-assistant"] {
        display: none !important;
        width: 0px !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* 2. 대화창 메시지 패딩 및 아이콘 빈자리(여백) 완전 제거 */
    [data-testid="stChatMessage"] {
        padding: 1rem 0 !important;
        gap: 0rem !important;
    }
    
    /* 3. 텍스트가 시작되는 콘텐츠 영역을 왼쪽 끝으로 밀착 */
    [data-testid="stChatMessageContent"] {
        margin-left: 0px !important;
        padding-left: 0.5rem !important;
    }
    
    /* 4. 사이드바 이미지 중앙 정렬 및 코드 블록 색상 */
    [data-testid="stSidebar"] img {
        margin-bottom: 2rem;
        border-radius: 8px;
    }
    code {
        color: #b39ddb !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 시스템 엔진 초기화 (무제한 쿼터 자동 탐지)
# ==========================================
def initialize_otgalnon():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API Key Missing"
    
    genai.configure(api_key=api_key)
    try:
        model_list = [m.name for m in genai.list_models()]
        # 시스템 내부 식별자를 자동으로 찾아 연결
        target = next((m for m in model_list if "gemini-3-flash" in m), "models/gemini-1.5-flash")
        
        model = genai.GenerativeModel(
            model_name=target,
            system_instruction=(
                "당신은 OTGALNON의 최고 분석관입니다. "
                "이모티콘 사용을 엄격히 금지하며, 제1원리 추론에 기반해 논리적으로 답변하십시오. "
                "코딩 스크립트 작성 시에는 주석과 함께 최적화된 코드를 제공하십시오."
            )
        )
        return model, target
    except Exception as e:
        return None, str(e)

engine, active_id = initialize_otgalnon()

# ==========================================
# 3. 사이드바 컨트롤 패널
# ==========================================
with st.sidebar:
    try:
        st.image("logo.png", use_column_width=True)
    except:
        # 로고 파일이 없을 경우 텍스트로 대체
        st.markdown("<h2 style='color: #6d5dfc; text-align: center; margin-bottom: 2rem;'>OTGALNON</h2>", unsafe_allow_html=True)
    
    st.markdown("### SYSTEM STATUS")
    if engine:
        st.success("ONLINE")
        st.caption("Engine Connected")
    else:
        st.error("OFFLINE")
    
    if st.button("RESET WORKSPACE", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 4. 메인 챗봇 인터페이스 (텍스트 중심)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 렌더링 (아바타 없이 깔끔하게 출력됨)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 5. 명령 입력 및 추론 로직
# ==========================================
if prompt := st.chat_input("명령을 입력하십시오..."):
    # 사용자 메시지
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 분석관 응답
    with st.chat_message("assistant"):
        if engine:
            with st.spinner("분석 중..."):
                try:
                    response = engine.generate_content(prompt)
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"시스템 오류: {str(e)}")
        else:
            st.warning("엔진 연결을 확인하십시오.")