import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 디자인 (보라색 테마)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { background-color: #1e1e2e !important; color: #ffffff !important; border: 1px solid #4b0082 !important; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #4b0082; color: white; border: none; height: 3em; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    [data-testid="stImage"] { margin-bottom: -35px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("Strategic Insight & Logic Engine")

st.divider()

# 4. 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="내용을 입력하십시오.", height=200)
uploaded_file = st.file_uploader("데이터 업로드 (이미지)", type=["jpg", "jpeg", "png"])

# 5. 설정 및 키 로드
with st.sidebar:
    st.title("Settings")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password")
    model_choice = st.selectbox("Engine Selection", ["gemini-1.5-flash", "gemini-1.5-pro"]) # 모델명 최신화
    st.caption("v5.5 | Final Stability Patch")

# 6. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("오류: API Key가 필요합니다.")
    elif not user_input and not uploaded_file:
        st.warning("내용을 입력하십시오.")
    else:
        with st.spinner("Decoding Strategy..."):
            try:
                # API Endpoint (v1beta 사용)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
                
                # 시스템 지침
                instr = "당신은 '오트가논' 전략 엔진입니다. 이모티콘 없이 수학적으로 간결하게 답변하세요."
                
                # 페이로드 구성
                contents_part = [{"text": f"{instr}\n\nTask: {user_input}"}]
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    contents_part.append({"inline_data": {"mime_type": uploaded_file.type, "data": img_data}})
                
                payload = {"contents": [{"parts": contents_part}]}
                
                # 요청 전송 (타임아웃 90초로 강화)
                response = requests.post(url, json=payload, timeout=90)
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### Strategic