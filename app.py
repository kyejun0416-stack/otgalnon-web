import streamlit as st
import sqlite3
from datetime import datetime
import os

# 1. 라이브러리 로드
try:
    import google.generativeai as genai
except ImportError:
    st.error("SYSTEM ERROR: 'google-generativeai' 라이브러리가 필요합니다.")

# ==========================================
# 2. 페이지 및 테마 설정 (이모티콘 배제)
# ==========================================
page_icon_path = "logo.png" if os.path.exists("logo.png") else None
st.set_page_config(
    page_title="OTGALNON - Hyper Intelligence",
    page_icon=page_icon_path,
    layout="wide"
)

# 보라색 다크 테마 적용
st.markdown("""
    <style>
    .main { background-color: #0b091a; color: #d1d1d1; }
    [data-testid="stSidebar"] { background-color: #0e0c1f; border-right: 1px solid #4b3d8f; }
    .stChatMessage { background-color: rgba(75, 61, 143, 0.1) !important; border: 1px solid rgba(75, 61, 143, 0.3); border-radius: 10px !important; }
    .stButton>button { background: linear-gradient(45deg, #4b3d8f, #6d5dfc); color: white; border: none; font-weight: 600; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 데이터베이스 엔진 (메모리 관리)
# ==========================================
class MemoryEngine:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS chat_log 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp DATETIME)''')

    def save(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                         (session_id, role, content, datetime.now()))

    def load(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

db = MemoryEngine()

# 세션 상태 초기화
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_v3_5_stable"
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 하이브리드 지능 엔진 (할당량 초과 대비)
# ==========================================
def run_intelligent_inference(user_input):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "CRITICAL ERROR: API Key가 존재하지 않습니다. Streamlit Secrets를 확인하십시오."

    genai.configure(api_key=api_key)
    
    # 지능 순서대로 모델 리스트업 (할당량 초과 시 자동 전환)
    # 사용자님이 원하시는 2.0 및 상위 지능 모델 포함
    model_candidates = ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
    
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=(
                    "당신은 OTGALNON의 최고 지능 분석 엔진입니다. "
                    "이모티콘 사용을 엄격히 금지하며, 고도로 정제된 전문용어와 논리적 구조를 사용하십시오. "
                    "단순한 응답을 넘어선 깊이 있는 통찰력(Insight)을 제시하십시오."
                )
            )
            response = model.generate_content(user_input)
            return f"**[ENGINE: {model_name}]**\n\n{response.text}"
        except Exception as e:
            # 429(할당량 초과) 에러가 나면 다음 모델로 시도
            if "429" in str(e):
                continue
            return f"SYSTEM ERROR: 엔진 구동 중 예외가 발생했습니다. ({str(e)})"
    
    return "ALL ENGINES EXHAUSTED: 모든 사용 가능한 모델의 할당량이 소진되었습니다. 잠시 후 다시 시도하십시오."

# ==========================================
# 5. UI 구성 및 실행
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png")
    st.markdown("<h2 style='text-align: center;'>OTGALNON</h2>", unsafe_allow_html=True)
    st.divider()
    if st.button("RESET WORKSPACE"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<h2 style='color: #6d5dfc; font-weight: 300; letter-spacing: 1px;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

# 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 입력창
if prompt := st.chat_input("Enter research query..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("EXECUTING HYPER-ANALYSIS..."):
            answer = run_intelligent_inference(prompt)
            st.markdown(answer)
            st.code(answer, language="markdown")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    db.save(st.session_state.session_id, "assistant", answer)