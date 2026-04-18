import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 페이지 테마 및 파비콘 설정
# ==========================================
# 파비콘을 logo.png로 교체하고 레이아웃을 와이드로 설정
st.set_page_config(page_title="OTGALNON", page_icon="logo.png", layout="wide")

# 모던 챗봇 스타일을 위한 커스텀 CSS 주입
st.markdown("""
    <style>
    /* 1. 기본 아바타(로봇, 사람 아이콘) 숨기기 */
    div[data-testid="stChatMessageAvatar"] {
        display: none !important;
    }
    
    /* 2. 대화창 메시지 패딩 조절 (아바타가 없어진 공간 최적화) */
    div[data-testid="stChatMessage"] {
        padding: 1rem 0;
        gap: 1rem;
    }
    
    /* 3. 사이드바 이미지 중앙 정렬 및 여백 최적화 */
    [data-testid="stSidebar"] img {
        margin-bottom: 2rem;
        border-radius: 8px;
    }
    
    /* 4. 코드 블록 및 UI 요소에 보라색 포인트 적용 */
    code {
        color: #b39ddb !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 시스템 엔진 초기화
# ==========================================
def initialize_otgalnon():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API Key Missing"
    
    genai.configure(api_key=api_key)
    try:
        model_list = [m.name for m in genai.list_models()]
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
# 3. 사이드바 UI (미니멀리즘 적용)
# ==========================================
with st.sidebar:
    # 버전 텍스트 삭제 및 logo.png 배치
    try:
        st.image("logo.png", use_column_width=True)
    except:
        st.markdown("<h2 style='color: #6d5dfc; text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    
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
# 4. 메인 챗봇 인터페이스
# ==========================================
# 상단 타이틀 숨김 처리 (챗봇 본연의 기능에 집중)
# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 렌더링
for msg in st.session_state.messages:
    # CSS로 인해 아바타는 보이지 않고 텍스트만 깔끔하게 출력됨
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 5. 명령 입력 및 추론
# ==========================================
if prompt := st.chat_input("메시지를 입력하십시오..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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