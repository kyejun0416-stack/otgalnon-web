import streamlit as st
import sqlite3
from datetime import datetime

# ==========================================
# 1. 데이터베이스 관리 클래스 (저장소 엔진)
# ==========================================
class ChatManager:
    def __init__(self, db_path="otgalnon_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 파일과 테이블을 생성합니다."""
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
        """대화 내역을 DB 파일에 저장합니다."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO chat_log (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now())
            )
            conn.commit()

    def load(self, session_id):
        """저장된 대화 내역을 불러옵니다."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM chat_log WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            return [{"role": r, "content": c} for r, c in cursor.fetchall()]

# ==========================================
# 2. 앱 초기 설정 및 엔진 가동
# ==========================================
st.set_page_config(page_title="otgalnon 프로젝트", page_icon="⚙️")
db = ChatManager()

# 세션 ID 고정 (앱 재시작 시 대화 복구용)
if "session_id" not in st.session_state:
    st.session_state.session_id = "otgalnon_main_session"

# DB에서 과거 대화 불러오기
if "messages" not in st.session_state:
    st.session_state.messages = db.load(st.session_id)

# ==========================================
# 3. 프로젝트 핵심 로직 (회전 명령어 등)
# ==========================================
def process_otgalnon_command(command):
    """기존에 개발하던 otgalnon 핵심 엔진 로직"""
    if "시계방향" in command or "회전" in command:
        #