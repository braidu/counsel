import re
import html
import streamlit as st
from dataclasses import dataclass
from typing import List, Tuple

st.set_page_config(
    page_title="경기대 상담심리 참고문헌 검증기",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 경기대 상담심리·상담교육 참고문헌 검증기")
st.caption("경기대학교 일반대학원 상담심리학과/교육대학원 상담교육전공 학위논문 참고문헌 작성법 기준")

st.info(
    " ※ 본 도구는 학과 지침에 따른 1차 형식 검토용입니다. 최종 제출 전 학과 지침서를 꼭 확인하세요 "
     " (굵게 표시는 본 웹에서는 확인 불가능)"
)

with st.expander("📌 핵심 규칙 보기", expanded=False):
    st.markdown(
        """
### 1. 본문 내 인용
- 저자명과 연도 사이 공백 없음: `김지형(2014)`, `Fredrickson과 Roberts(1997)`
- 2인 저자 서술형: `최의소와 조광명(1979)`, `Fredrickson과 Roberts(1997)`
- 2인 저자 괄호형: `(Fredrickson & Roberts, 1997)`
- 3인 이상 서술형: `염종훈 등(1999)`, `Kosslyn 등(1996)`
- 3인 이상 괄호형: `(Kosslyn et al., 1996)`
- 다수 문헌 괄호형: `(Adams et al., 2019; Shumway & Shulman, 2015; Westinghouse, 2017)`

### 2. 참고문헌 목록
- 국문 저자 뒤에는 마침표를 찍지 않음: `김지연 (2021).`
- 참고문헌 목록에서는 저자명과 연도 사이 한 칸 띄움
- 국문 저자 나열에는 `&`를 사용하지 않음: `김기욱, 박성규 (2019).`
- 국문 학술지 논문은 학술지명과 권까지만 굵게: `**진로교육연구, 34**(4), 1-35.`
- `(호)`와 페이지는 굵게 처리하지 않음
- 학위논문 참고문헌에서는 DOI 생략
        """
    )

mode = st.radio(
    "검증 유형을 선택하세요",
    ["자동 판정", "본문 내 인용", "참고문헌 목록"],
    horizontal=True,
)

sample = "김지형 (2014) 의료 판매원의 정서성, 직무 자율성, 고객 무례성이 감정노동의 수행 및 결과에 미치는 영향. 숙명여자대학교 대학원 박사학위 논문\n고남정. (2018). 유식 삼성설과 인지치료의 비교연구: 엘리스와 아론벡의인지치료를 중심으로. (박사학위논문). 동국대학교."

user_text = st.text_area(
    "검증할 본문 인용 또는 참고문헌 목록을 입력하세요",
    height=220,
    placeholder=sample,
)

@dataclass(frozen=True)
class Correction:
    item: str
    before: str
    after: str
    note: str = ""


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def add_correction(corrections: List[Correction], item: str, before: str, after: str, note: str = "") -> None:
    before_clean = normalize_spaces(before)
    after_clean = normalize_spaces(after)
    if not before_clean or before_clean == after_clean:
        return
    key = (item, before_clean, after_clean)
    existing = {(c.item, c.before, c.after) for c in corrections}
    if key not in existing:
        corrections.append(Correction(item, before_clean, after_clean, note))


def guess_mode(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "본문 내 인용"
    ref_like = 0
    for ln in lines:
        if re.search(r"\([12]\d{3}|근간|in press|n\.d\.\)\)", ln) and re.search(r"\.\s*", ln):
            ref_like += 1
        if re.search(r"학위논문|학위 논문|대학교|대학원|[가-힣A-Za-z ]+,\s*\d+\(\d+\),\s*\d+\s*-\s*\d+", ln):
            ref_like += 1
    return "참고문헌 목록" if ref_like >= max(1, len(lines) // 2) else "본문 내 인용"


def check_in_text(text: str) -> Tuple[List[Correction], str]:
    corrections: List[Correction] = []
    fixed = text

    # 저자명과 연도 사이 공백: 김지형 (2014) -> 김지형(2014)
    pattern_space = re.compile(r"([가-힣A-Za-z]+(?:과|와| 등| 외| et al\.)?)\s+\((\d{4}|n\.d\.)\)")
    for m in pattern_space.finditer(text):
        before = m.group(0)
        after = f"{m.group(1)}({m.group(2)})"
        add_correction(corrections, "본문인용 공백", before, after, "본문 내 인용에서는 저자명과 연도 사이를 붙입니다.")
        fixed = fixed.replace(before, after)

    # 저자명 뒤 점: 고남정.(2018) 또는 고남정. (2018) -> 고남정(2018)
    pattern_dot = re.compile(r"([가-힣A-Za-z]+)\.\s*\((\d{4}|n\.d\.)\)")
    for m in pattern_dot.finditer(text):
        before = m.group(0)
        after = f"{m.group(1)}({m.group(2)})"
        add_correction(corrections, "본문인용 저자 뒤 마침표", before, after, "본문 내 인용에서는 저자명 뒤 마침표를 쓰지 않습니다.")
        fixed = fixed.replace(before, after)

    # 영문 2인 서술형 & 오용: Fredrickson & Roberts(1997) -> Fredrickson과 Roberts(1997)
    pattern_amp_narrative = re.compile(r"\b([A-Z][A-Za-z'\-]+)\s*&\s*([A-Z][A-Za-z'\-]+)\s*\((\d{4}|n\.d\.)\)")
    for m in pattern_amp_narrative.finditer(text):
        before = m.group(0)
        after = f"{m.group(1)}과 {m.group(2)}({m.group(3)})"
        add_correction(corrections, "2인 저자 서술형", before, after, "서술형에서는 영문 저자라도 와/과를 사용합니다.")
        fixed = fixed.replace(before, after)

    # 괄호형 영문 2인 and 오용: (Kim and Kolen, 2007) -> (Kim & Kolen, 2007)
    pattern_and_parenthetical = re.compile(r"\(([A-Z][A-Za-z'\-]+)\s+and\s+([A-Z][A-Za-z'\-]+),\s*(\d{4}|n\.d\.)\)")
    for m in pattern_and_parenthetical.finditer(text):
        before = m.group(0)
        after = f"({m.group(1)} & {m.group(2)}, {m.group(3)})"
        add_correction(corrections, "2인 저자 괄호형", before, after, "괄호형 영문 인용에서는 &를 사용합니다.")
        fixed = fixed.replace(before, after)

    # 서술형 3인 이상 et al. 오용: Kosslyn et al.(1996) -> Kosslyn 등(1996)
    pattern_etal_narrative = re.compile(r"\b([A-Z][A-Za-z'\-]+)\s+et\s+al\.\s*\((\d{4}|n\.d\.)\)")
    for m in pattern_etal_narrative.finditer(text):
        before = m.group(0)
        after = f"{m.group(1)} 등({m.group(2)})"
        add_correction(corrections, "3인 이상 서술형", before, after, "서술형에서는 영문 저자라도 등/외를 사용합니다.")
        fixed = fixed.replace(before, after)

    # 문장 끝 괄호형 인용 앞 마침표: .(김지형, 2014) -> (김지형, 2014).
    pattern_period_before = re.compile(r"\.\s*(\([^\)]*?,\s*(?:\d{4}|n\.d\.)[^\)]*\))")
    for m in pattern_period_before.finditer(text):
        before = m.group(0)
        after = f"{m.group(1)}."
        add_correction(corrections, "괄호형 인용 마침표 위치", before, after, "마침표는 괄호형 인용 뒤에 둡니다.")
        fixed = fixed.replace(before, after)

    return corrections, fixed


def fix_korean_author_segment(line: str) -> Tuple[str, List[Correction]]:
    corrections: List[Correction] = []
    original = line

    # 연도 앞까지를 저자부로 간주
    m = re.search(r"\((\d{4}|근간|in press|n\.d\.)\)", line)
    if not m:
        return line, corrections

    author_part = line[:m.start()].strip()
    rest = line[m.start():]
    new_author = author_part

    # 국문 저자부의 & 제거
    if "&" in new_author and re.search(r"[가-힣]", new_author):
        before = new_author
        new_author = new_author.replace("&", "")
        new_author = re.sub(r",\s*,", ",", new_author)
        new_author = re.sub(r",\s*$", "", new_author).strip()
        add_correction(corrections, "국문 저자 & 사용", before, new_author, "국문 저자 나열에는 &를 사용하지 않습니다.")

    # 저자명 뒤 마침표 제거: 김지형. -> 김지형
    if re.search(r"\.\s*$", new_author):
        before = new_author
        new_author = re.sub(r"\.\s*$", "", new_author).strip()
        add_correction(corrections, "참고문헌 저자 뒤 마침표", before, new_author, "참고문헌 목록에서도 저자명 뒤에는 마침표를 찍지 않고 연도 괄호가 이어집니다.")

    # 쉼표 주변 정리
    before_spacing = new_author
    new_author = re.sub(r"\s*,\s*", ", ", new_author)
    new_author = re.sub(r"\s+", " ", new_author).strip()
    if before_spacing != new_author:
        add_correction(corrections, "국문 저자 나열 공백", before_spacing, new_author, "저자 사이는 쉼표 뒤 한 칸으로 정리합니다.")

    fixed = f"{new_author} {rest}"

    # 참고문헌 목록에서 저자와 연도 사이 공백 보장
    before_line = fixed
    fixed = re.sub(r"^(.+?)\s*\((\d{4}|근간|in press|n\.d\.)\)", r"\1 (\2)", fixed, count=1)
    if before_line != fixed:
        add_correction(corrections, "참고문헌 연도 앞 공백", before_line, fixed, "참고문헌 목록에서는 저자명과 연도 사이를 한 칸 띄웁니다.")

    return fixed, corrections


def check_references(text: str) -> Tuple[List[Correction], str]:
    corrections: List[Correction] = []
    fixed_lines = []

    for line in text.splitlines():
        if not line.strip():
            fixed_lines.append(line)
            continue

        fixed_line, line_corrs = fix_korean_author_segment(line)
        for c in line_corrs:
            add_correction(corrections, c.item, c.before, c.after, c.note)

        # DOI 생략 권고
        if re.search(r"doi\s*:|doi\.org", fixed_line, flags=re.IGNORECASE):
            before = fixed_line
            after = re.sub(r"\s*https?://(?:dx\.)?doi\.org/\S+", "", fixed_line, flags=re.IGNORECASE)
            after = re.sub(r"\s*doi\s*:\s*\S+", "", after, flags=re.IGNORECASE).strip()
            add_correction(corrections, "DOI 표기", before, after, "학위논문 참고문헌에서는 DOI를 생략합니다.")
            fixed_line = after

        # 국문 학술지 굵게 범위 검사. Markdown 입력 기준.
        journal_plain = re.search(r"([가-힣A-Za-z·\s]+),\s*(\d+)\((\d+)\),\s*(\d+\s*-\s*\d+)\.", fixed_line)
        journal_bold_correct = re.search(r"\*\*([가-힣A-Za-z·\s]+),\s*(\d+)\*\*\((\d+)\),\s*(\d+\s*-\s*\d+)\.", fixed_line)
        journal_bold_wrong = re.search(r"\*\*([가-힣A-Za-z·\s]+),\s*(\d+)\((\d+)\)\*\*,\s*(\d+\s*-\s*\d+)\.", fixed_line)

        if journal_bold_wrong:
            before = journal_bold_wrong.group(0)
            after = f"**{journal_bold_wrong.group(1).strip()}, {journal_bold_wrong.group(2)}**({journal_bold_wrong.group(3)}), {journal_bold_wrong.group(4)}."
            add_correction(corrections, "국문 학술지 굵게 범위", before, after, "학술지명과 권까지만 굵게 처리합니다. (호)는 굵게 처리하지 않습니다.")
            fixed_line = fixed_line.replace(before, after)
        elif journal_plain and "**" not in fixed_line:
            before = journal_plain.group(0)
            after = f"**{journal_plain.group(1).strip()}, {journal_plain.group(2)}**({journal_plain.group(3)}), {journal_plain.group(4)}."
            add_correction(corrections, "국문 학술지 굵게 표시", before, after, "Markdown 기준으로 학술지명과 권까지만 굵게 표시합니다.")
            fixed_line = fixed_line.replace(before, after)
        elif "**" in fixed_line and journal_bold_correct is None and journal_plain:
            before = journal_plain.group(0)
            after = f"**{journal_plain.group(1).strip()}, {journal_plain.group(2)}**({journal_plain.group(3)}), {journal_plain.group(4)}."
            add_correction(corrections, "국문 학술지 굵게 범위", before, after, "굵게 범위를 학술지명과 권까지만 맞춥니다.")

        fixed_lines.append(fixed_line)

    return corrections, "\n".join(fixed_lines)


def render_corrections(corrections: List[Correction]) -> None:
    if not corrections:
        st.success("감지된 형식 오류가 없습니다.")
        return

    st.markdown("### 🛠️ 교정 내역")
    table = ["| 항목 | 수정 전 | 수정 후 |", "|---|---|---|"]
    for c in corrections:
        table.append(f"| {html.escape(c.item)} | {html.escape(c.before)} | {html.escape(c.after)} |")
    st.markdown("\n".join(table))

    with st.expander("교정 근거 보기", expanded=False):
        for c in corrections:
            if c.note:
                st.markdown(f"- **{c.item}**: {c.note}")


if st.button("검증하기", use_container_width=True):
    if not user_text.strip():
        st.warning("검증할 내용을 입력해 주세요.")
        st.stop()

    selected_mode = guess_mode(user_text) if mode == "자동 판정" else mode
    if selected_mode == "본문 내 인용":
        corrections, fixed_text = check_in_text(user_text)
    else:
        corrections, fixed_text = check_references(user_text)

    st.markdown("## 🔍 검증 결과")
    st.markdown(f"- **검증 유형**: {selected_mode}")
    st.markdown(f"- **상태**: {'✅ 대체로 정확함' if not corrections else '🔺 교정 필요'}")
    st.markdown("- **주의**: 수정 전과 수정 후가 완전히 동일한 항목은 교정 내역에서 자동 제외됩니다.")

    render_corrections(corrections)

    st.markdown("### ✍️ 최종 권장 표기")
    st.code(fixed_text, language="markdown")

st.markdown("---")
st.caption("※ 본 도구는 학과 지침에 따른 1차 형식 검토용입니다. 최종 제출 전 지도교수 및 학과 지침서를 확인하세요.")
