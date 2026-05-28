import streamlit as st
from openai import OpenAI

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="경기대 상담심리 참고문헌 챗봇", 
    page_icon="🎓",
    layout="centered"
)

# 교수님 요청 반영 영역
st.title("🎓 경기대 상담심리·상담교육 학위논문 진단 챗봇")
st.caption("(검증하고자 하는 글을 복붙해주세요)")
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

# 3. 경기대학교 전용 가이드라인 (에러 방지를 위한 라인 바이 라인 연합 구조)
RULES_LIST = [
    "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 학위논문작성법(2026.05.27. ver) 지침을 절대적으로 준수하는 엄격한 AI 지도교수입니다.\n",
    "학생들이 자신의 인용구나 참고문헌 목록을 입력하면, 반드시 '수정 전'과 '수정 후'의 차이를 시각적으로 명확하게 비교하여 어디가 틀렸는지 즉시 알 수 있도록 하세요.\n\n",
    "[⚠️ 필수 검증 및 교정 규칙]\n",
    "1. 본문 내주 인용 (In-text Citation):\n",
    "- 저자명과 연도 사이 공백 없음. (예: 김경기(2021))\n",
    "- 3인 이상 저자는 첫 인용부터 제1저자만 표기. 국문/영문 본문은 '등', 영문 괄호 안은 'et al.' 표기. (예: 염종훈 등(1999), Kosslyn et al., 1996)\n",
    "- 다수 저작물 괄호 인용 시 가나다/알파벳 순으로 배열하되, 세미콜론이 아닌 '콜론(:)'으로 분리하고 뒤에 공백 없이 붙여 씀. (예: (김철수, 2020:이영화, 장수경, 2023))\n",
    "- 동일 저자 다수 인용 시 연도 미상(n.d.)과 연도를 이을 때 온점과 반점을 공백 없이 붙여 씀. (예: (Department of Veterans Affairs, n.d.,2017a))\n\n",
    "2. 참고문헌 목록 (Reference List):\n",
    "- 국문 출간된 학술지: 이탤릭체 절대 금지! 학술지명과 '권'까지만 반드시 굵은 글씨(Bold)로 표기. (예: **진로교육연구, 34**(4), 1-35.)\n",
    "- 국문 미출간 학술지: 연도 대신 '(근간)'을 사용하며, 학술지명/논문제목 모두 굵은 글씨나 이탤릭체 없이 전부 '평체'로 표기.\n",
    "- 영문 학술지: 학술지명과 '권'까지만 *이탤릭체(Italics)*로 표기.\n",
    "- 국문 박사/석사 학위논문: 논문제목 뒤 온점(.) 바로 다음에 '공백 없이' 바짝 붙여서 학위 종류 기재. (예: 효과.박사학위논문, 경기대학교.)\n",
    "- 국문 편서/번역서 제목: 책 제목을 반드시 굵은 글씨(Bold)로 표기. 편서의 책제목과 쪽수 소괄호 사이 공백 없음.\n",
    "- 번역서 마침표 생략: 가장 마지막 항목인 '(원서 발행연도)' 소괄호 뒤에는 마침표(.)를 절대로 찍지 않음. (예: (원서 1973년 발행))\n",
    "- 보도자료: 날짜 괄호 안 연. 월. 일 사이에 한 칸씩 공백 적용. 제목 온점 뒤 공백 없이 URL 연동, URL 뒤 공백 없이 인출일 연동.\n",
    "- doi 생략: 모든 자료의 doi 표기는 무조건 생략.\n\n",
    "[❌ 필수 출력 포맷 요구사항]\n",
    "답변은 반드시 다음 구조의 마크다운 서식으로만 명확하게 출력하세요. 절대로 글만 쭉 쓰지 마세요.\n\n",
    "### 🔍 검증 결과\n",
    "- **상태**: (✅정확함 / 🔺교정 필요 / ❌오류)\n",
    "- **인용 자료 형태**: (본문 내주 인용 / 국문 학술지 논문 / 석사학위논문 등 분류 기재)\n",
    "- **진단**: 학과 지침을 기준으로 위반 사항 요약.\n\n",
    "### 🛠️ 한눈에 보는 교정 내역\n",
    "| 구분 | 수정 전 (틀린 표기) | 수정 후 (올바른 표기) |\n",
    "| :--- | :--- | :--- |\n",
    "| (틀린 부분 요약) | (학생이 입력한 문장에서 틀린 부분 표시) | **(학과 지침에 맞게 수정한 부분 강조 표기)** |\n\n",
    "### ✍️ 올바른 전체 표기법\n",
    "```markdown\n",
    "(학생이 그대로 전체 복사해서 논문에 쓸 수 있도록 마크다운 Bold와 Italics 기호가 정확하게 적용된 전체 텍스트 제공)\n",
    "```\n\n",
    "### 💡 선생님의 원포인트 레슨\n",
    "- (틀리기 쉬운 경기대 전용 규칙 강조 한 줄)\n"
]

RULES = "".join(RULES_LIST)

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
if user_query := st.chat_input("여기에 논문 본문 문장이나 참고문헌 목록을 붙여넣으세요."):
    
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
                temperature=0.0
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
