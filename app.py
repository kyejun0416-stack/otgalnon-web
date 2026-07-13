import streamlit as st
import google.generativeai as genai
from pptx import Presentation
import io

# ==========================================
# 1. 페이지 및 테마 설정
# ==========================================
st.set_page_config(page_title="OTGALNON", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
    /* 아바타 숨김 및 여백 최적화 (이전 완벽 버전 유지) */
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
    [data-testid="stChatMessage"] {
        padding: 1rem 0 !important;
        gap: 0rem !important;
    }
    [data-testid="stChatMessageContent"] {
        margin-left: 0px !important;
        padding-left: 0.5rem !important;
    }
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
# 2. PPT 자동 생성 로직 (OTGALNON 확장 기능)
# ==========================================
def generate_ppt_buffer():
    """PPT를 생성하고 메모리 버퍼에 저장하여 바로 다운로드할 수 있게 함"""
    prs = Presentation()
    
    # [슬라이드 1: 제목]
    slide0 = prs.slides.add_slide(prs.slide_layouts[0])
    slide0.shapes.title.text = "생성형 AI를 활용한 커스텀 챗봇 'OTGALNON' 개발"
    slide0.placeholders[1].text = "API 연동 및 UI/UX 최적화 탐구\n\n2학년 O반 O번 OOO"

    # [슬라이드 2: 목차]
    slide1 = prs.slides.add_slide(prs.slide_layouts[1])
    slide1.shapes.title.text = "목차"
    tf1 = slide1.placeholders[1].text_frame
    tf1.text = "1. 탐구 동기 및 시스템 구조"
    tf1.add_paragraph().text = "2. 핵심 과제 1: 오류 디버깅 (404 Not Found 해결)"
    tf1.add_paragraph().text = "3. 핵심 과제 2: UI/UX 디자인 최적화 (CSS 주입)"
    tf1.add_paragraph().text = "4. 결론 및 느낀 점"

    # [슬라이드 3: 핵심 내용 요약]
    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "프로젝트 핵심 요약"
    tf2 = slide2.placeholders[1].text_frame
    tf2.text = "동적 모델 탐색(genai.list_models)을 통한 시스템 안정성 확보"
    tf2.add_paragraph().text = "HTML DOM 분석 및 CSS 주입으로 모던 챗봇 인터페이스 구축"
    tf2.add_paragraph().text = "python-pptx 라이브러리 연동으로 자기 생성형(Self-generating) 프로젝트 완성"

    # 메모리에 저장 (서버에 쓰레기 파일이 남지 않도록 최적화)
    ppt_buffer = io.BytesIO()
    prs.save(ppt_buffer)
    ppt_buffer.seek(0)
    return ppt_buffer

# ==========================================
# 3. 시스템 엔진 초기화
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
# 4. 사이드바 컨트롤 패널
# ==========================================
with st.sidebar:
    try:
        st.image("logo.png", use_column_width=True)
    except:
        st.markdown("<h2 style='color: #6d5dfc; text-align: center; margin-bottom: 2rem;'>OTGALNON</h2>", unsafe_allow_html=True)
    
    st.markdown("### SYSTEM STATUS")
    if engine:
        st.success("ONLINE")
    else:
        st.error("OFFLINE")
    
    if st.button("RESET WORKSPACE", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 🚀 OTGALNON TOOLS")
    
    # PPT 생성 버튼 및 다운로드 로직
    if st.button("📊 발표용 PPT 자동 생성", use_container_width=True):
        with st.spinner("OTGALNON이 PPT를 작성 중입니다..."):
            ppt_file = generate_ppt_buffer()
            st.success("PPT 생성 완료!")
            st.download_button(
                label="📥 PPT 파일 다운로드",
                data=ppt_file,
                file_name="OTGALNON_발표자료.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )

# ==========================================
# 5. 메인 챗봇 인터페이스
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("명령을 입력하십시오..."):
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