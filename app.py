import re
from typing import Dict, List, Tuple

import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="경기대 상담심리 참고문헌 검증기",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 경기대 상담심리·상담교육 참고문헌 검증기")
st.caption("경기대학교 일반대학원 상담심리학과/교육대학원 상담교육전공 학위논문 참고문헌 작성법 기준")

st.info(
    "본문 인용과 참고문헌을 붙여넣으면 경기대 상담심리·상담교육 양식 기준으로 1차 검증합니다. "
    "Word의 실제 굵게/이탤릭 서식은 텍스트 입력창에서 직접 판별할 수 없으므로, "
    "굵게 검증은 Markdown 표기(**진로교육연구, 34**(4))가 있을 때만 확정 판정합니다."
)

with st.expander("📌 핵심 규칙 보기", expanded=False):
    st.markdown(
        """
### 본문 내 인용
- 1인 서술형: `김경기(2021)` / 괄호형: `(김경기, 2021)`
- 2인 서술형: `최의소와 조광명(1979)`, `Fredrickson과 Roberts(1997)`
- 2인 괄호형: `(Fredrickson & Roberts, 1997)`
- 3인 이상 서술형: `염종훈 등(1999)`, `Kosslyn 등(1996)`
- 3인 이상 괄호형: `(Kosslyn et al., 1996)`
- 다수 문헌 괄호형: `(Adams et al., 2019; Shumway & Shulman, 2015; Westinghouse, 2017)`

### 참고문헌 목록
- 국문 학술지 논문: `저자 (연도). 논문제목. **학술지명, 권**(호), 쪽.`
- 국문 참고문헌 저자 뒤에는 마침표를 찍지 않고 바로 `(연도)`를 씁니다.
  - 맞음: `김지연 (2021). 제목. **진로교육연구, 34**(4), 1-35.`
  - 틀림: `김지연. (2021). 제목. **진로교육연구, 34**(4), 1-35.`
- 국문 저자 나열에는 `&`를 쓰지 않습니다.
- 학위논문 참고문헌에서는 DOI를 생략합니다.
"""
    )


# -----------------------------
# API 설정
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

client = OpenAI(api_key=api_key) if api_key else None
model = st.sidebar.selectbox("AI 정밀 검토 모델", ["gpt-4o-mini", "gpt-4.1-mini"], index=0)


SYSTEM_PROMPT = "\n".join(
    [
        "당신은 경기대학교 일반대학원 상담심리학과 및 교육대학원 상담교육전공 학위논문 참고문헌 작성법 검증 도우미다.",
        "일반 APA 지식보다 경기대 상담심리·상담교육 지침을 우선한다.",
        "규칙 위반이 명확하지 않으면 임의로 고치지 말고 '확인 필요'라고 쓴다.",
        "학생 입력과 수정 후가 완전히 동일하다면 교정 내역 표에 넣지 않는다.",
        "국문 참고문헌의 저자 뒤에는 마침표를 찍지 않는다. 예: 김지연 (2021).",
        "국문 참고문헌에서 김기욱,& 박성규. (2019). 같은 표기는 틀렸다. 예: 김기욱, 박성규 (2019).",
        "국문 학술지 논문은 학술지명과 권까지만 굵게다. 예: **진로교육연구, 34**(4), 1-35.",
        "(호)와 페이지는 굵게가 아니다.",
        "본문 인용에서 Fredrickson과 Roberts(1997)는 맞다. 이를 Fredrickson & Roberts(1997)로 고치면 안 된다.",
        "괄호형 다중 인용에서 (Calogero et al., 2011; Fredrickson et al., 1998)는 맞다.",
        "괄호형 다중 인용을 Calogero et al. (2011); Fredrickson et al. (1998)처럼 바꾸면 안 된다.",
        "출력은 간결하게 하되, 학생이 바로 복사할 수 있는 최종 권장 표기를 제공한다.",
    ]
)


# -----------------------------
# 공통 유틸
# -----------------------------
def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def same_text(a: str, b: str) -> bool:
    return normalize_spaces(a) == normalize_spaces(b)


def split_entries(text: str) -> List[str]:
    """참고문헌/본문 입력을 줄 단위로 나눈다. 너무 짧은 줄은 제외한다."""
    raw = [line.strip() for line in text.splitlines()]
    entries = [line for line in raw if line and line not in {"[...]", "…"}]
    return entries


def make_markdown_table(rows: List[Dict[str, str]]) -> str:
    if not rows:
        return "오류가 명확히 감지되지 않았습니다."

    table = "| 항목 | 수정 전 | 수정 후 |\n|---|---|---|\n"
    for row in rows:
        before = row["before"].replace("|", "\\|")
        after = row["after"].replace("|", "\\|")
        table += f"| {row['item']} | {before} | {after} |\n"
    return table


# -----------------------------
# 본문 인용 검증
# -----------------------------
def check_in_text_citation(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []

    # 저자명과 연도 사이 공백: 김경기 (2021), Fredrickson (1997)
    for m in re.finditer(r"(?<![\w가-힣])([가-힣A-Za-z][가-힣A-Za-z .'-]*?)\s+\((\d{4}|n\.d\.)\)", text):
        before = m.group(0)
        after = f"{m.group(1).strip()}({m.group(2)})"
        if not same_text(before, after):
            rows.append({"item": "본문인용 공백", "before": before, "after": after})

    # 영문 2인 서술형에서 &를 쓴 경우: Fredrickson & Roberts(1997)
    # 단, 괄호형 (Fredrickson & Roberts, 1997)는 맞으므로 잡지 않음
    for m in re.finditer(r"(?<!\()\b([A-Z][A-Za-z.'-]+)\s*&\s*([A-Z][A-Za-z.'-]+)\((\d{4})\)", text):
        before = m.group(0)
        after = f"{m.group(1)}과 {m.group(2)}({m.group(3)})"
        rows.append({"item": "2인 저자 서술형", "before": before, "after": after})

    # 영문 2인 서술형에서 and를 쓴 경우
    for m in re.finditer(r"\b([A-Z][A-Za-z.'-]+)\s+and\s+([A-Z][A-Za-z.'-]+)\((\d{4})\)", text):
        before = m.group(0)
        after = f"{m.group(1)}과 {m.group(2)}({m.group(3)})"
        rows.append({"item": "2인 저자 서술형", "before": before, "after": after})

    # 괄호형 영문 2인에서 and 사용: (Kim and Kolen, 2007)
    for m in re.finditer(r"\(([A-Z][A-Za-z.'-]+)\s+and\s+([A-Z][A-Za-z.'-]+),\s*(\d{4})\)", text):
        before = m.group(0)
        after = f"({m.group(1)} & {m.group(2)}, {m.group(3)})"
        rows.append({"item": "2인 저자 괄호형", "before": before, "after": after})

    # 3인 이상 서술형에서 et al. 사용: Kosslyn et al.(1996)
    for m in re.finditer(r"\b([A-Z][A-Za-z.'-]+)\s+et\s+al\.?\s*\((\d{4})\)", text):
        before = m.group(0)
        after = f"{m.group(1)} 등({m.group(2)})"
        rows.append({"item": "3인 이상 서술형", "before": before, "after": after})

    # 문장 끝 괄호형 앞에 마침표가 먼저 온 경우: 주장하였다.(김, 2020)
    for m in re.finditer(r"\.\s*(\([^)]*,\s*(?:\d{4}|n\.d\.)[^)]*\))", text):
        before = m.group(0)
        after = f"{m.group(1)}."
        rows.append({"item": "마침표 위치", "before": before, "after": after})

    # 동일 교정 중복 제거
    unique = []
    seen = set()
    for row in rows:
        key = (row["item"], row["before"], row["after"])
        if key not in seen and not same_text(row["before"], row["after"]):
            unique.append(row)
            seen.add(key)
    return unique


# -----------------------------
# 참고문헌 검증
# -----------------------------
def fix_korean_author_segment(author_segment: str) -> str:
    """국문 참고문헌 저자부의 대표 오류 수정."""
    s = author_segment.strip()
    s = re.sub(r"\s*&\s*", " ", s)  # 국문 저자부 & 제거 전처리
    s = re.sub(r",\s*and\s*", ", ", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*,\s*", ", ", s)
    s = s.strip(" ,.")
    return s


def check_reference_entry(entry: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    original = entry.strip()

    # DOI 생략 규칙
    if re.search(r"doi\s*:|doi\.org", original, flags=re.IGNORECASE):
        rows.append({"item": "DOI 생략", "before": "DOI 포함", "after": "학위논문 참고문헌에서는 DOI 생략"})

    # 국문 참고문헌 저자부: 저자. (연도). -> 저자 (연도).
    m = re.match(r"^(.+?)\.\s*\((\d{4}|근간|in press|n\.d\.|\d{4},\s*[^)]+)\)\.", original)
    if m and re.search(r"[가-힣]", m.group(1)):
        fixed_authors = fix_korean_author_segment(m.group(1))
        before = m.group(0)
        after = f"{fixed_authors} ({m.group(2)})."
        if not same_text(before, after):
            rows.append({"item": "국문 저자 뒤 마침표", "before": before, "after": after})

    # 국문 참고문헌에서 & 사용: 김기욱,& 박성규 (2019).
    m2 = re.match(r"^(.+?)\s*\((\d{4}|근간|in press|n\.d\.|\d{4},\s*[^)]+)\)\.", original)
    if m2 and re.search(r"[가-힣]", m2.group(1)):
        author_before = m2.group(1)
        author_after = fix_korean_author_segment(author_before)
        if author_before != author_after:
            before = f"{author_before} ({m2.group(2)})."
            after = f"{author_after} ({m2.group(2)})."
            if not same_text(before, after):
                rows.append({"item": "국문 저자 나열", "before": before, "after": after})

    # 국문 학술지 굵게 범위: **학술지명, 권(호)** -> **학술지명, 권**(호)
    wrong_bold_issue = re.search(r"\*\*([^*]+?),\s*(\d+)\((\d+)\)\*\*,\s*([0-9]+\s*-\s*[0-9]+)", original)
    if wrong_bold_issue:
        before = wrong_bold_issue.group(0)
        after = f"**{wrong_bold_issue.group(1)}, {wrong_bold_issue.group(2)}**({wrong_bold_issue.group(3)}), {wrong_bold_issue.group(4)}"
        rows.append({"item": "굵게 범위", "before": before, "after": after})

    # 국문 학술지 논문인데 Markdown 굵게가 없는 경우: 확정 오류가 아니라 안내
    journal_plain = re.search(r"\.\s*([가-힣A-Za-z][가-힣A-Za-z\s·]+),\s*(\d+)\((\d+)\),\s*([0-9]+\s*-\s*[0-9]+)\.", original)
    if journal_plain and "**" not in original:
        journal = journal_plain.group(1).strip()
        volume = journal_plain.group(2)
        issue = journal_plain.group(3)
        pages = journal_plain.group(4)
        before = f"{journal}, {volume}({issue}), {pages}."
        after = f"**{journal}, {volume}**({issue}), {pages}."
        rows.append({"item": "국문 학술지 서식", "before": before, "after": after})

    # 완전 동일 교정 제거
    unique = []
    seen = set()
    for row in rows:
        key = (row["item"], row["before"], row["after"])
        if key not in seen and not same_text(row["before"], row["after"]):
            unique.append(row)
            seen.add(key)
    return unique


def build_full_recommendation(text: str) -> str:
    """대표 오류를 전체 텍스트에 적용한 초안. 과도한 재작성은 하지 않는다."""
    out = text

    # 저자. (연도). -> 저자 (연도). 단, 줄 시작에서만 처리
    def repl_author_dot(m: re.Match) -> str:
        authors = m.group(1)
        year = m.group(2)
        if re.search(r"[가-힣]", authors):
            return f"{fix_korean_author_segment(authors)} ({year})."
        return m.group(0)

    out = re.sub(r"(?m)^(.+?)\.\s*\((\d{4}|근간|in press|n\.d\.|\d{4},\s*[^)]+)\)\.", repl_author_dot, out)

    # 국문 저자부 & 제거: 줄 시작 저자부만
    def repl_author_amp(m: re.Match) -> str:
        authors = m.group(1)
        year = m.group(2)
        if re.search(r"[가-힣]", authors):
            return f"{fix_korean_author_segment(authors)} ({year})."
        return m.group(0)

    out = re.sub(r"(?m)^(.+?)\s*\((\d{4}|근간|in press|n\.d\.|\d{4},\s*[^)]+)\)\.", repl_author_amp, out)

    # 굵게 범위 수정
    out = re.sub(r"\*\*([^*]+?),\s*(\d+)\((\d+)\)\*\*,\s*([0-9]+\s*-\s*[0-9]+)", r"**\1, \2**(\3), \4", out)

    # 본문 인용 일부 수정
    out = re.sub(r"\b([A-Z][A-Za-z.'-]+)\s*&\s*([A-Z][A-Za-z.'-]+)\((\d{4})\)", r"\1과 \2(\3)", out)
    out = re.sub(r"\b([A-Z][A-Za-z.'-]+)\s+and\s+([A-Z][A-Za-z.'-]+)\((\d{4})\)", r"\1과 \2(\3)", out)
    out = re.sub(r"\b([A-Z][A-Za-z.'-]+)\s+et\s+al\.?\s*\((\d{4})\)", r"\1 등(\2)", out)

    return out.strip()


# -----------------------------
# 화면 입력 및 실행
# -----------------------------
user_text = st.text_area(
    "검증할 본문 인용 또는 참고문헌 목록을 입력하세요",
    height=240,
    placeholder="예: 김기욱,& 박성규. (2019).\n김지연 (2021). 진로전담교사의 전문성 발달과정 연구: 근거이론적 접근. 진로교육연구, 34(4), 1-35.",
)

col1, col2 = st.columns(2)
run_rule = col1.button("1차 규칙 검증", use_container_width=True)
run_ai = col2.button("AI 정밀 검토", use_container_width=True)

if run_rule and user_text.strip():
    all_rows: List[Dict[str, str]] = []
    all_rows.extend(check_in_text_citation(user_text))
    for entry in split_entries(user_text):
        all_rows.extend(check_reference_entry(entry))

    final_text = build_full_recommendation(user_text)
    status = "✅ 명확한 오류 없음" if not all_rows else "🔺 교정 필요"

    st.markdown("### 🔍 검증 결과")
    st.markdown(f"- **상태**: {status}")
    st.markdown("- **주의**: 수정 전과 수정 후가 완전히 동일한 항목은 교정 내역에서 자동 제외했습니다.")

    st.markdown("### 🛠️ 교정 내역")
    st.markdown(make_markdown_table(all_rows))

    st.markdown("### ✍️ 최종 권장 표기 초안")
    st.code(final_text, language="markdown")

if run_ai and user_text.strip():
    if not client:
        st.error("OpenAI API Key를 입력하거나 Streamlit Secrets에 등록해 주세요.")
        st.stop()

    all_rows: List[Dict[str, str]] = []
    all_rows.extend(check_in_text_citation(user_text))
    for entry in split_entries(user_text):
        all_rows.extend(check_reference_entry(entry))

    final_text = build_full_recommendation(user_text)
    rule_table = make_markdown_table(all_rows)

    prompt = f"""
다음 학생 입력을 경기대학교 상담심리·상담교육 학위논문 참고문헌 작성법 기준으로 검토하세요.

[학생 입력]
{user_text}

[규칙 기반 검출 결과]
{rule_table}

[규칙 기반 최종 권장 표기 초안]
{final_text}

검토 지시:
1. 규칙 기반 검출 결과를 우선 신뢰하세요.
2. 학생 입력과 수정 후가 동일한 항목은 절대 오류로 제시하지 마세요.
3. 국문 참고문헌 저자 뒤에는 마침표를 찍지 않습니다. '김지연 (2021).'가 맞고 '김지연. (2021).'는 틀립니다.
4. 국문 저자 나열에서 &를 쓰지 않습니다.
5. 본문 인용 Fredrickson과 Roberts(1997)는 맞습니다.
6. 괄호형 다중 인용 (Calogero et al., 2011; Fredrickson et al., 1998)는 맞습니다.
7. 불확실하면 추가 확인 필요라고 쓰세요.

출력 형식:
### 🔍 검증 결과
- 상태:
- 핵심 진단:

### 🛠️ 교정 내역
| 항목 | 수정 전 | 수정 후 |
|---|---|---|

### ✍️ 최종 권장 표기
```markdown
...
```
"""

    with st.spinner("AI가 정밀 검토 중입니다..."):
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
st.caption("※ 이 도구는 1차 검토용입니다. 최종 제출 전 학과 지침서와 지도교수 확인이 필요합니다.")
