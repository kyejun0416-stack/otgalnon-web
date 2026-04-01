import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정 및 브라우저 탭 아이콘
st.set_page_config(
    page_title="otgalnon",
    page_icon="logo.png",
    layout="centered"
)

# 2. 보라색 테마 기반 CSS 커스텀
st.markdown("""
    <style>
    /* 전체 배경 및 텍스트 영역 */
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { 
        background-color: #1e1e2e; 
        color: #d1d1e0; 
        border-radius: 8px; 
        border: 1px solid #4b0082; /* 인디고 퍼플 경계선 */
    }
    
    /* 버튼 스타일: 보라색 포인트 */
    .stButton button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        background-color: #4b0082; 
        color: white; 
        border: none;
        transition: all 0.3s;
    }
    .stButton button:hover { 
        background-color: #6a0dad; 
        box-shadow: 0 0 15px #6a0dad;
    }
    
    /* 코드 박스 스타일: 보라색 텍스트 강조 */
    code { 
        color: #bf94ff !important; 
        background-color: #16161d !important;
    }
    
    /* 로고 이미지 위치 조정 */
    [data-testid="stImage"] { margin-bottom: -35px; }
    
    /* 구분선 컬러 */
    hr { border-top: 1px solid #3d3d5c; }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더 섹션 (로고 & 타이틀)
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.caption("System")

with col2:
    st.title("otgalnon")
    st.markdown("<p style='color:#8a8ab5; margin-top:-15px;'>Strategic Insight & Logic Engine</p>", unsafe_allow_html=True)

st.divider()

# 4. API 키 보안 로드 (Secrets 우선)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.title("System Settings")