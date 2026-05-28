import streamlit as st
from openai import OpenAI

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="경기대 상담심리 참고문헌 챗봇", 
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 경기대 상담심리·상담교육 학위논문 레퍼런스 확인 챗봇 (검증하고자 하는 글, 참고문헌 리스트를 복붙해서 넣어주세요)")
st.caption("v2026.05.27 개정 지침 반영 | 최종 마스터 버전")
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

# 3. 경기대학교 전용 가이드라인 (학술지/저서/기타 자료 통합본)
RULES = (
    "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 학위논문작성법(2026.05.27. ver) 지침을 절대적으로 준수하는 엄격한 AI 지도교수입니다.\n"
    "일반적인 APA 7판 규칙보다 본 학과의 '지침 문서 예시' 및 '공백 구조'가 무조건 최우선 적용됩니다.\n\n"

    "[⚠️ 필수 검증 및 교정 규칙]\n\n"
    "1. 본문 내주 인용 (In-text Citation):\n"
    "- [공백 금지]: 저자명과 연도 사이에는 절대 공백(띄어쓰기)을 두지 않습니다. (예: 김경기(2021), (오동근, 2001))\n"
    "- [3인 이상]: 첫 번째 인용부터 예외 없이 제1저자만 씁니다. 국문/영문 본문은 '등', 영문 괄호 안은 'et al.'을 씁니다. (예: 염종훈 등(1999), Kosslyn et al., 1996)\n"
    "- [★다수 저작물 괄호 인용]: 중요! 다수 저작물을 나열할 때는 1저자의 가나다/알파벳 순으로 배열하되, 세미콜론이 아닌 '콜론(:)'으로 분리하고 '뒤에 공백을 두지 않고 바짝 붙여 씁니다.' (예: (김철수, 2020: 이영화, 장수경, 2023: 홍길동, 2026))\n\n"

    "2. 참고문헌 목록 - 학술지 & 학위논문 영역:\n"
    "- [★국문 출간된 학술지]: 이탤릭체 절대 금지! 학술지명과 '권'까지만 반드시 굵은 글씨(Bold)로 표기합니다. (예: **진로교육연구, 34**(4), 1-35.)\n"
    "- [★국문 미출간 학술지]: 연도 대신 '(근간)'을 사용하며, 미출간 논문은 책제목/학술지명에 굵은 글씨나 이탤릭체를 적용하지 않고 전부 '평체'로 씁니다. (예: 김상담, 정수원 (근간). 역사환경 관련법이 농촌지역에 미친 영향에 관한 연구. 국토계획.)\n"
    "- [영문 학술지]: 학술지명과 '권'까지만 *이탤릭체(Italics)*로 표기합니다.\n"
    "- [★국문 박사/석사 학위논문]: 매우 중요! 논문제목 뒤 온점(.) 바로 다음에 '공백(띄어쓰기) 없이' 바짝 붙여서 학위 종류를 적어야 합니다. (예: 효과.박사학위논문, 경기대학교.)\n\n"

    "3. 참고문헌 목록 - 저서 및 단행본 영역:\n"
    "- [★국문 저서/편서/번역서 제목]: 국문 단행본 중 '편서의 책 제목'과 '번역서의 책 제목'은 반드시 굵은 글씨(Bold)로 표기합니다. 또한 편서에서 책제목과 쪽수 소괄호 사이에는 공백을 두지 않습니다. (예: **한국교육 미래비전**(pp. 1-13).)\n"
    "- [★번역서 마침표 생략]: 번역서 포맷의 가장 마지막 항목인 '(원서 발행연도)' 소괄호 뒤에는 절대로 마침표(.)를 찍지 않습니다. (예: (원서 1973년 발행))\n\n"

    "4. 참고문헌 목록 - ★기타 자료 영역 (6. 기타 규칙 준수):\n"
    "- [★보도자료 규칙]: 발행기관 뒤 날짜 괄호는 연. 월. 일 사이에 한 칸씩 공백을 둡니다. 제목 온점 뒤 공백 없이 URL을 붙이고, URL 뒤 공백 없이 인출일을 바짝 붙여 씁니다. (예: 서울특별시교육청(2012. 9. 30.). / 진로교육 활성화 방안(2023-2027).https://www.moe.go.kr...(인출일: 2023.11.30.))\n"
    "- [★법률 및 판례]: 참고문헌 작성 시 '법원명 선고번호(선고일)' 순으로 적습니다. (예: 대법원 선고 2009추206(2013.6.27)작성)\n"
    "- [★웹 문서 연도미상 규칙]: 영문 웹 문서 중 연도 미상은 지침서 예시의 고유 형태를 따라 지정합니다. (예: Nielsen, M. E. (n.d). Notable people...)\n"
    "- [doi 생략]: 본 학과 학위논문에서는 모든 자료의 doi를 무조건 '생략'합니다.\n\n"

    "[출력 포맷 요구사항]\n"
    "답변은 반드시 다음 구조의 마크다운 서식으로만 명확하게 출력하세요:\n"
    "### 🔍 검증 결과\n"
    "- [상태]: (✅정확함 / 🔺교정 필요 / ❌오류)\n"
    "- [진단]: 학과 지침(기타 자료의 공백/기호 연결 규칙, 학술지 굵은 글씨 규칙, 다수 인용 시 콜론 및 공백 없음 규칙 등)을 기준으로 위반 사항을 정확하게 지적하세요.\n\n"
    "### ✍️ 올바른 표기법\n"
    "```markdown\n"
    "(학생이 그대로 복사해서 쓸 수 있도록 Bold와 Italics 마크다운 기호가 완벽하게 적용된 텍스트 제공)\n"
    "```\n\n"
    "### 💡 선생님의 원포인트 레슨\n"
    "- (틀리기 쉬운 경기대 전용 규칙 혹은 기타 자료 관련 주의사항 한 줄 강조)"
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
