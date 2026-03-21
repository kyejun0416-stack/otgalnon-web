import streamlit as st
import google.generativeai as genai

# 1. 화면 구성 (심플 & 다크)
st.set_page_config(page_title="Otgalnon v0.1", layout="centered")
st.title("🚀 Otgalnon Control Console")
st.caption("Nexus-Omni Logic Engine v1.0")

# 2. 보안을 위한 사이드바 설정
with st.sidebar:
    st.header("⚙️ 엔진 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    # 모델명을 안정적인 버전으로 선택할 수 있게 합니다.
    target_model = st.selectbox("모델 선택", ["gemini-1.5-flash", "gemini-1.5-pro"])

# 3. 메인 로직 가동
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(target_model)

        user_input = st.text_area("질문이나 고민을 입력하세요:", height=150, placeholder="여기에 입력...")

        if st.button("엔진 가동 (Run)", type="primary"):
            if not user_input.strip():
                st.warning("❗ 분석할 내용을 입력해주세요.")
            else:
                # 코랩의 rules를 그대로 계승
                rules = "당신은 Nexus-Omni 요약 엔진입니다. 1.[분해] 2.[검증] 3.[출력] 구조로 핵심만 짧고 명확하게 답변하세요."
                
                with st.spinner("🧠 오트가논 논리 엔진 분석 중..."):
                    response = model.generate_content(f"{rules}\n\n질문: {user_input}")
                    
                    st.markdown("---")
                    st.subheader("💡 분석 결과")
                    st.markdown(response.text)
                    st.markdown("---")
                    
    except Exception as e:
        # 에러 발생 시 상세 내용을 화면에 표시
        st.error(f"❌ 엔진 작동 중 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바( > 모양 클릭)에 API Key를 입력하면 엔진이 활성화됩니다.")