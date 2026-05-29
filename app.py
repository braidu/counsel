import re
from typing import List, Tuple

import streamlit as st
from openai import OpenAI


# =========================================================
# 경기대 상담심리·상담교육 참고문헌/본문인용 검증기
# - 규칙 기반 검증을 우선 적용
# - AI는 '위반 후보 설명' 보조용으로만 사용
# - Word의 실제 굵게/이탤릭 서식은 텍스트 입력창에서 직접 판독 불가
# =========================================================

st.set_page_config(
    page_title="경기대 상담심리 참고문헌 검증기",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 경기대 상담심리·상담교육 참고문헌 검증기")
st.caption("경기대학교 일반대학원 상담심리학과/교육대학원 상담교육전공 학위논문 참고문헌 작성법 기준")

st.info(
    "굵게/이탤릭까지 검증하려면 Markdown 방식으로 입력해 주세요. "
    "예: **진로교육연구, 34**(4), 1-35.  "
    "Word에서 복사한 일반 텍스트만으로는 실제 굵게 여부를 확정할 수 없습니다."
)

with st.expander("📌 핵심 규칙 보기", expanded=False):
    st.markdown(
        """
### Ⅰ. 본문 내 인용
- 1인 서술형: `김경기(2021)`, `Avram(1975)`
- 1인 괄호형: `(김경기, 2021)`, `(Avram, 1975)`
- 2인 서술형: `최의소와 조광명(1979)`, `Fredrickson과 Roberts(1997)`
- 2인 괄호형: `(Fredrickson & Roberts, 1997)`
- 3인 이상 서술형: `염종훈 등(1999)`, `Kosslyn 등(1996)`
- 3인 이상 괄호형: `(Kosslyn et al., 1996)`
- 다수 문헌 괄호형: `(김철수, 2020; 이영화, 장수경, 2023; 홍길동, 2026)`
- 다수 문헌 괄호형: `(Adams et al., 2019; Shumway & Shulman, 2015; Westinghouse, 2017)`

### Ⅱ. 국문 학술지 논문
- 기본 구조: `저자 (연도). 논문제목. 학술지명, 권(호), 쪽.`
- 굵게 범위: `학술지명, 권`까지만 굵게
- 예: `김지연 (2021). 진로전담교사의 전문성 발달과정 연구: 근거이론적 접근. **진로교육연구, 34**(4), 1-35.`
- `(호)`와 페이지는 굵게 아님
- 학위논문 참고문헌에서는 DOI 생략
        """
    )


# ---------------------------------------------------------
# OpenAI 설정
# ---------------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

client = OpenAI(api_key=api_key) if api_key else None

model = st.sidebar.selectbox(
    "AI 보조 검토 모델",
    ["gpt-4o-mini", "gpt-4.1-mini"],
    index=0,
)

SYSTEM_PROMPT = "\n".join(
    [
        "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 학위논문 참고문헌 작성법 검증 도우미다.",
        "반드시 경기대 지침을 일반 APA 지식보다 우선한다.",
        "가장 중요한 원칙: 규칙 기반 검증 결과에서 위반으로 잡히지 않은 항목은 임의로 고치지 않는다.",
        "본문 내 인용에서 서술형과 괄호형을 절대 혼동하지 않는다.",
        "Fredrickson과 Roberts(1997)는 올바른 2인 영문 저자 서술형 인용이다. 이를 Fredrickson & Roberts(1997)로 고치면 안 된다.",
        "(Fredrickson & Roberts, 1997)는 올바른 2인 영문 저자 괄호형 인용이다.",
        "(Calogero et al., 2011; Fredrickson et al., 1998)는 올바른 다수 문헌 괄호형 인용이다.",
        "이를 Calogero et al. (2011); Fredrickson et al. (1998)처럼 서술형으로 바꾸면 안 된다.",
        "다수 문헌 괄호형 인용에서는 각 문헌을 세미콜론으로 구분하고, 저자와 연도 사이에는 쉼표를 둔다.",
        "국문 학술지 논문은 학술지명과 권까지만 굵게다. 예: **진로교육연구, 34**(4), 1-35.",
        "(호)와 페이지는 굵게 처리하지 않는다.",
        "학생이 Markdown으로 굵게를 표시하지 않은 경우, 실제 굵게 여부는 확인 불가라고 말한다.",
        "출력은 간결하게 하되, 학생이 바로 고칠 수 있도록 수정 전/후를 표로 제시한다.",
    ]
)


# ---------------------------------------------------------
# 규칙 검증 함수
# ---------------------------------------------------------
Issue = Tuple[str, str, str]


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def split_top_level_semicolon(citation_body: str) -> List[str]:
    return [part.strip() for part in citation_body.split(";") if part.strip()]


def detect_in_text_citation_issues(text: str) -> List[Issue]:
    """본문 내 인용 규칙 검증. 오탐 방지를 위해 매우 명확한 경우만 오류로 잡는다."""
    issues: List[Issue] = []
    t = normalize_spaces(text)

    # 1. 서술형 인용: 저자와 연도 사이 공백 금지
    # 예: 김경기 (2021), Fredrickson과 Roberts (1997)
    if re.search(r"[가-힣A-Za-z]+(?:와|과| 등| 외)?\s+\(\d{4}[a-z]?\)", t):
        issues.append(
            (
                "본문인용 공백",
                "저자명/저자표현과 연도 괄호 사이에 공백이 있음",
                "김경기(2021), Fredrickson과 Roberts(1997)처럼 붙여 씀",
            )
        )

    # 2. 영문 2인 서술형에서 & 사용 금지
    # 올바름: Fredrickson과 Roberts(1997)
    if re.search(r"\b[A-Z][A-Za-z'\-]+\s*&\s*[A-Z][A-Za-z'\-]+\s*\(\d{4}[a-z]?\)", t):
        issues.append(
            (
                "2인 저자 서술형",
                "서술형 본문 인용에서 & 사용",
                "Fredrickson과 Roberts(1997)처럼 와/과 사용",
            )
        )

    # 3. 영문 2인 서술형에서 and 사용 금지
    if re.search(r"\b[A-Z][A-Za-z'\-]+\s+and\s+[A-Z][A-Za-z'\-]+\s*\(\d{4}[a-z]?\)", t):
        issues.append(
            (
                "2인 저자 서술형",
                "서술형 본문 인용에서 and 사용",
                "Fredrickson과 Roberts(1997)처럼 와/과 사용",
            )
        )

    # 4. 2인 괄호형에서 와/과 사용 금지
    if re.search(r"\([A-Z][A-Za-z'\-]+(?:와|과)\s*[A-Z][A-Za-z'\-]+,\s*\d{4}[a-z]?\)", t):
        issues.append(
            (
                "2인 저자 괄호형",
                "괄호형 영문 인용에서 와/과 사용",
                "(Fredrickson & Roberts, 1997)처럼 & 사용",
            )
        )

    # 5. 2인 괄호형에서 and 사용 금지
    if re.search(r"\([A-Z][A-Za-z'\-]+\s+and\s+[A-Z][A-Za-z'\-]+,\s*\d{4}[a-z]?\)", t):
        issues.append(
            (
                "2인 저자 괄호형",
                "괄호형 영문 인용에서 and 사용",
                "(Fredrickson & Roberts, 1997)처럼 & 사용",
            )
        )

    # 6. 3인 이상 영문 서술형에서 et al. 사용 금지
    # 올바름: Kosslyn 등(1996)
    if re.search(r"\b[A-Z][A-Za-z'\-]+\s+et\s+al\.?\s*\(\d{4}[a-z]?\)", t):
        issues.append(
            (
                "3인 이상 서술형",
                "서술형 본문 인용에서 et al. 사용",
                "Kosslyn 등(1996)처럼 등/외 사용",
            )
        )

    # 7. 3인 이상 괄호형에서 등/외 사용 금지
    if re.search(r"\([A-Z][A-Za-z'\-]+\s*(?:등|외),\s*\d{4}[a-z]?\)", t):
        issues.append(
            (
                "3인 이상 괄호형",
                "영문 괄호형 인용에서 등/외 사용",
                "(Kosslyn et al., 1996)처럼 et al. 사용",
            )
        )

    # 8. 괄호형 인용의 마침표 위치: .(저자, 2020) 형태는 의심
    if re.search(r"\.\s*\([가-힣A-Za-z][^)]*,\s*\d{4}[a-z]?\)", t):
        issues.append(
            (
                "마침표 위치",
                "마침표가 괄호형 인용 앞에 있음",
                "문장 내용(저자, 연도).처럼 괄호 뒤에 마침표",
            )
        )

    # 9. 괄호형 다수 문헌에서 각 문헌을 서술형으로 바꾼 형태 감지
    # 예: Calogero et al. (2011); Fredrickson et al. (1998)
    if re.search(r"[A-Z][A-Za-z'\-]+\s+et\s+al\.?\s*\(\d{4}[a-z]?\)\s*;", t):
        issues.append(
            (
                "다수 문헌 괄호형",
                "각 문헌의 연도를 별도 괄호로 감싼 서술형 형태",
                "(Calogero et al., 2011; Fredrickson et al., 1998)처럼 전체를 하나의 괄호 안에 제시",
            )
        )

    # 10. 괄호형 다수 문헌에서 세미콜론 뒤 공백 누락
    if re.search(r"\([^)]*;[^\s][^)]*\)", t):
        issues.append(
            (
                "다수 문헌 구분",
                "세미콜론 뒤 공백이 없음",
                "세미콜론 뒤 한 칸 띄움: (A, 2020; B, 2021)",
            )
        )

    return issues


def detect_korean_journal_issues(text: str) -> Tuple[str, List[Issue]]:
    """국문 학술지 논문 참고문헌 검증."""
    issues: List[Issue] = []
    t = text.strip()

    ref_type = "자동분류 불확실"

    # DOI 생략 규칙
    if re.search(r"doi\s*:|doi\.org|https?://doi\.org", t, re.IGNORECASE):
        issues.append(("DOI", "DOI가 포함되어 있음", "학위논문 참고문헌에서는 DOI 생략"))

    # 국문 학술지 논문 구조 감지
    # 김지연 (2021). 제목. 진로교육연구, 34(4), 1-35.
    plain = re.search(
        r"^(?P<authors>.+?)\s*\((?P<year>\d{4}|근간)\)\.\s*"
        r"(?P<title>.+?)\.\s*"
        r"(?P<journal>[가-힣A-Za-z·\s]+),\s*"
        r"(?P<volume>\d+)\((?P<issue>\d+)\),\s*"
        r"(?P<pages>\d+\s*-\s*\d+)\.?",
        t,
    )

    if plain:
        ref_type = "국문 학술지 논문"
        journal = plain.group("journal").strip()
        volume = plain.group("volume")
        issue = plain.group("issue")
        pages = plain.group("pages").replace(" ", "")
        correct = f"**{journal}, {volume}**({issue}), {pages}."

        # 올바른 Markdown 굵게 범위
        correct_bold = re.search(
            rf"\*\*{re.escape(journal)},\s*{re.escape(volume)}\*\*\({re.escape(issue)}\),\s*{re.escape(pages)}\.?",
            t,
        )

        # (호)까지 굵게 된 경우
        wrong_issue_bold = re.search(
            rf"\*\*{re.escape(journal)},\s*{re.escape(volume)}\({re.escape(issue)}\)\*\*,\s*{re.escape(pages)}\.?",
            t,
        )

        # 전체 학술지 부분이 굵게 된 경우
        wrong_all_bold = re.search(
            rf"\*\*{re.escape(journal)},\s*{re.escape(volume)}\({re.escape(issue)}\),\s*{re.escape(pages)}\.?\*\*",
            t,
        )

        if wrong_issue_bold or wrong_all_bold:
            issues.append(("굵게 범위", "(호) 또는 페이지까지 굵게 처리됨", correct))
        elif "**" not in t:
            issues.append(("굵게 확인", "Markdown 굵게 표시가 없어 실제 굵게 여부 확인 불가", correct))
        elif not correct_bold:
            issues.append(("굵게 범위", "학술지명과 권까지만 굵게 처리되었는지 불명확", correct))

    return ref_type, issues


def classify_input(text: str) -> str:
    if re.search(r"\(\d{4}[a-z]?\)", text) and "." in text and "," in text:
        if re.search(r"\d+\(\d+\),\s*\d+\s*-\s*\d+", text):
            return "참고문헌"
    if re.search(r"\(.*\d{4}[a-z]?.*\)", text):
        return "본문 내 인용"
    return "자동분류 불확실"


def make_rule_report(text: str) -> Tuple[str, str, List[Issue]]:
    input_type = classify_input(text)
    all_issues: List[Issue] = []

    ref_type, journal_issues = detect_korean_journal_issues(text)
    citation_issues = detect_in_text_citation_issues(text)

    all_issues.extend(journal_issues)
    all_issues.extend(citation_issues)

    if ref_type != "자동분류 불확실":
        input_type = ref_type

    status = "✅ 대체로 정확함" if not all_issues else "🔺 교정 필요"
    return status, input_type, all_issues


def issues_to_markdown_rows(issues: List[Issue]) -> str:
    if not issues:
        return "| - | 특별한 오류가 감지되지 않음 | 현재 표기 유지 가능 |\n"
    rows = []
    for item, before, after in issues:
        rows.append(f"| {item} | {before} | {after} |")
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
example = "Fredrickson과 Roberts(1997)는 자기대상화 이론을 제안하였다."
user_text = st.text_area(
    "검증할 본문 인용 또는 참고문헌을 입력하세요",
    value="",
    height=180,
    placeholder=example,
)

col1, col2 = st.columns(2)
run_rule = col1.button("1차 규칙 검증", use_container_width=True)
run_ai = col2.button("AI 보조 설명", use_container_width=True)

if run_rule and user_text.strip():
    status, input_type, issues = make_rule_report(user_text)
    st.markdown("### 🔍 1차 규칙 검증 결과")
    st.markdown(f"- **상태**: {status}")
    st.markdown(f"- **자료 유형**: {input_type}")
    st.markdown("### 🛠️ 교정 내역")
    st.markdown("| 항목 | 현재 표기 | 권장 표기 |\n|---|---|---|\n" + issues_to_markdown_rows(issues))

    if not issues:
        st.success("명확한 규정 위반은 감지되지 않았습니다. AI가 임의로 올바른 표기를 바꾸지 않도록 설계했습니다.")

if run_ai and user_text.strip():
    if not client:
        st.error("OpenAI API Key를 입력하거나 Streamlit Secrets에 등록해 주세요.")
        st.stop()

    status, input_type, issues = make_rule_report(user_text)
    issue_rows = issues_to_markdown_rows(issues)

    prompt = f"""
다음 학생 입력을 검토하라.

[학생 입력]
{user_text}

[규칙 기반 검증 결과]
상태: {status}
자료 유형: {input_type}
교정 후보:
{issue_rows}

지시:
1. 규칙 기반 검증에서 오류가 없으면, '명확한 오류가 감지되지 않았다'고 말하고 임의 교정을 하지 말라.
2. 특히 Fredrickson과 Roberts(1997)는 올바른 서술형 표기이므로 절대 &로 바꾸지 말라.
3. 특히 (Calogero et al., 2011; Fredrickson et al., 1998)는 올바른 괄호형 다수 문헌 표기이므로 각 연도를 별도 괄호로 바꾸지 말라.
4. 오류가 있는 경우에만 교정표를 작성하라.
"""

    with st.spinner("AI가 규칙 기반 결과를 설명 중입니다..."):
        try:
            response = client.responses.create(
                model=model,
                instructions=SYSTEM_PROMPT,
                input=prompt,
            )
            st.markdown(response.output_text)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

st.markdown("---")
st.caption("※ 본 도구는 1차 검토용입니다. 최종 제출 전 학과 지침서와 지도교수 확인이 필요합니다.")
