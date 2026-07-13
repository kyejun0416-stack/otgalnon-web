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
    /* 아바타 숨김 및 여백 최적화 */
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
# 2. AI 답변 기반 동적 PPT 생성 로직
# ==========================================
def parse_text_to_ppt(ai_text):
    """오트가논이 답변한 마크다운 텍스트를 분석하여 PPT 슬라이드로 자동 변환"""
    prs = Presentation()
    lines = ai_text.split('\n')
    
    current_title = "OTGALNON AI 분석 결과"
    current_bullets = []
    
    # 제목 레이아웃으로 첫 장 생성 (표지)
    slide_layout_title = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout_title)
    slide.shapes.title.text = "OTGALNON 실시간 발표자료"
    slide.placeholders[1].text = "AI가 실시간으로 추출한 데이터 기반 보고서"

    # 본문 슬라이드 레이아웃 (제목 + 내용)
    slide_layout_content = prs.slide_layouts[1]

    def add_slide_to_presentation(title, bullets):
        """슬라이드를 추가하는 내부 헬퍼 함수"""
        if bullets or title != "OTGALNON AI 분석 결과":
            s = prs.slides.add_slide(slide_layout_content)
            s.shapes.title.text = title.replace('#', '').replace('*', '').strip()
            tf = s.placeholders[1].text_frame
            if bullets:
                tf.text = bullets[0]
                for bullet in bullets[1:]:
                    tf.add_paragraph().text = bullet

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # ### 나 ## 혹은 #으로 시작하면 새로운 슬라이드 제목으로 인식
        if line.startswith('#'):
            add_slide_to_presentation(current_title, current_bullets)
            current_title = line
            current_bullets = []
        # 글머리 기호 나 숫자 문장들을 본문 텍스트로 인식
        elif line.startswith(('*', '-', '•')) or (line[0].isdigit() if len(line) > 0 else False):
            clean_bullet = line.lstrip('*-•0123456789. ')
            if clean_bullet:
                current_bullets.append(clean_bullet)
        else:
            if len(current_bullets) < 5:  # 슬라이드 한 장당 최대 5줄 제한
                current_bullets.append(line)
                
    add_slide_to_presentation(current_title, current_bullets)

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
                "사용자가 발표 자료나 PPT 형태의 출력을 요구하면, 각 슬라이드의 제목은 '###' 또는 '##'으로 구분하고, "
                "내용은 글머리 기호(* 또는 -)를 사용하여 요약식으로 가독성 있게 작성하십시오."
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
    
    last_assistant_response = None
    if "messages" in st.session_state:
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                last_assistant_response = msg["content"]
                break

    if last_assistant_response:
        try:
            ppt_file = parse_text_to_ppt(last_assistant_response)
            st.download_button(
                label="📥 마지막 답변 PPT로 다운로드",
                data=ppt_file,
                file_name="OTGALNON_AI_발표자료.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )
        except Exception as e:
            st.caption(f"PPT 파일 변환 대기 중...")
    else:
        st.info("오트가논에게 명령을 내려서 답변을 받아보세요. 그 답변으로 PPT를 만들어 드립니다.")

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
                    st.rerun() # 코드 하단 오타 수정 완료 (rarun -> rerun)
                except Exception as e:
                    st.error(f"시스템 오류: {str(e)}")
        else:
            st.warning("엔진 연결을 확인하십시오.")