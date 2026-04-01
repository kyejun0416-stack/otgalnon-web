import streamlit as st
import requests
import base64
import re

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon: Professional", layout="centered")

# CSS 스타일: 이모티콘 없이 선과 색상으로만 구분
st.markdown("""
    <style>
    .stTextArea textarea { background-color: #1e1e1e; color: #ffffff; border-radius: 5px; }
    .stButton button { width: 100%; border-radius: 5px; font-weight: bold; background-color: #333; color: white; border: 1px solid #555; }
    .stButton button:hover { border-color: #ff4b4b; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. API 키 로드 로직
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        st.title("System Settings")
        api_key = st.text_input("Gemini API Key", type="password")
        st.caption("Settings -> Secrets에 GEMINI_API_KEY를 등록하세요.")

# 사이드바 설정
with st.sidebar:
    st.divider()
    model_choice = st.selectbox("Engine Selection", ["gemini-flash-latest", "gemini-pro-latest"])
    st.caption("Project: otgalnon v4.1")
    st.caption("Mode: Direct Strategy (Minimal)")

# 3. 메인 인터페이스
st.title("otgalnon")
st.caption("분해와 검증을 거친 최종 전략 엔진")
st.divider()

user_input = st.text_area("분석 과제 입력", placeholder="텍스트를 입력하거나 파일을 업로드하십시오.", height=150)
uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])

if st.button("RUN ENGINE"):
    if not api_key:
        st.error("API Key가 누락되었습니다.")
    elif not user_input and not uploaded_file:
        st.warning("분석할 데이터가 없습니다.")
    else:
        with st.spinner("Processing..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
            
            system_instruction = "당신은 '오트가논' 엔진입니다. 내부적으로 분해/검증 후 최종 [출력] 내용만 핵심 위주로 제시하세요. 이모티콘 사용을 금지하고 건조하고 명확한 문체를 유지하십시오."
            
            parts = [{"text": f"{system_instruction}\n\n사용자 요청: {user_input}"}]
            if uploaded_file:
                image_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": image_b64}})
            
            payload = {"contents": [{"parts":
