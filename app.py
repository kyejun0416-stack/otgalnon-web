import streamlit as st
import google.generativeai as genai

# 1. 기본 설정 (심플한 타이틀)
st.set_page_config(page_title="Otgalnon v0.1", layout="centered")
st.title("Otgalnon v0.1")
st.caption("Logic Processing Framework")

# 2. AI 엔진 연결 (Gemini API 키 입력 필요)
# 실제 배포 시에는 보안을 위해 암호화 처리가 필요합니다.
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 3. 사용자 입력창
    user_input = st.text_area("분석할 지식이나 고민을 입력하십시오:", placeholder="예: 공공 배포 프로그램 구축 전략")

    if st.button("오트가논 엔진 가동"):
        if user_input:
            # 4. 오트가논 핵심 로직 프롬프트 (분해-검증-출력)
            prompt = f"""
            당신은 '오트가논' 엔진입니다. 다음 입력에 대해 반드시 3단계 구조로 답변하십시오.
            
            [분해]: 문제를 해결하기 위한 3가지 핵심 하위 과제 (키워드 중심).
            [검증]: 현실적 제약, 논리적 오류, 리스크 2~3가지 비판.
            [출력]: 최적의 실행 전략을 개조식(Action Item)으로 제안.

            입력 내용: {user_input}
            """
            
            with st.spinner("논리 가공 중..."):
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
        else:
            st.warning("내용을 입력해 주세요.")
else:
    st.info("왼쪽 사이드바에 Gemini API Key를 입력하면 엔진이 활성화됩니다.")