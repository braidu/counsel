import streamlit as st
from openai import OpenAI

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="경기대 상담심리 참고문헌 챗봇", 
    page_icon="🎓",
    layout="centered"
)

# 대문 타이틀 및 요청 캡션 적용
st.title("🎓 경기대 상담심리·상담교육 학위논문 진단 챗봇")
st.caption("(검증하고자 하는 글을 복붙해주세요)")
st.markdown("---")

# 2. 첫 화면 공식 가이드라인 예시 배치 (문법 에러 유발 기호 완벽 제거)
st.markdown("### 📘 경기대학교 상담심리 학과 공식 가이드 (PDF 원본)")
st.info("💡 아래의 각 항목을 클릭하시면 학과 지침서에 명시된 공식 작성 예시를 바로 확인하실 수 있습니다.")

with st.expander("📌 1. 본문 내주 인용 (In-text Citation) 지침"):
    st.write("- **1인 저자 (내주):** 저자명과 연도 사이 공백 없음")
    st.write("  * 올바른 예시: 김경기(2021)이 개발한 시스템에 따르면... / ...을 주장하고 있다(Avram, 1975).")
    st.write("- **2인 저자 (내주):** 국문은 '와/과'로 연결, 영문 괄호 안은 '&' 사용")
    st.write("  * 올바른 예시: 최의소와 조광명(1979)은... / ...라고 주장하고 있다(Kim & Kolen, 2007).")
    st.write("- **3인 이상 저자 (내주):** 첫 인용부터 제1저자만 제시 후 국문 '등', 영문 괄호 안 ', et al.' 표기")
    st.write("  * 올바른 예시: 염종훈 등(1999)이 지적한... / ...라고 하였다(Kosslyn et al., 1996).")
    st.write("- **다수 저작물 동시 인용:** 가나다/알파벳 순으로 배열하되, 반드시 세미콜론(;) 뒤에 한 칸 띄어서 분리")
    st.write("  * 올바른 예시: (김철수, 2020; 이영화, 장수경, 2023; 홍길동, 2026)")
    st.write("  * 올바른 예시: (Adams et al., 2019; Shumway & Shulman, 2015; Westinghouse, 2017)")
    st.write("- **동일 저자의 다수 저작물:** 반점(,) 뒤에 한 칸 띄어서 연도 나열")
    st.write("  * 올바른 예시: (Department of Veterans Affairs, n.d., 2017a, 2017b, 2019)")

with st.expander("📌 2. 학술지 논문 (Journal Articles) 지침"):
    st.write("- **국문 학술지 (출간):** 이탤릭체 절대 금지. 학술지명과 '권'까지만 **굵은 글씨(Bold)** 적용")
    st.write("  * 올바른 예시: 김지연 (2021). 진로전담교사의 전문성 발달과정 연구: 근거이론적 접근. **진로교육연구, 34**(4), 1-35.")
    st.write("- **영문 학술지 (출간):** 주요 단어 첫 글자 대문자, 학술지명과 '권'까지만 *이탤릭체(Italics)* 적용")
    st.write("  * 올바른 예시: Bingham, R. P. (2002). The issue may be the integration of personal and career issues. *The Counseling Psychologist, 30*(6), 885-890.")
    st.write("- **국문 미출간 학술지:** 연도 자리에 (근간) 표기. 논문제목 및 학술지명에 굵은글씨/이탤릭체 없이 모두 평체 표기")
    st.write("  * 올바른 예시: 김상담, 정수원 (근간). 역사환경 관련법이 농촌지역에 미친 영향에 관한 연구. 국토계획.")
    st.write("- **⚠️ doi 표기 안내:** 경기대학교 학위논문 체제에서는 참고문헌 목록의 모든 doi 표기를 **생략**합니다.")

with st.expander("📌 3. 석사 및 박사 학위논문 지침"):
    st.write("- **국문 학위논문 (띄어쓰기 교정 완료):** 논문제목 뒤 온점(.)을 찍고 반드시 **한 칸 띄어쓰기(공백)** 후 학위 종류 제시")
    st.write("  * 올바른 예시: 송영숙 (2022). 육군병사의 진로적응성 향상을 위한 Adler이론 기반 진로상담 프로그램 개발 및 효과. 박사학위논문, 경기대학교.")
    st.write("- **영문 학위논문 (DB인출):** 간행물 번호 소괄호가 대괄호 앞에 위치")
    st.write("  * 올바른 예시: Hollander, M. M. (2017). *Resistance to authority: Methodological innovations and new lessons from the Milgram experiment* (Publication No. 10289373) [Doctoral dissertation, University of Wisconsin-Madison]. ProQuest Dissertations and Theses Global.")

with st.expander("📌 4. 저서 / 편서 / 번역서 지침"):
    st.write("- **국문 저서:** 저자 1인 평체 표기")
    st.write("  * 올바른 예시: 김경기 (1970). 상담심리학. 학지사.")
    st.write("- **영문 저서:** 제목 전체 *이탤릭체* 기재 (첫 글자만 대문자인 Sentence-case)")
    st.write("  * 올바른 예시: Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Erlbaum.")
    st.write("- **영문 저자 2인 이상 주의:** 저자가 2인일지라도 앰퍼샌드(&) 앞에 반드시 **쉼표(,)** 삽입")
    st.write("  * 올바른 예시: Mitchell, T. R., & Larson, J. R., Jr. (1987).")
    st.write("- **국문 편서:** 책 제목을 **굵은 글씨**로 표기하며, 제목과 쪽수 소괄호 사이 공백 없음")
    st.write("  * 올바른 예시: 김태완 (2011). 한국의 사회적 과제와 창의적인 글로벌 인재 양성. 한국교육개발원 미래기획위원회(편), **한국교육 미래비전**(pp. 1-13). 학지사.")
    st.write("- **국문 번역서:** 책 제목 **굵은 글씨** 적용, 가장 마지막의 원서발행연도 소괄호 뒤에는 **마침표(.)를 찍지 않음**")
    st.write("  * 올바른 예시: Rutvan, K. K. (1988). **페미니스트 문학비평** (김경수 역). 문학과 비평사. (원서 1973년 발행)")

with st.expander("📌 5. 기타 자료 (보도자료 / 법률 및 판례 / 웹 문서) 지침"):
    st.write("- **보도자료:** 발행기관 뒤 날짜 괄호 안 연. 월. 일 사이에 한 칸씩 공백 적용. 제목 온점 뒤 공백 없이 URL 연동, URL 뒤 공백 없이 인출일 연동")
    st.write("  * 올바른 예시: 서울특별시교육청(2012. 9. 30.)은 ... 라고 발표했다.")
    st.write("  * 올바른 예시: 교육부 (2023). 진로교육 활성화 방안(2023-2027).https://www.moe.go.kr...(인출일: 2023.11.30.)")
    st.write("- **법률 및 판례:** 법원명 선고번호(선고일) 순으로 작성")
    st.write("  * 올바른 예시: 대법원 선고 2009추206(2013. 6. 27)작성")
    st.write("- **웹 문서 연도미상:** 지침서 고유 형태에 따라 소괄호 안 온점 표기 유의")
    st.write("  * 올바른 예시: Nielsen, M. E. (n.d). *Notable people in psychology of religion.* Retrieved August 3, 2001...")

st.markdown("---")
st.markdown("### 🔍 실시간 논문 진단 및 교정창")

# 3. API Key 검증
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요:", type="password")
    if not api_key:
        st.info("💡 안전한 구동을 위해 사이드바에 OpenAI API Key를 입력하거나 Secrets에 등록해주세요.")
        st.stop()

client = OpenAI(api_key=api_key)

# 4. 경기대학교 전용 가이드라인 규칙 리스트
RULES_LIST = [
    "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 학위논문작성법(2026.05.27. ver) 지침을 절대적으로 준수하는 엄격한 AI 지도교수입니다.\n",
    "일반적인 관행이나 타 대학 규칙이 아닌, 오직 경기대 상담심리 학과의 가이드라인 문서 내용만을 기준으로 학생들의 글을 검증하세요.\n\n",
    "[⚠️ 본문 인용(내주) 절대 규칙]\n",
    "1. 1인/2인 내주 인용 공백 규정:\n",
    "   - 문장 본문에서 내주 인용 시, 저자명(또는 조사 '와/과')과 연도 소괄호 사이에는 공백을 두지 않고 바로 붙여서 제시합니다. 예시: 김경기(2021), 최의소와 조광명(1979)은, Kim과 Kolen(2007)은\n",
    "2. 문장 끝 소괄호 인용 규정:\n",
    "   - 문장 끝에 소괄호 내주 인용이 올 경우 문장과 소괄호 사이에 간격을 두지 않고 바로 제시하며, 반드시 소괄호를 '닫고 나서' 마침표를 찍습니다. 예: 시스템이 있다(오동근, 2001).\n",
    "3. 3인 이상 저자 표기 규칙:\n",
    "   - 저자가 3명 이상일 경우 '첫 번째 인용 시부터' 제1저자명만 쓰고 국문/영문(본문)은 '등' 혹은 '외'를 첨부하고, 영문 소괄호 안 내주일 때는 ', et al.'을 첨부합니다. 예: 염종훈 등(1999), Kosslyn et al., 1996\n",
    "4. 다수의 저작물 소괄호 인용 규칙:\n",
    "   - 한 소괄호 안에 다수의 저작물을 나열할 때는 1저자의 가나다순, 알파벳순으로 배열하되, 반드시 '세미콜론(;)' 뒤에 한 칸을 띄어서 분리합니다. 올바른 예시: (김철수, 2020; 이영화, 장수경, 2023; 홍길동, 2026)\n",
    "5. 동일 저자의 다수 저작물 규칙:\n",
    "   - 출판 연도에 따라 배열하되 연도 미상(n.d.)과 연도 사이는 반점(,) 뒤에 한 칸을 띄어서 나열합니다. 올바른 예시: (Department of Veterans Affairs, n.d., 2017a, 2017b, 2019)\n\n",
    "[⚠️ 참고문헌 목록 절대 규칙]\n",
    "1. 국문 출간된 학술지 논문:\n",
    "   - 절대로 이탤릭체를 사용하지 마세요. 대신 학술지명과 '권'까지만 반드시 굵은 글씨(Bold)로 표기해야 합니다. 예: **진로교육연구, 34**(4), 1-35.\n",
    "2. 영문 출간된 학술지 논문:\n",
    "   - 학술지명과 '권'까지만 반드시 이탤릭체로 기재합니다. 예: *The Counseling Psychologist, 30*(6), 885-890.\n",
    "3. 국문 박사 및 석사 학위논문:\n",
    "   - 반드시 논문제목 뒤 온점(.)을 찍고 나서 '한 칸 띄어쓰기(공백)'를 한 후에 학위 종류를 적어야 합니다. 올바른 예시: 개발 및 효과. 박사학위논문, 경기대학교.\n",
    "4. doi 표기 생략:\n",
    "   - 참고문헌 목록의 모든 doi 표기를 '생략'합니다.\n\n",
    "[❌ 필수 출력 포맷 요구사항]\n",
    "사용자가 텍스트를 입력하면 무조건 아래의 마크다운 서식으로 표를 포함하여 출력하세요. 글만 나열하면 절대 안 됩니다.\n\n",
    "### 🔍 검증 결과\n",
    "- **상태**: (✅정확함 / 🔺교정 필요 / ❌오류)\n",
    "- **인용 자료 형태**: (분류 결과 기재)\n",
    "- **진단**: 위반 사항 요약.\n\n",
    "### 🛠️ 한눈에 보는 교정 내역\n",
    "| 구분 | 수정 전 (학생 표기) | 수정 후 (학과 지침 준수) |\n",
    "| :--- | :--- | :--- |\n",
    "| (틀린 항목 명칭) | (틀린 부분) | **(정확히 교정된 텍스트)** |\n\n",
    "### ✍️ 올바른 전체 표기법\n",
    "```markdown\n",
    "(학생이 전체 복사해서 바로 쓸 수 있도록 서식이 적용된 최종 완성본 제공)\n",
    "
```\n\n",
    "### 💡 선생님의 원포인트 레슨\n",
    "- (해당 규칙에 대한 원본 지침서의 핵심 요약 한 줄)\n"
]

RULES = "".join(RULES_LIST)

# 5. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": RULES}
    ]

# 6. 기존 대화 렌더링
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. 사용자 입력 및 스트리밍 응답
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
