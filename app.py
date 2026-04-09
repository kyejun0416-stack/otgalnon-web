import streamlit as st
import sqlite3
from datetime import datetime
import os

# ==========================================
# 1. 고급 보라색 테마 및 페이지 설정 (완벽 복구)
# ==========================================
st.set_page_config(
    page_title="otgalnon - Advanced Engine",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [디자인] 보라색 테마 및 고급진 UI 스타일링
st.markdown("""
    <style>
    /* 전체 배경 및 텍스트 톤 조절 */
    .main {
        background-color: #0f0c29;
        background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 50, 0.9);
        border-right: 1px solid #6d5dfc;
    }
    
    /* 채팅 메시지 박스 커스텀 */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(109, 93, 252, 0.3);
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 강조 색상 (보라색 포인트) */
    .stTextInput>div>div>input {
        color: #e0e0e0;
        background-color: #1e1e32;
        border-color: #6d5dfc !important;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background: linear-gradient(45deg, #6d5dfc, #b83af3);
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px #6d5dfc;
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
        with sqlite3.connect