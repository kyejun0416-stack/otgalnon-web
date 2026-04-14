import streamlit as st
import sqlite3
from datetime import datetime
import os
import streamlit as st

# ==========================================
# 0. AI ENGINE CONFIGURATION (PRO MODEL)
# ==========================================
# Streamlit Secrets 또는 환경 변수에서 키를 가져오도록 설정
# 로컬 테스트 시에는 .streamlit/secrets.toml 파일에 저장하세요.
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("SYSTEM NOTICE: API Key가 감지되지 않았습니다. 관리자 설정을 확인하십시오.")

def get_brain_engine():
    # 지능의 극대화를 위해 시스템 명령어를 더욱 정교하게 강화
    return genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=(
            "당신은 OTGALNON 프로젝트의 지식 아키텍트입니다. "
            "단순 응답이 아닌, 제1원리(First Principles)에 기반하여 문제를 분석하십시오. "
            "이모티콘을 철저히 배제하고, 논문 수준의 전문적인 한국어를 구사하십시오. "
            "답변의 구조는 서론, 본론(심층 분석), 결론(실행 방안)의 형식을 갖추십시오."
        )
    )

# ... (기존 UI 및 DB 로직 동일) ...

# 명령어 입력 및 처리 섹션 수정
if prompt := st.chat_input("Enter complex inquiry..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    memory.record(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("EXECUTING NEURAL REASONING..."):
            if api_key:
                try:
                    brain = get_brain_engine()
                    # 이전 대화 맥락을 모두 반영하여 지능적 연결성 확보
                    response = brain.generate_content(prompt)
                    output = response.text
                except Exception as e:
                    output = f"SYSTEM ERROR: 분석 과정에서 예외가 발생했습니다. ({str(e)})"
            else:
                output = "CRITICAL: 유효한 API Key 없이 분석 프로세스를 시작할 수 없습니다."
            
            st.markdown(output)
            st.code(output, language="markdown")
    
    st.session_state.messages.append({"role": "assistant", "content": output})
    memory.record(st.session_state.session_id, "assistant", output)
# 라이브러리 로드 시 예외 처리
try:
    import google.generativeai as genai
except ImportError:
    st.error("requirements.txt에 google-generativeai가 누락되었거나 설치 중입니다.")

# ==========================================
# 1. 페이지 설정 및 테마 (이모티콘 제거)
# ==========================================
page_icon_path = "logo.png" if os.path.exists("logo.png") else None
st.set_page_config(
    page_title="OTGALNON - Hyper Intelligence",
    page_icon=page_icon_path,
    layout="wide"
)

# 고급 보라색 테마 유지
st.markdown("""
    <style>
    .main { background: #0b091a; color: #d1d1d1; }
    [data-testid="stSidebar"] { background-color: #121026; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid #4b3d8f; border-radius: 8px; }
    .stButton>button { background: linear-gradient(45deg, #6d5dfc, #b83af3); color: white; border: none; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터베이스 엔진
# ==========================================
class MemoryEngine:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS chat_log 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp DATETIME)''')

    def record(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                         (session_id, role, content, datetime.now()))

    def recall(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

# ==========================================
# 3. 핵심 로직 및 세션 초기화 (순서 수정)
# ==========================================
memory = MemoryEngine()

# [중요] session_id를 가장 먼저 초기화하여 AttributeError 방지
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

# 그 다음 메시지 내역 로드
if "messages" not in st.session_state:
    st.session_state.messages = memory.recall(st.session_state.session_id)

# Gemini 설정
api_key = "YOUR_GEMINI_API_KEY" # 실제 키로 교체 필요
if api_key != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=api_key)

# ==========================================
# 4. 사이드바 및 UI
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    st.markdown("<h2 style='text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    st.divider()
    
    st.write(f"System Status: **ACTIVE**")
    st.write(f"Session: `{st.session_state.session_id}`")
    
    if st.button("RESET WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h1 style='color: #8e7cc3; font-weight: 300; letter-spacing: 2px;'>HYPER-INTELLIGENCE CENTER</h1>", unsafe_allow_html=True)

# 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 명령어 입력 및 처리
if prompt := st.chat_input("Enter command..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    memory.record(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Pro 모델로 고도화된 추론 수행
                model = genai.GenerativeModel('gemini-1.5-pro')
                sys_instruct = "당신은 OTGALNON의 분석 엔진입니다. 전문적이고 이모티콘 없는 고도의 지성체로 답하십시오."
                response = model.generate_content(f"{sys_instruct}\n\n질문: {prompt}")
                output = response.text
            except Exception as e:
                output = f"Operation Error: 분석 엔진 응답 실패. (사유: API 키 확인 필요)"
            
            st.markdown(output)
            st.code(output, language="markdown")
    
    st.session_state.messages.append({"role": "assistant", "content": output})
    memory.record(st.session_state.session_id, "assistant", output)




