import streamlit as st
import requests
import base64
import re
import os 

# 1. 페이지 설정
st.set_page_config(page_title="otgalnon", page_icon="logo.png", layout="centered")

# 2. 보라색 테마 기반 CSS (강력 적용)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    /* 입력창이 무조건 보이도록 배경색과 테두리 강조 */
    .stTextArea textarea { 
        background-color: #1e1e2e !important; 
        color: #ffffff !important; 
        border: 2px solid #4b0082 !important; 
        border-radius: 8px; 
    }
    .stButton button { 
        width: 100%; border-radius: 8px; font-weight: bold; 
        background-color: #4b0082; color: white; border: none; height: 3em;
    }
    .stButton button:hover { background-color: #6a0dad; box-shadow: 0 0 15px #6a0dad; }
    code { color: #bf94ff !important; background-color: #16161d !important; }
    [data-testid="stImage"] { margin-bottom: -35px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 헤더 섹션 (로고 & 타이틀)
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=80)
    else:
        st.write("🟣") # 로고 없을 시 임시 아이콘

with col2:
    st.title("otgalnon")
    st.markdown("<p style='color:#8a8ab5; margin-top:-15px;'>Strategic Insight & Logic Engine</p>", unsafe_allow_html=True)

st.divider()

# 4. [수정] 입력 인터페이스를 최우선으로 노출 (조건문 밖으로 추출)
user_input = st.text_area("분석 과제 입력", placeholder="분석할 내용을 입력하십시오.", height=200)
uploaded_file = st.file_uploader("데이터 업로드 (이미지 선택)", type=["jpg", "jpeg", "png"])

# 5. API 키 및 모델 설정 (사이드바)
with st.sidebar:
    st.title("Settings")
    # Secrets 확인 후 없으면 입력창
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key Loaded from Secrets")
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="API 키를 입력해야 엔진이 작동합니다.")
    
    st.divider()
    model_choice = st.selectbox("Engine Selection", ["gemini-flash-latest", "gemini-pro-latest"])
    st.caption("v5.2 | Strategic Purple")


# 6. 엔진 가동 로직 (타임아웃 보강 버전)
if st.button("RUN STRATEGY ENGINE"):
    if not api_key:
        st.error("오류: 사이드바에 API Key를 입력하십시오.")
    elif not user_input and not uploaded_file:
        st.warning("분석 데이터가 없습니다.")
    else:
        # 진행 상태 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Decoding Strategy..."):
            try:
                # API 엔드포인트
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
                
                # 시스템 지침 강화
                system_instruction = "당신은 '오트가논' 전략 엔진입니다. 이모티콘 없이 수학적이고 간결한 문체로 핵심만 답변하세요."
                
                status_text.text("데이터 패키징 중...")
                progress_bar.progress(30)
                
                parts = [{"text": f"{system_instruction}\n\nTask: {user_input}"}]
                
                if uploaded_file:
                    # 이미지 인코딩
                    image_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    parts.append({"inline_data": {"mime_type": uploaded_file.type, "data": image_b64}})
                
                status_text.text("구글 서버 통신 중 (최대 60초 대기)...")
                progress_bar.progress(60)
                
                # [핵심 수정] 타격 대기 시간을 60초로 확장하고 JSON 구조 정밀화
                response = requests.post(
                    url, 
                    json={"contents": [{"parts": parts}]}, 
                    headers={'Content-Type': 'application/json'},
                    timeout=60 # 대기 시간을 60초로 상향
                )
                
                res_json = response.json()
                progress_bar.progress(90)
                
                if 'candidates' in res_json:
                    status_text.text("전략 추출 완료.")
                    answer = res_json['candidates'][0]['content']['parts'][0]['text']
                    
                    st.markdown("### Strategic Output")
                    st.write(answer)
                    
                    # 텍스트 복사 최적화
                    clean_text = re.sub(r'[*#\-`>]', '', answer).strip()
                    st.divider()
                    st.markdown("<p style='color:#bf94ff; font-size:0.8rem;'>Plain Text for Copy</p>", unsafe_allow_html=True)
                    st.code(clean_text, language=None)
                else:
                    error_details = res_json.get('error', {}).get('message', '알 수 없는 API 응답')
                    st.error(f"Engine Error: {error_details}")
                
                progress_bar.progress(100)
                status_text.empty()

            except requests.exceptions.Timeout:
                st.error(" 서버 응답 시간 초과 (Timeout): 구글 서버가 너무 바쁘거나 데이터가 너무 큽니다. 잠시 후 다시 시도하세요.")
            except Exception as e:
                st.error(f" 가동 실패: {e}")