import streamlit as st
import requests
import base64
import re
import os

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 보라색 테마 디자인
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stTextArea textarea { 
        background-color: #1e1e2e !important; 
        color: #ffffff !important; 
        border: 1px solid #4b0082 !important; 
    }
    .stButton button { 
        width: 100%; border-radius: 8px; font-weight: bold; 
        background-color: #4b0082; color: white; border: none; height: 3.5em;
    }
    .stButton button:hover { background-color: #6a0dad; box-shadow: 0 0 20px #6a0dad; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    [data-testid="stImage"] { margin-bottom: -35px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더 섹션
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"): st.image("logo.png", width=80)
    else: st.write("🟣")
with col2:
    st.title("otgalnon")
    st.caption("Strategic Insight & Logic Engine")

st.divider()

# 4. 입력 인터페이스
user_input = st.text_area("분석 과제 입력", placeholder="전략적 분석이 필요한 내용을 입력하십시오.", height=200)
uploaded_file = st.file_uploader("이미지 데이터 업로드", type=["jpg", "jpeg", "png"])

# 5. API 설정 (Secrets 자동 로드)
# 사용자가 수정할 필요가 없으므로 사이드바를 깔끔하게 정리합니다.
api_key = st.secrets.get("GEMINI_API_KEY")
model_name = "gemini-flash-latest"

with st.sidebar:
    st.title("System Status")
    if api_key:
        st.success("API Engine: Online")
    else:
        st.error(" API Key Missing in Secrets")
    st.divider()
    st.caption(f"Model: {model_name}")
    st.caption("v6.0 | Full-Auto Mode")

# 6. 엔진 가동 로직
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("시스템 오류: Streamlit Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
    elif not user_input and not uploaded_file:
        st.warning("분석할 데이터를 입력하십시오.")
    else:
        with st.spinner("Processing Strategy..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                instr = "당신은 '오트가논' 엔진입니다. 이모티콘 없이 수학적으로 간결하게 답변하세요."
                
                parts = [{"text": f"{instr}\n\nTask: {user_input}"}]
                
                if uploaded_file:
                    img_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": img_data}})
                
                response = requests.post(url, json={"contents": [{"parts": parts}]}, timeout=60)
                res_json = response.json()
                
                if 'candidates' in res_json:
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    st.divider()
                    st.markdown("<p style='color:#bf94ff; font-size:0.8rem;'>Plain Text for Copy</p>", unsafe_allow_html=True)
                    st.code(re.sub(r'[*#\-`>]', '', answer).strip(), language=None)
                else:
                    err = res_json.get('error', {}).get('message', 'Unknown Error')
                    st.error(f"Engine Error: {err}")
            except Exception as e:
                st.error(f"System Failure: {e}")

st.divider()
st.caption("© 2026 otgalnon Architecture. Automated via Streamlit Secrets.")