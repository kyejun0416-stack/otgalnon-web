
import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 엔진 설정 (자동 탐지 로직 유지)
# ==========================================
st.set_page_config(page_title="OTGALNON v6.0", layout="wide")

def get_engine():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return None, "API Key Missing"
    genai.configure(api_key=api_key)
    try:
        model_list = [m.name for m in genai.list_models()]
        # 스크린샷에서 확인한 Gemini 3 Flash 계열 우선 선택
        target = next((m for m in model_list if "gemini-3-flash" in m), "models/gemini-1.5-flash")
        return target
    except: return "models/gemini-1.5-flash"

active_model_id = get_engine()

# ==========================================
# 2. 사이드바 제어판 (모드 선택 추가)
# ==========================================
with st.sidebar:
    st.title("OTGALNON v6.0")
    st.success(f"CORE: {active_model_id}")
    
    # [핵심 추가] 스크립트 생성 모드 스위치
    gen_mode = st.radio("OPERATING MODE", ["General Research", "Script Generator"])
    
    st.divider()
    if st.button("CLEAR TERMINAL"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. 프롬프트 엔지니어링 (모드별 차등 적용)
# ==========================================
system_prompt = (
    "당신은 OTGALNON의 최고 분석관입니다. 모든 답변에서 이모티콘을 금지하십시오. "
    "사용자의 질문에 대해 제1원리 사고를 적용하여 답변하십시오."
)

if gen_mode == "Script Generator":
    system_prompt += (
        "\n\n[SCRIPT MODE ACTIVE]\n"
        "1. 코드는 실행 가능하고(Production-ready) 최적화되어야 합니다.\n"
        "2. 모든 코드에는 한글 주석을 상세히 작성하십시오.\n"
        "3. 사용자가 요청한 언어(Python, JS 등)의 최신 문법을 사용하십시오.\n"
        "4. 코드 블록 앞뒤에 구현 로직에 대한 간략한 설명을 포함하십시오."
    )

# ==========================================
# 4. 메인 채팅 인터페이스
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
                
                # 마크다운 렌더링
                st.markdown(answer)
                # 스크립트 모드일 때 코드를 더 편하게 복사할 수 있도록 강조
                if "```" in answer:
                    st.info("스크립트가 생성되었습니다. 아래 코드 블록을 복사하십시오.")
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"RUNTIME ERROR: {str(e)}")