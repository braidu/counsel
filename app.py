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

# 2. 첫 화면 공식 가이드라인 예시 배치 (들여쓰기 에러 완벽 차단 구조)
st.markdown("### 📘 경기대학교 상담심리 학과 공식 가이드 (PDF 원본)")
st.info("💡 아래의 각 항목을 클릭하시면 학과 지침서에 명시된 공식 작성 예시를 바로 확인하실 수 있습니다.")

with st.expander("📌 1. 본문 내주 인용 (In-text Citation) 지침"):
    st.markdown("""
* **1인 저자 (내주):** 저자명과 연도 사이 공백 없음
  * *올바른 예:* `김경기(2021)이 개발한 시스템에 따르면...` / `...을 주장하고 있다(Avram, 1975).`
* **2인 저자 (내주):** 국문은 '와/과'로 연결, 영문 괄호 안은 '&' 사용
  * *올바른 예:* `최의소와 조광명(1979)은...` / `...라고 주장하고 있다(Kim & Kolen, 2007).`
* **3인 이상 저자 (내주):** 첫 번째 인용부터 제1저자만 제시 후 국문 '등', 영문 괄호 안 ', et al.' 표기
  * *올바른 예:* `염종훈 등(1999)이 지적한...` / `...라고 하였다(Kosslyn et al., 1996).`
* **다수 저작물 동시 인용:** 가나다/알파벳 순으로 배열하되, 반드시 **세미콜론(;)** 뒤에 한 칸 띄어서 분리
  * *올바른 예:* `(김철수, 2020; 이영화, 장수경, 2023; 홍길동, 2026)`
  * *올바른 예:* `(Adams et al., 2019; Shumway & Shulman, 2015; Westinghouse, 2017)`
* **동일 저자의 다수 저작물:** 반점(,) 뒤에 한 칸 띄어서 연도 나열
  * *올바른 예:* `(Department of Veterans Affairs, n.d., 2017a, 2017b, 2019)`
    """)

with st.expander("📌 2. 학술지 논문 (Journal Articles) 지침"):
    st.markdown("""
* **국문 학술지 (출간):** 이탤릭체 절대 금지. 학술지명과 '권'까지만 **굵은 글씨(Bold)** 적용
  * *올바른 예:* 김지연 (2021). 진로전담교사의 전문성 발달과정 연구: 근거이론적 접근. **진로교육연구, 34**(4), 1-35.
* **영문 학술지 (출간):** 주요 단어 첫 글자 대문자, 학술지명과 '권'까지만 *이탤릭체(Italics)* 적용
  * *올바른 예:* Bingham, R. P. (2002). The issue may be the integration of personal and career issues. *The Counseling Psychologist, 30*(6), 885-890.
* **국문 미출간 학술지:** 연도 자리에 (근간) 표기. 논문제목 및 학술지명에 굵은글씨/이탤릭체 없이 모두 평체 표기
  * *올바른 예:* 김상담, 정수원 (근간). 역사환경 관련법이 농촌지역에 미친 영향에 관한 연구. 국토계획.
* **⚠️ doi 표기 안내:** 경기대학교 학위논문 체제에서는 참고문헌 목록의 모든 doi 표기를 **생략**합니다.
    """)

with st.expander("📌 3. 석사 및 박사 학위논문 지침"):
    st.markdown("""
* **국문 학위논문 (★띄어쓰기 반영):** 논문제목 뒤 온점(.)을 찍고 반드시 **한 칸 띄어쓰기(공백)** 후 학위 종류 제시
  * *올바른 예:* 송영숙 (2022). 육군병사의 진로적응성 향상을 위한 Adler이론 기반 진로상담 프로그램 개발 및 효과. 박사학위논문, 경기대학교.
* **영문 학위논문 (DB인출):** 간행물 번호 소괄호가 대괄호 앞에 위치
  * *올바른 예:* Hollander, M. M. (2017). *Resistance to authority: Methodological innovations and new lessons from the Milgram experiment* (Publication No. 10289373) [Doctoral dissertation, University of Wisconsin-Madison]. ProQuest Dissertations and Theses Global.
    """)

with st.expander("📌 4. 저서 / 편서 / 번역서 지침"):
    st.markdown("""
* **국문 저서:** 저자 1인 평체 표기
  * *올바른 예:* 김경기 (1970). 상담심리학. 학지사.
