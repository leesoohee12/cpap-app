import math
import re
import statistics
import streamlit as st

st.set_page_config(page_title="양압기 사용 기록 살펴보기")
st.title("양압기 사용 기록 살펴보기")
st.caption("개인별 변화 탐지 · 설명형 피드백 앱 — 첫 번째 버전")

st.info(
    "가상 기록으로 기능을 확인하는 연구용 앱입니다. "
    "6시간과 Z점수 −2는 연구용 기준이며, "
    "분석 결과는 치료 효과나 건강 위험을 뜻하지 않습니다."
)

st.subheader("1. 사용 기록 입력")
st.write(
    "오늘을 제외한 이전 20일의 사용시간을 입력하세요. "
    "단위는 시간이며, 7시간 30분은 7.5로 입력합니다."
)

example = (
    "8, 8.5, 7.5, 8, 8.5, 7.5, 8, 8.5, 7.5, 8, "
    "8.5, 7.5, 8, 8.5, 7.5, 8, 8.5, 7.5, 8, 8"
)

raw = st.text_area(
    "이전 20일 사용시간 — 쉼표나 줄바꿈으로 구분",
    value=example,
    height=120,
)

today = st.number_input(
    "오늘 사용시간",
    min_value=0.0,
    max_value=24.0,
    value=6.5,
    step=0.1,
)

try:
    parts = re.split(r"[,\s]+", raw.strip())
    records = [float(p) for p in parts if p]
except ValueError:
    st.error("숫자와 구분 기호만 입력하세요. 예: 8, 7.5, 8.5")
    st.stop()

if any(not math.isfinite(x) or not 0 <= x <= 24 for x in records):
    st.error("사용시간은 0~24 사이의 유한한 숫자로 입력하세요.")
    st.stop()

st.caption(f"입력된 기준 기록: {len(records)}일")

if len(records) != 20:
    st.warning(
        "분석을 보류합니다. 이번 버전은 이전 20일 기록이 필요합니다. "
        "누락된 기록을 임의로 0으로 채우지 마세요."
    )
    st.stop()

mean = statistics.mean(records)
sd = statistics.stdev(records)
change = today - mean
def time_text(hours):
    total_minutes = round(abs(hours) * 60)
    h, m = divmod(total_minutes, 60)

    if h == 0:
        return f"{m}분"
    if m == 0:
        return f"{h}시간"
    return f"{h}시간 {m}분"


def change_text(hours):
    if hours < 0:
        return f"−{time_text(hours)}"
    if hours > 0:
        return f"+{time_text(hours)}"
    return "0분"
# 두 기준의 판단 결과를 각각 보존합니다.
a = int(today < 6.0)
b = None if sd == 0 else int((today - mean) / sd <= -2.0)
z = None if sd == 0 else (today - mean) / sd
c = None if b is None else a + b

st.subheader("2. 평소 기록과 비교")
col1, col2, col3 = st.columns(3)
col1.metric("이전 20일 평균", time_text(mean))
col2.metric("오늘 사용시간", time_text(today))
col3.metric("평균과의 차이", change_text(change))
st.caption("시간·분 표시는 분 단위로 반올림하며, 판단에는 반올림 전 값을 사용합니다.")

st.subheader("3. 오늘 기록의 의미")

if change < 0:
    st.write(
        f"오늘은 이전 20일 평균보다 **{time_text(change)} 적게** 사용했습니다."
    )
elif change > 0:
    st.write(
        f"오늘은 이전 20일 평균보다 **{time_text(change)} 많이** 사용했습니다."
    )
else:
    st.write("오늘 사용시간은 **이전 20일 평균과 같습니다.**")

with st.expander("왜 이런 결과가 나타났나요?", expanded=True):
    if b is None:
        st.write(
            "이전 20일의 사용시간이 모두 같아 "
            "평소 변동 폭을 기준으로 한 판단은 보류합니다. "
            "평균과의 시간 차이만 확인할 수 있습니다."
        )
        st.write(
            "오늘 사용시간은 "
            + ("연구용 공통 기준인 6시간 미만입니다."
               if a else "연구용 공통 기준인 6시간 이상입니다.")
        )
    elif a and b:
        st.write(
            "오늘은 6시간 미만 사용했으며, "
            "평소 변동 폭을 고려해도 크게 감소했습니다. "
            "두 연구용 기준에 모두 해당합니다."
        )
    elif a:
        st.write(
            "오늘은 6시간 미만 사용했습니다. "
            "다만 평소 변동 폭을 고려한 큰 감소 기준에는 "
            "해당하지 않습니다."
        )
    elif b:
        st.write(
            "오늘은 6시간 이상 사용했습니다. "
            "다만 평소 변동 폭을 고려하면 "
            "사용시간이 크게 감소한 경우에 해당합니다."
        )
    else:
        st.write("오늘 기록은 두 연구용 탐지 기준에 모두 해당하지 않습니다.")

st.caption(
    "이 설명은 사용시간 기록에 관한 것입니다. "
    "해당 기준의 수가 많다고 건강이 더 나쁘다는 뜻은 아니며, "
    "기준에 해당하지 않는다고 건강 상태가 좋다는 뜻도 아닙니다."
)

with st.expander("계산 과정 보기"):
    st.write(f"개인 평균: {mean:.4f}시간")
    st.write(f"표본표준편차: {sd:.4f}시간")
    st.write(f"A · 오늘 사용시간 6시간 미만: {a}")

    if z is None:
        st.write("표본표준편차가 0이므로 Z점수, B, C의 판단을 보류합니다.")
    else:
        st.write("Z점수 = (오늘 사용시간 − 개인 평균) ÷ 표본표준편차")
        st.write(f"Z점수: {z:.4f}")
        st.write(f"B · Z점수 −2 이하: {b}")
        st.write(f"C = A + B: {c}")
        st.write(f"두 연구용 기준 중 해당하는 기준 수: {c}개")
        st.caption(
            "C는 건강 위험 점수가 아닙니다. "
            "C=1일 때도 A만 해당하는 경우와 B만 해당하는 경우가 다릅니다."
        )

    st.caption("판단에는 반올림하기 전 계산값을 사용합니다.")
