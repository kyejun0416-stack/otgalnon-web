import streamlit as st
import sqlite3
from datetime import datetime
import os

# ==========================================
# 1. 고급 테마 및 페이지 설정 (이모티콘 제거)
# ==========================================
# 페이지 아이콘에 logo.png 적용 (파일이 없을 경우를 대비해 설정)
page_icon_path = "logo.png" if os.path.exists("logo.png") else None

st.set_page_config(
    page_title="otgalnon - Advanced Engine",
    page_icon=page_icon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# [디자인] 보라색 테마 및 고급진 UI 스타일링
st.markdown("""
    <style>
    .main {
        background-color: #0f0c29;
        background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 50, 0.9);
        border-right: 1px solid #6d5dfc;
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(109, 93, 252, 0.3);
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stTextInput>div>div>input {
        color: #e0e0e0;
        background-color: #1e1e32;
        border-color: #6d5dfc !important;
    }
    .stButton>button {
        background: linear-gradient(45deg, #6d5dfc, #b83af3);
        color: white;
        border: none;
        transition: 0.3s;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px #6d5dfc;
    }
    /* 로고 이미지 정렬 */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        display: block;
        margin-left: auto;
        margin-right: auto;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 저장소 엔진 (SQLite)
# ==========================================
class ChatManager:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME
                )
            ''')
            conn.commit()

    def save(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now())
            )
            conn.commit()

    def load(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

# ==========================================
# 3. 데이터 초기화
# ==========================================
db = ChatManager()

if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_state.session_id)

# ==========================================
# 4. 사이드바 및 로고 제어
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #b83af3;'>OTGALNON</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-size: 0.75rem; color: #a0a0a0; margin-top: -10px;'>ADVANCED RESEARCH ENGINE</p>", unsafe_allow_html=True)
    st.divider()
    
    st.write(f"System Status: **ACTIVE**")
    st.write(f"Current Session: `{st.session_state.session_id}`")
    
    if st.button("New Workspace"):
        st.session_state.session_id = f"session_{datetime.now().strftime('%m%d_%H%M')}"
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption("Developed by User | Powered by otgalnon Core")

# ==========================================
# 5. 분석적 답변 로직 (이모티콘 제거)
# ==========================================
def process_command(text):
    cmd = text.strip()
    if "회전" in cmd or "시계방향" in cmd:
        return (
            "### Engine Control Sequence\n"
            "시스템 프로토콜에 의거하여 시계방향 회전 명령을 수신했습니다.\n\n"
            "- 수행 결과: 서보 모터 정밀 제어 완료\n"
            "- 현재 상태: 90도 회전 후 고정됨\n"
            "추가적인 캘리브레이션이 필요하시면 명령을 입력하십시오."
        )
    elif "라면" in cmd:
        return (
            "### 가이드: 조리 알고리즘 분석\n"
            "시스템 데이터베이스에 저장된 최적의 조리 시퀀스입니다.\n\n"
            "1. Water: 550ml의 물을 가열 장치로 비등점까지 도달시킵니다.\n"
            "2. Process: 물이 끓기 시작하면 면과 수프를 투입하고 4분간 일정한 열량을 유지하십시오.\n"
            "3. Result: 연산 결과에 따른 최상의 조리 상태가 도출되었습니다."
        )
    else:
        return (
            f"### Operation Analysis\n"
            f"입력 데이터 '{cmd}'에 대한 분석이 완료되었습니다.\n\n"
            "시스템은 현재 최적화된 대기 상태를 유지하고 있습니다."
        )

# ==========================================
# 6. 메인 제어 센터 (이모티콘 제거)
# ==========================================
st.markdown("<h2 style='color: #b83af3; letter-spacing: 2px;'>OTGALNON CONTROL CENTER</h2>", unsafe_allow_html=True)

# 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 명령어 입력
if prompt := st.chat_input("Enter command..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    db.save(st.session_state.session_id, "user", prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = process_command(prompt)
            st.markdown(response)
            st.code(response, language="markdown")
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    db.save(st.session_state.session_id, "assistant", response)