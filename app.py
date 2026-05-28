import streamlit as st
from openai import OpenAI

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="경기대 상담심리 참고문헌 챗봇", 
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 경기대 상담심리·상담교육 학위논문 가이드")
st.caption("v2026.05.27 개정 지침 반영 | 선생님 모드 구동 중")
st.markdown("---")

# 2. API Key 검증
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요:", type="password")
    if not api_key:
        st.info("💡 안전한 구동을 위해 사이드바에 OpenAI API Key를 입력하거나 Secrets에 등록해주세요.")
        st.stop()

client = OpenAI(api_key=api_key)

# 3. 경기대학교 전용 가이드라인 (문법 에러 방지를 위해 깔끔하게 정리된 버전)
RULES = (
    "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 학위논문작성법(2026.05.27. ver) 지침을 숙지한 전문 AI 지도교수입니다.\n\n"
    "학생들이 내주 인용이나 참고문헌을 입력하면 다음 규정에 맞춰 '검증'하고 '교정'하세요.\n\n"
    "1. 내주 인용 규칙:\n"
    "- 문장과 내주 사이, 저자와 연도 사이 공백 없음 (예: 김경기(2021), (오동근, 2001))\n"
    "- 3인 이상 저자는 '첫 인용부터' 제1저자만 쓰고 국문은 '등', 영문 괄호 안은 ', et al.' 표기 (예: 염종훈 등(1999), Kosslyn et al., 1996)\n"
    "- 한 괄호 안 다수 인용은 가나다/알파벳 순으로 배열하고 세미콜론(;)으로 구분\n\n"
    "2. 참고문헌 규칙:\n"
    "- 학술지: doi 표기는 '학위논문에서 생략'함. 국문/영문 학술지명과 '권'까지만 이탤릭체 표기 (예: *진로교육연구, 34*(4))\n"
    "- 저서: 국서 제목은 이탤릭체 제외, 영서 제목은 이탤릭체 적용\n"
    "- 번역서: '원저자 (연도). 번역서명 (역자 역). 출판사. (원서 발행연도)' 순서로 쓰되 제일 뒤 원서연도 소괄호 다음에는 마침표(.)를 찍지 않음\n"
    "- 학위논문: '박사학위논문, 경기대학교.' 형식 준수\n"
    "- 웹문서: URL과 (인출일: YYYY.MM.DD.) 필수 표기. 연도 없으면 (n.d.)\n\n"
    "답변은 반드시 다음 형식을 갖추어 친절하게 존댓말로 출력하세요:\n"
    "### 🔍 검증 결과\n- [상태]: (✅정확함 / 🔺교정 필요 / ❌오류)\n- [진단]: 어떤 규칙을 위반했는지 구체적 설명\n\n"
    "### ✍️ 올바른 표기법\n```markdown\n(여기에 학생이 복사해서 쓸 수 있는 마크다운 이탤릭체 *가 적용된 올바른 포맷 제공)\n```\n\n"
    "### 💡 선생님의 원포인트 레슨\n- (조언 한 줄)"
)

# 4. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": RULES}
    ]

# 5. 기존 대화 렌더링
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 6. 사용자 입력 및 스트리밍 응답
if user_query := st.chat_input("검증받을 내주 인용구 또는 참고문헌 양식을 입력하세요."):
    
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        response_place = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
                temperature=0.2
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_place.markdown(full_response + "▌")
            response_place.markdown(full_response)
            
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")
            st.stop()
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
