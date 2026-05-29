
import re
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="경기대 상담심리 참고문헌 검증기",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 경기대 상담심리·상담교육 참고문헌 검증기")
st.caption("경기대학교 상담심리학과/상담교육전공 학위논문 참고문헌 작성법 기준")

st.warning(
    "주의: 이 입력창은 Word의 실제 굵게/이탤릭 서식을 직접 읽지 못합니다. "
    "서식까지 검증하려면 **진로교육연구, 34**(4)처럼 Markdown 형식으로 입력하세요."
)

with st.expander("📌 핵심 규칙 보기", expanded=False):
    st.markdown(
        """
### 본문 내 인용
- 1인 저자: `김경기(2021)`, `(김경기, 2021)`
- 2인 저자 서술형: `최의소와 조광명(1979)`, `Kim과 Kolen(2007)`
- 2인 저자 괄호형: `(Kim & Kolen, 2007)`
- 3인 이상 서술형: `염종훈 등(1999)`, `Kosslyn 등(1996)`
- 3인 이상 괄호형: `(Kosslyn et al., 1996)`
- 다수 문헌: `(김철수, 2020; 이영화, 2023; 홍길동, 2026)`

### 국문 학술지 논문
- 기본 구조: `저자 (연도). 논문제목. 학술지명, 권(호), 쪽.`
- 서식: `학술지명, 권`까지만 굵게
- 예: `김지연 (2021). 진로전담교사의 전문성 발달과정 연구: 근거이론적 접근. **진로교육연구, 34**(4), 1-35.`
- `(호)`와 페이지는 굵게 아님
- DOI는 학위논문 참고문헌에서는 생략
"""
    )

api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

model = st.sidebar.selectbox(
    "모델 선택",
    ["gpt-4o-mini", "gpt-4.1-mini"],
    index=0,
)

client = OpenAI(api_key=api_key) if api_key else None

SYSTEM_PROMPT = (
    "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 "
    "학위논문 참고문헌 작성법(2026.05.27 ver.)을 기준으로 검토하는 엄격한 검증 도우미다.\n\n"
    "절대 규칙:\n"
    "1. 일반 APA 7판보다 경기대 상담심리학과 지침을 우선 적용한다.\n"
    "2. 국문 학술지 논문은 학술지명과 권(volume)까지만 굵게 처리한다. 예: **진로교육연구, 34**(4), 1-35.\n"
    "3. (호), 페이지는 굵게 처리하지 않는다.\n"
    "4. 영문 학술지 논문은 학술지명과 권(volume)까지만 이탤릭체로 본다.\n"
    "5. 학위논문 참고문헌에서는 DOI를 생략한다.\n"
    "6. 본문 내 인용에서 저자명과 연도 괄호 사이에는 공백을 두지 않는다.\n"
    "7. 2인 저자 서술형은 와/과를 사용한다. 괄호형 영문 인용은 &를 사용한다.\n"
    "8. 3인 이상 서술형은 국문/영문 모두 '등' 또는 '외'를 사용한다.\n"
    "9. 3인 이상 영문 괄호형은 et al.을 사용한다.\n"
    "10. 불확실한 경우 단정하지 말고 '추가 확인 필요'라고 쓴다.\n\n"
    "출력 형식:\n"
    "### 🔍 검증 결과\n"
    "- 상태:\n"
    "- 자료 유형:\n"
    "- 핵심 진단:\n\n"
    "### 🛠️ 교정 내역\n"
    "| 항목 | 현재 표기 | 권장 표기 |\n"
    "|---|---|---|\n\n"
    "### ✍️ 최종 권장 표기\n"
    "```markdown\n"
    "수정된 전체 문장 또는 참고문헌\n"
    "```\n\n"
    "### 💡 원포인트 설명\n"
    "- 한 줄 설명\n"
)


def detect_korean_journal_reference(text: str):
    issues = []

    if re.search(r"(doi\.org|DOI|doi:)", text, re.IGNORECASE):
        issues.append(("DOI 표기", "DOI가 포함되어 있음", "학위논문 참고문헌에서는 DOI 생략 권장"))

    plain_pattern = re.compile(
        r"(?P<authors>^[가-힣A-Za-z\s,·\.\-&]+)\s?\((?P<year>\d{4}|근간|in press)\)\.\s?"
        r"(?P<title>.+?)\.\s?"
        r"(?P<journal>[가-힣A-Za-z\s]+),\s?"
        r"(?P<volume>\d+)\((?P<issue>\d+)\),\s?"
        r"(?P<pages>\d+\s?-\s?\d+)\.",
        re.MULTILINE,
    )

    bold_pattern = re.compile(
        r"\*\*(?P<journal>[가-힣A-Za-z\s]+),\s?(?P<volume>\d+)\*\*\((?P<issue>\d+)\),\s?(?P<pages>\d+\s?-\s?\d+)\."
    )

    wrong_bold_issue_pattern = re.compile(
        r"\*\*(?P<journal>[가-힣A-Za-z\s]+),\s?(?P<volume>\d+)\((?P<issue>\d+)\)\*\*,\s?(?P<pages>\d+\s?-\s?\d+)\."
    )

    match = plain_pattern.search(text)
    if match:
        data = match.groupdict()
        ref_type = "국문 학술지 논문"

        if wrong_bold_issue_pattern.search(text):
            issues.append((
                "굵게 범위",
                "학술지명, 권(호) 전체가 굵게 처리됨",
                f"**{data['journal']}, {data['volume']}**({data['issue']}), {data['pages']}.",
            ))
        elif "**" in text and not bold_pattern.search(text):
            issues.append((
                "굵게 범위",
                "굵게 표시가 있으나 학술지명과 권까지만 굵게 처리되었는지 불명확함",
                f"**{data['journal']}, {data['volume']}**({data['issue']}), {data['pages']}.",
            ))
        elif "**" not in text:
            issues.append((
                "굵게 서식",
                "학술지명과 권의 굵게 여부를 확인할 수 없거나 표시되지 않음",
                f"**{data['journal']}, {data['volume']}**({data['issue']}), {data['pages']}.",
            ))

        return ref_type, data, issues

    return "자동분류 불확실", {}, issues


def detect_in_text_citation_issues(text: str):
    issues = []

    if re.search(r"[가-힣A-Za-z]+ \(\d{4}\)", text):
        issues.append(("본문인용 공백", "저자명과 연도 사이에 공백이 있음", "김경기(2021)처럼 붙여 씀"))

    if re.search(r"[A-Z][A-Za-z]+ and [A-Z][A-Za-z]+ ?\(\d{4}\)", text):
        issues.append(("2인 저자 서술형", "영문 저자 서술형에서 and 사용", "Kim과 Kolen(2007)처럼 과/와 사용"))

    if re.search(r"\([A-Z][A-Za-z]+ and [A-Z][A-Za-z]+,\s?\d{4}\)", text):
        issues.append(("2인 저자 괄호형", "괄호형 인용에서 and 사용", "(Kim & Kolen, 2007)처럼 & 사용"))

    if re.search(r"[A-Z][A-Za-z]+ et al\.?\s?\(\d{4}\)", text):
        issues.append(("3인 이상 서술형", "서술형에서 et al. 사용", "Kosslyn 등(1996)처럼 등 사용"))

    if re.search(r"\.\([가-힣A-Za-z].+?,\s?\d{4}\)", text):
        issues.append(("마침표 위치", "마침표가 괄호형 인용 앞에 있음", "문장 내용(저자, 연도). 형태로 괄호 뒤에 마침표"))

    return issues


def make_rule_based_report(text: str):
    ref_type, data, ref_issues = detect_korean_journal_reference(text)
    citation_issues = detect_in_text_citation_issues(text)
    issues = ref_issues + citation_issues

    status = "✅ 대체로 정확함" if not issues else "🔺 교정 필요"

    if issues:
        rows = ""
        for item, before, after in issues:
            rows += f"| {item} | {before} | {after} |\n"
    else:
        rows = "| - | 특별한 오류가 감지되지 않음 | 현재 표기 유지 가능 |\n"

    return status, ref_type, rows


user_text = st.text_area(
    "검증할 본문 인용 또는 참고문헌을 입력하세요",
    height=180,
    placeholder="예: 김지연 (2021). 진로전담교사의 전문성 발달과정 연구: 근거이론적 접근. **진로교육연구, 34**(4), 1-35.",
)

col1, col2 = st.columns([1, 1])
with col1:
    run_rule = st.button("1차 규칙 검증", use_container_width=True)
with col2:
    run_ai = st.button("AI 정밀 검토", use_container_width=True)

if run_rule and user_text.strip():
    status, ref_type, rows = make_rule_based_report(user_text)

    st.markdown("### 🔍 1차 규칙 검증 결과")
    st.markdown(f"- **상태**: {status}")
    st.markdown(f"- **자동 분류**: {ref_type}")
    st.markdown("### 🛠️ 감지된 항목")
    st.markdown("| 항목 | 현재 표기 | 권장 표기 |\n|---|---|---|\n" + rows)

if run_ai and user_text.strip():
    if not client:
        st.error("OpenAI API Key를 입력하거나 Streamlit Secrets에 등록해 주세요.")
        st.stop()

    status, ref_type, rows = make_rule_based_report(user_text)

    user_prompt = (
        "다음 학생 입력을 경기대학교 상담심리학과/상담교육전공 학위논문 참고문헌 작성법 기준으로 검토하라.\n\n"
        "[학생 입력]\n"
        f"{user_text}\n\n"
        "[1차 자동검출 결과]\n"
        f"상태: {status}\n"
        f"자료 유형: {ref_type}\n"
        f"교정 후보:\n{rows}\n\n"
        "중요:\n"
        "- 학생이 Markdown으로 굵게를 표시했다면 ** ** 범위를 실제 굵게 범위로 간주한다.\n"
        "- 학생이 일반 텍스트만 입력했다면 실제 굵게/이탤릭 여부는 확인 불가라고 말한다.\n"
        "- 국문 학술지 논문은 학술지명과 권까지만 굵게다. (호)는 굵게가 아니다.\n"
    )

    with st.spinner("AI가 정밀 검토 중입니다..."):
        try:
            response = client.responses.create(
                model=model,
                instructions=SYSTEM_PROMPT,
                input=user_prompt,
            )
            st.markdown(response.output_text)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

st.markdown("---")
st.caption("※ 본 도구는 1차 검토용입니다. 최종 제출 전 학과 지침서와 지도교수 확인이 필요합니다.")
