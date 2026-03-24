"""
streamlit_app.py  —  PawType 프론트엔드
실행: streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import requests

API_URL = "http://localhost:5000"   # EC2 배포 시 실제 주소로 변경

# MBTI 설문 문항
QUESTIONS = [
    ("EI", "처음 보는 사람에게 먼저 말을 건다",            "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("EI", "혼자 있는 시간보다 사람들과 함께하는 게 좋다", "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("EI", "모임에서 분위기를 주도하는 편이다",             "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("SN", "새로운 아이디어를 떠올리는 걸 즐긴다",          "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("SN", "계획보다 즉흥적으로 행동할 때가 많다",          "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("SN", "상상력이 풍부한 편이다",                        "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("TF", "결정할 때 감정보다 논리를 우선시한다",          "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("TF", "친구가 힘들면 조언보다 공감을 먼저 한다",       "매우 아니다", "아니다", "그렇다", "매우 그렇다"),
    ("TF", "타인의 감정에 쉽게 영향을 받는다",              "매우 아니다", "아니다", "그렇다", "매우 그렇다"),
    ("JP", "일을 미리 계획하고 체계적으로 처리한다",        "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
    ("JP", "마감 직전에 일하는 게 더 잘 된다",              "매우 아니다", "아니다", "그렇다", "매우 그렇다"),
    ("JP", "정해진 루틴이 있는 게 편하다",                  "매우 그렇다", "그렇다", "아니다", "매우 아니다"),
]

def calc_mbti(answers: list) -> str:
    scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    for i, (axis, _, o1, o2, o3, o4) in enumerate(QUESTIONS):
        val = answers[i]
        if val == o1:   v = 2
        elif val == o2: v = 1
        elif val == o3: v = -1
        else:           v = -2
        pos, neg = axis[0], axis[1]
        if v > 0:  scores[pos] += v
        else:      scores[neg] += abs(v)

    result = ""
    for pos, neg in [("E","I"), ("S","N"), ("T","F"), ("J","P")]:
        result += pos if scores[pos] >= scores[neg] else neg
    return result

def call_top3(user_mbti: str, species: str) -> dict:
    try:
        res = requests.post(f"{API_URL}/match/top3",
                            json={"user_mbti": user_mbti, "species": species},
                            timeout=10)
        return res.json()
    except:
        return {"error": "서버 연결 실패"}

def call_one(user_mbti: str, desertion_no: str) -> dict:
    try:
        res = requests.post(f"{API_URL}/match/one",
                            json={"user_mbti": user_mbti, "desertionNo": desertion_no},
                            timeout=10)
        return res.json()
    except:
        return {"error": "서버 연결 실패"}

# ── UI ────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="PawType", page_icon="🐾", layout="centered")
st.title("🐾 PawType")
st.caption("나의 MBTI로 찾는 나만의 유기동물")

if "step" not in st.session_state:
    st.session_state.step      = 1
    st.session_state.species   = None
    st.session_state.answers   = []
    st.session_state.user_mbti = None
    st.session_state.results   = None

# ── 1단계: 종 선택 ────────────────────────────────────────────────────────────

if st.session_state.step == 1:
    st.subheader("어떤 동물을 찾고 계신가요?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🐶  강아지", use_container_width=True):
            st.session_state.species = "dog"
            st.session_state.step    = 2
            st.rerun()
    with col2:
        if st.button("🐱  고양이", use_container_width=True):
            st.session_state.species = "cat"
            st.session_state.step    = 2
            st.rerun()

# ── 2단계: MBTI 설문 ──────────────────────────────────────────────────────────

elif st.session_state.step == 2:
    st.subheader("MBTI 검사")
    progress = st.progress(0)
    answers  = []

    for i, (axis, question, o1, o2, o3, o4) in enumerate(QUESTIONS):
        progress.progress((i + 1) / len(QUESTIONS))
        st.markdown(f"**Q{i+1}.** {question}")
        ans = st.radio("", [o1, o2, o3, o4], key=f"q{i}", horizontal=True, label_visibility="collapsed")
        answers.append(ans)
        st.divider()

    if st.button("결과 보기", type="primary", use_container_width=True):
        mbti = calc_mbti(answers)
        st.session_state.user_mbti = mbti
        st.session_state.answers   = answers

        with st.spinner("나와 맞는 동물을 찾는 중..."):
            data = call_top3(mbti, st.session_state.species)

        st.session_state.results = data
        st.session_state.step    = 3
        st.rerun()

# ── 3단계: 결과 ───────────────────────────────────────────────────────────────

elif st.session_state.step == 3:
    mbti    = st.session_state.user_mbti
    results = st.session_state.results

    st.subheader(f"나의 MBTI: **{mbti}**")
    species_label = "강아지" if st.session_state.species == "dog" else "고양이"
    st.caption(f"나와 잘 맞는 {species_label} TOP 3")

    if "error" in results:
        st.error(results["error"])
    else:
        for r in results.get("results", []):
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if r.get("image"):
                        st.image(r["image"], width=120)
                with col2:
                    st.markdown(f"### {r['rank']}위  {r['kindNm']}")
                    st.markdown(f"**MBTI:** {r['mbti']}  |  **궁합:** {r['score']}점")
                    st.markdown(f"*{r['comment']}*")
                    st.caption(f"📍 {r.get('careNm','')}  {r.get('careAddr','')}")
                    st.caption(f"📞 {r.get('careTel','')}")

                # 1:1 궁합 상세 조회
                if st.button(f"자세한 궁합 보기", key=f"detail_{r['desertionNo']}"):
                    with st.spinner("궁합 계산 중..."):
                        detail = call_one(mbti, r["desertionNo"])
                    st.info(f"궁합 점수: {detail.get('score',0)}점  —  {detail.get('comment','')}")

    st.divider()
    if st.button("다시 테스트하기", use_container_width=True):
        for key in ["step","species","answers","user_mbti","results"]:
            del st.session_state[key]
        st.rerun()