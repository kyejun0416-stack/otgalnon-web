import streamlit as st
from ai_engine import initialize_otgalnon
from ppt_maker import parse_text_to_ppt
from chat_history import load_history, save_history, clear_history

# ==========================================
# 1. 페이지 및 UI 설정
# ==========================================
st.set_page_config(page_title="OTGALNON", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
    [data-testid="stChatMessageAvatar"], .stChatMessageAvatar, div[data-testid^="chatAvatarIcon"] { display: none !important; width: 0!important; height: 0!important; margin: 0!important; padding: 0!important; }
    [data-testid="stChatMessage"] { padding: 1rem 0 !important; gap: 0rem !important; }
    [data-testid="stChatMessageContent"] { margin-left: 0px !important; padding-left: 0.5rem !important; }
    [data-testid="stSidebar"] img { margin-bottom: 2rem; border-radius: 8px; }
    code { color: #b39ddb !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 시스템 초기화 및 사이드바
# ==========================================
engine, active_id = initialize_otgalnon()

with st.sidebar:
    try:
        st.image("logo.png", use_column_width=True)
    except:
        st.markdown("<h2 style='color:#6d5dfc; text-align:center;'>OTGALNON</h2>", unsafe_allow_html=True)
    
    st.markdown("### SYSTEM STATUS")
    st.success("ONLINE") if engine else st.error("OFFLINE")
    
    if st.button("RESET WORKSPACE", use_container_width=True):
        st.session_state.messages = []
        clear_history()
        st.rerun()

    st.markdown("---")
    st.markdown("### 🚀 OTGALNON TOOLS")
    
    # 마지막 AI 답변 찾기 및 PPT 버튼 활성화
    last_assistant_response = next((msg["content"] for msg in reversed(st.session_state.get("messages", [])) if msg["role"] == "assistant"), None)

    if last_assistant_response:
        try:
            ppt_file = parse_text_to_ppt(last_assistant_response)
            st.download_button("📥 마지막 답변 PPT로 다운로드", data=ppt_file, file_name="OTGALNON_발표.pptx", use_container_width=True)
        except:
            st.caption("PPT 변환 대기 중...")
    else:
        st.info("AI의 답변을 PPT로 만들어 드립니다.")

# ==========================================
# 3. 메인 챗봇 인터페이스
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("명령을 입력하십시오..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    
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
                    save_history(st.session_state.messages)
                    st.rerun()
                except Exception as e:
                    st.error(f"시스템 오류: {str(e)}")
        else:
            st.warning("엔진 연결을 확인하십시오.")