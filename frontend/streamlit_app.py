"""
streamlit_app.py  —  궁합냥멍 프론트엔드
실행: streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import requests

API_URL = "http://localhost:5000"

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

MBTI_DESC = {
    "ENFP": "열정적인 활동가", "ENFJ": "정의로운 사회운동가",
    "ENTP": "뜨거운 논쟁을 즐기는 변론가", "ENTJ": "대담한 통솔자",
    "ESFP": "자유로운 영혼의 연예인", "ESFJ": "사교적인 외교관",
    "ESTP": "모험을 즐기는 사업가", "ESTJ": "엄격한 관리자",
    "INFP": "열정적인 중재자", "INFJ": "선의의 옹호자",
    "INTP": "논리적인 사색가", "INTJ": "용의주도한 전략가",
    "ISFP": "호기심 많은 예술가", "ISFJ": "용감한 수호자",
    "ISTP": "만능 재주꾼", "ISTJ": "청렴결백한 논리주의자",
}

RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}

# SVG 일러스트
CAT_SVG = """
<svg width="90" height="90" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- 귀 -->
  <polygon points="18,32 10,10 30,24" fill="#ffb3c6"/>
  <polygon points="72,32 80,10 60,24" fill="#ffb3c6"/>
  <polygon points="20,30 14,14 28,25" fill="#ff85a1"/>
  <polygon points="70,30 76,14 62,25" fill="#ff85a1"/>
  <!-- 얼굴 -->
  <ellipse cx="45" cy="52" rx="30" ry="26" fill="#ffe0ec"/>
  <!-- 눈 -->
  <ellipse cx="34" cy="47" rx="5" ry="6" fill="#333"/>
  <ellipse cx="56" cy="47" rx="5" ry="6" fill="#333"/>
  <circle cx="36" cy="45" r="2" fill="white"/>
  <circle cx="58" cy="45" r="2" fill="white"/>
  <!-- 코 -->
  <ellipse cx="45" cy="56" rx="3" ry="2" fill="#ff85a1"/>
  <!-- 입 -->
  <path d="M42 58 Q45 62 48 58" stroke="#ff85a1" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <!-- 수염 -->
  <line x1="20" y1="54" x2="38" y2="56" stroke="#ccc" stroke-width="1" stroke-linecap="round"/>
  <line x1="20" y1="58" x2="38" y2="58" stroke="#ccc" stroke-width="1" stroke-linecap="round"/>
  <line x1="52" y1="56" x2="70" y2="54" stroke="#ccc" stroke-width="1" stroke-linecap="round"/>
  <line x1="52" y1="58" x2="70" y2="58" stroke="#ccc" stroke-width="1" stroke-linecap="round"/>
  <!-- 볼터치 -->
  <ellipse cx="30" cy="58" rx="6" ry="3" fill="#ffb3c6" opacity="0.5"/>
  <ellipse cx="60" cy="58" rx="6" ry="3" fill="#ffb3c6" opacity="0.5"/>
</svg>"""

DOG_SVG = """
<svg width="90" height="90" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- 귀 -->
  <ellipse cx="20" cy="40" rx="12" ry="18" fill="#c8976e" transform="rotate(-15 20 40)"/>
  <ellipse cx="70" cy="40" rx="12" ry="18" fill="#c8976e" transform="rotate(15 70 40)"/>
  <ellipse cx="20" cy="40" rx="8" ry="13" fill="#e8b48a" transform="rotate(-15 20 40)"/>
  <ellipse cx="70" cy="40" rx="8" ry="13" fill="#e8b48a" transform="rotate(15 70 40)"/>
  <!-- 얼굴 -->
  <ellipse cx="45" cy="50" rx="29" ry="26" fill="#e8c9a0"/>
  <!-- 눈 -->
  <ellipse cx="34" cy="44" rx="5" ry="5.5" fill="#333"/>
  <ellipse cx="56" cy="44" rx="5" ry="5.5" fill="#333"/>
  <circle cx="36" cy="42" r="2" fill="white"/>
  <circle cx="58" cy="42" r="2" fill="white"/>
  <!-- 코 부분 -->
  <ellipse cx="45" cy="56" rx="13" ry="9" fill="#d4a574"/>
  <!-- 코 -->
  <ellipse cx="45" cy="53" rx="5" ry="3.5" fill="#555"/>
  <ellipse cx="44" cy="52" rx="2" ry="1" fill="#777" opacity="0.5"/>
  <!-- 입 -->
  <path d="M40 58 Q45 63 50 58" stroke="#555" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <line x1="45" y1="57" x2="45" y2="60" stroke="#555" stroke-width="1.5" stroke-linecap="round"/>
  <!-- 볼터치 -->
  <ellipse cx="28" cy="56" rx="7" ry="3.5" fill="#e8a0a0" opacity="0.4"/>
  <ellipse cx="62" cy="56" rx="7" ry="3.5" fill="#e8a0a0" opacity="0.4"/>
</svg>"""

BG_DECO = """
<style>
.bg-animals {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0; overflow: hidden;
}
.bg-pet {
    position: absolute;
    opacity: 0.07;
    animation: float 6s ease-in-out infinite;
}
.bg-pet:nth-child(2) { animation-delay: 1s; }
.bg-pet:nth-child(3) { animation-delay: 2s; }
.bg-pet:nth-child(4) { animation-delay: 3s; }
.bg-pet:nth-child(5) { animation-delay: 1.5s; }
.bg-pet:nth-child(6) { animation-delay: 2.5s; }
@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50%       { transform: translateY(-12px) rotate(3deg); }
}
</style>
<div class="bg-animals">
  <div class="bg-pet" style="top:5%;left:3%;font-size:80px;">🐱</div>
  <div class="bg-pet" style="top:8%;right:4%;font-size:70px;">🐶</div>
  <div class="bg-pet" style="top:30%;left:1%;font-size:55px;">🐾</div>
  <div class="bg-pet" style="top:55%;right:2%;font-size:65px;">🐱</div>
  <div class="bg-pet" style="bottom:15%;left:4%;font-size:70px;">🐶</div>
  <div class="bg-pet" style="bottom:5%;right:5%;font-size:50px;">🐾</div>
</div>
"""

def calc_mbti(answers):
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
    for pos, neg in [("E","I"),("S","N"),("T","F"),("J","P")]:
        result += pos if scores[pos] >= scores[neg] else neg
    return result

def call_top3(user_mbti, species):
    try:
        res = requests.post(f"{API_URL}/match/top3",
                            json={"user_mbti": user_mbti, "species": species},
                            timeout=10)
        return res.json()
    except:
        return {"error": "서버 연결 실패"}

def call_one(user_mbti, desertion_no):
    try:
        res = requests.post(f"{API_URL}/match/one",
                            json={"user_mbti": user_mbti, "desertionNo": desertion_no},
                            timeout=10)
        return res.json()
    except:
        return {"error": "서버 연결 실패"}

# ── 페이지 설정 & CSS ─────────────────────────────────────────────────────────

st.set_page_config(page_title="궁합냥멍", page_icon="🐾", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.stApp { background: linear-gradient(160deg, #fff5f8 0%, #ffeef8 40%, #f0f4ff 100%); }

.hero { text-align:center; padding:2rem 0 0.5rem; position:relative; z-index:1; }
.hero-title {
    font-size:2.8rem; font-weight:900;
    background: linear-gradient(135deg, #ff6b9d, #c44dff, #4d79ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; margin:0; line-height:1.2;
}
.hero-sub { color:#999; font-size:1rem; margin-top:0.4rem; }

.hero-pets { display:flex; justify-content:center; gap:1rem; margin:1rem 0 0.5rem; }

.species-card {
    background:white; border-radius:24px; padding:2.2rem 1rem;
    text-align:center; box-shadow:0 8px 30px rgba(0,0,0,0.08);
    border:2px solid transparent; transition:all 0.3s;
}
.species-card:hover {
    border-color:#ff6b9d; transform:translateY(-6px);
    box-shadow:0 16px 40px rgba(255,107,157,0.2);
}
.species-icon { font-size:4.5rem; display:block; margin-bottom:0.6rem; }
.species-name { font-size:1.3rem; font-weight:700; color:#333; }
.species-sub  { font-size:0.82rem; color:#aaa; margin-top:0.2rem; }

.q-wrap {
    background:white; border-radius:18px; padding:1.3rem 1.6rem;
    margin-bottom:0.8rem; box-shadow:0 4px 16px rgba(0,0,0,0.05);
    border-left:4px solid #ff6b9d; position:relative; z-index:1;
}
.q-num  { color:#ff6b9d; font-size:0.78rem; font-weight:700; letter-spacing:0.1em; }
.q-text { color:#333; font-size:1.05rem; font-weight:500; margin-top:0.3rem; }

.mbti-wrap { text-align:center; padding:1.8rem 0 1.2rem; position:relative; z-index:1; }
.mbti-badge {
    display:inline-block;
    background:linear-gradient(135deg, #ff6b9d, #c44dff);
    color:white; font-size:2.6rem; font-weight:900;
    padding:0.5rem 2rem; border-radius:50px;
    box-shadow:0 8px 24px rgba(196,77,255,0.3); letter-spacing:0.05em;
}
.mbti-type-name { color:#c44dff; font-size:1rem; font-weight:500; margin-top:0.5rem; }

.result-card {
    background:white; border-radius:22px; padding:1.4rem 1.5rem;
    margin-bottom:1rem; box-shadow:0 6px 24px rgba(0,0,0,0.07);
    border:1px solid #f0e0ff; transition:transform 0.2s; position:relative; z-index:1;
}
.result-card:hover {
    transform:translateY(-3px);
    box-shadow:0 12px 32px rgba(196,77,255,0.12);
}
.animal-name { color:#333; font-size:1.1rem; font-weight:700; }
.animal-mbti-tag {
    display:inline-block;
    background:linear-gradient(135deg, #ffe0f0, #f0e0ff);
    color:#c44dff; border-radius:20px; padding:0.18rem 0.8rem;
    font-size:0.82rem; font-weight:700; margin-left:0.4rem;
}
.score-label { color:#aaa; font-size:0.8rem; margin-bottom:3px; }
.score-val   { color:#ff6b9d; font-weight:700; font-size:0.88rem; }
.score-bg    { background:#f5f0ff; border-radius:10px; height:7px; margin:3px 0 7px; }
.score-fill  { background:linear-gradient(90deg, #ff6b9d, #c44dff); border-radius:10px; height:7px; }
.comment-txt { color:#c44dff; font-size:0.88rem; font-style:italic; margin:0.3rem 0; }
.care-txt    { color:#bbb; font-size:0.8rem; margin-top:0.3rem; }

.stButton > button {
    background:linear-gradient(135deg, #ff6b9d, #c44dff) !important;
    color:white !important; font-weight:700 !important;
    border:none !important; border-radius:14px !important;
    padding:0.75rem 1.5rem !important; font-size:1rem !important;
    transition:all 0.2s !important;
    box-shadow:0 4px 16px rgba(196,77,255,0.25) !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 24px rgba(196,77,255,0.35) !important;
}
.stProgress > div > div { background:linear-gradient(90deg, #ff6b9d, #c44dff) !important; }
.stRadio label { color:#555 !important; font-size:0.93rem !important; }
div[data-testid="stRadio"] > div { gap:0.5rem !important; }
</style>
""", unsafe_allow_html=True)

# 배경 동물 데코
st.markdown(BG_DECO, unsafe_allow_html=True)

# ── 세션 초기화 ───────────────────────────────────────────────────────────────

if "step" not in st.session_state:
    st.session_state.step      = 1
    st.session_state.species   = None
    st.session_state.answers   = []
    st.session_state.user_mbti = None
    st.session_state.results   = None

# ── 공통 헤더 ─────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="hero">
  <div class="hero-title">궁합냥멍 🐾</div>
  <div class="hero-sub">나의 MBTI로 찾는 나만의 유기동물 친구</div>
  <div class="hero-pets">
    {CAT_SVG}
    {DOG_SVG}
  </div>
</div>
""", unsafe_allow_html=True)

# ── 1단계: 종 선택 ────────────────────────────────────────────────────────────

if st.session_state.step == 1:
    st.markdown("<h3 style='text-align:center;color:#666;margin:0.5rem 0 1.5rem;font-weight:500;'>어떤 친구를 찾고 있나요? 🔍</h3>",
                unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""
        <div class="species-card">
          <span class="species-icon">🐶</span>
          <div class="species-name">강아지</div>
          <div class="species-sub">활발하고 충성스러운</div>
        </div>""", unsafe_allow_html=True)
        if st.button("강아지랑 궁합 보기 🐶", use_container_width=True, key="dog"):
            st.session_state.species = "dog"
            st.session_state.step    = 2
            st.rerun()
    with col2:
        st.markdown("""
        <div class="species-card">
          <span class="species-icon">🐱</span>
          <div class="species-name">고양이</div>
          <div class="species-sub">독립적이고 도도한</div>
        </div>""", unsafe_allow_html=True)
        if st.button("고양이랑 궁합 보기 🐱", use_container_width=True, key="cat"):
            st.session_state.species = "cat"
            st.session_state.step    = 2
            st.rerun()

# ── 2단계: MBTI 설문 ──────────────────────────────────────────────────────────

elif st.session_state.step == 2:
    species_emoji = "🐶" if st.session_state.species == "dog" else "🐱"
    st.markdown(f"<h3 style='color:#333;margin-bottom:0.2rem;'>MBTI 검사 {species_emoji}</h3>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#aaa;font-size:0.87rem;margin-bottom:1.2rem;'>솔직하게 답할수록 더 잘 맞는 친구를 찾을 수 있어요!</p>",
                unsafe_allow_html=True)

    answers = []
    for i, (axis, question, o1, o2, o3, o4) in enumerate(QUESTIONS):
        st.markdown(f"""
        <div class="q-wrap">
          <div class="q-num">Q {i+1} / {len(QUESTIONS)}</div>
          <div class="q-text">{question}</div>
        </div>""", unsafe_allow_html=True)
        ans = st.radio("", [o1, o2, o3, o4], key=f"q{i}",
                       horizontal=True, label_visibility="collapsed")
        answers.append(ans)

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(1.0)
    st.markdown("<p style='color:#c44dff;text-align:center;font-size:0.88rem;margin-bottom:1rem;'>✨ 모든 문항 완료! 결과를 확인해보세요</p>",
                unsafe_allow_html=True)

    if st.button("내 궁합 동물 찾기 ✨", use_container_width=True):
        mbti = calc_mbti(answers)
        st.session_state.user_mbti = mbti
        st.session_state.answers   = answers
        with st.spinner("나와 찰떡궁합인 동물을 찾는 중이에요 🐾"):
            data = call_top3(mbti, st.session_state.species)
        st.session_state.results = data
        st.session_state.step    = 3
        st.rerun()

# ── 3단계: 결과 ───────────────────────────────────────────────────────────────

elif st.session_state.step == 3:
    mbti          = st.session_state.user_mbti
    results       = st.session_state.results
    species_label = "강아지" if st.session_state.species == "dog" else "고양이"
    desc          = MBTI_DESC.get(mbti, "")
    pet_svg       = DOG_SVG if st.session_state.species == "dog" else CAT_SVG

    st.markdown(f"""
    <div class="mbti-wrap">
      {pet_svg}
      <p style="color:#aaa;font-size:0.88rem;margin:0.8rem 0 0.4rem;">나의 MBTI는</p>
      <div class="mbti-badge">{mbti}</div>
      <div class="mbti-type-name">✦ {desc} ✦</div>
      <p style="color:#bbb;font-size:0.83rem;margin-top:0.8rem;">
        나와 잘 맞는 {species_label} TOP 3를 찾았어요! 🎉
      </p>
    </div>
    """, unsafe_allow_html=True)

    if "error" in results:
        st.error(results["error"])
    else:
        for r in results.get("results", []):
            rank  = r["rank"]
            score = r["score"]
            st.markdown(f"""
            <div class="result-card">
              <div style="margin-bottom:0.6rem;">{RANK_EMOJI.get(rank,rank)}</div>
              <div>
                <span class="animal-name">{r.get('kindNm','')}</span>
                <span class="animal-mbti-tag">{r.get('mbti','')}</span>
              </div>
              <div style="margin:0.7rem 0 0.3rem;">
                <div style="display:flex;justify-content:space-between;">
                  <span class="score-label">궁합 점수</span>
                  <span class="score-val">{score}점 💕</span>
                </div>
                <div class="score-bg">
                  <div class="score-fill" style="width:{score}%;"></div>
                </div>
              </div>
              <div class="comment-txt">"{r.get('comment','')}"</div>
              <div class="care-txt">📍 {r.get('careNm','')} &nbsp;|&nbsp; 📞 {r.get('careTel','')}</div>
              <div class="care-txt">{r.get('careAddr','')}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🔍 자세한 궁합 보기", key=f"detail_{r['desertionNo']}"):
                with st.spinner("궁합 계산 중... 💕"):
                    detail = call_one(mbti, r["desertionNo"])
                st.success(f"💕 궁합 점수: {detail.get('score',0)}점 — {detail.get('comment','')}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 다시 테스트하기", use_container_width=True):
        for key in ["step","species","answers","user_mbti","results"]:
            del st.session_state[key]
        st.rerun()