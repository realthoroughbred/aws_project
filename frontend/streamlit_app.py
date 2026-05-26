"""
streamlit_app.py  —  궁합냥멍 프론트엔드
실행: 프로젝트 루트 또는 frontend에서 `streamlit run frontend/streamlit_app.py` (둘 다 `frontend/.streamlit` 또는 루트 `.streamlit`의 라이트 테마 적용)
"""

import os

import streamlit as st
import requests
import base64
from pathlib import Path
from urllib.parse import quote

API_URL = os.environ.get("API_URL", "http://localhost:5000").rstrip("/")

def _pets_hero_img_html() -> str:
    _png = Path(__file__).resolve().parent / "assets" / "pets_hero.png"
    _b64 = base64.b64encode(_png.read_bytes()).decode("ascii")
    return f'<img src="data:image/png;base64,{_b64}" style="width:320px;max-width:90%;margin:0.8rem auto 0;display:block;">'


PETS_IMG = _pets_hero_img_html()

PLACEHOLDER_IMG = 'data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20width%3D%27800%27%20height%3D%27500%27%3E%3Crect%20width%3D%27100%25%27%20height%3D%27100%25%27%20fill%3D%27%23f7edf9%27/%3E%3Ctext%20x%3D%2750%25%27%20y%3D%2746%25%27%20text-anchor%3D%27middle%27%20fill%3D%27%23c44dff%27%20font-size%3D%2744%27%3E%F0%9F%90%BE%3C/text%3E%3Ctext%20x%3D%2750%25%27%20y%3D%2758%25%27%20text-anchor%3D%27middle%27%20fill%3D%27%239a72c7%27%20font-size%3D%2728%27%3E%EC%82%AC%EC%A7%84%20%EC%A4%80%EB%B9%84%20%EC%A4%91%3C/text%3E%3C/svg%3E'

DOG_IMAGES = ["assets/dogs/dog_1.png","assets/dogs/dog_2.png","assets/dogs/dog_3.png","assets/dogs/dog_4.png","assets/dogs/dog_5.png"]
CAT_IMAGES = ["assets/cats/cat_1.png","assets/cats/cat_2.png","assets/cats/cat_3.png","assets/cats/cat_4.png","assets/cats/cat_5.png"]

def pick_local_pet_image(desertion_no, species):
    pool = DOG_IMAGES if species == "dog" else CAT_IMAGES if species == "cat" else []
    if not pool: return None
    seed = sum(ord(c) for c in (desertion_no or "pet"))
    return pool[seed % len(pool)]

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

# 동물 등록 설문 문항
ANIMAL_QUESTIONS = [
    {
        "key": "social",
        "question": "사람을 대하는 태도는?",
        "options": ["매우 잘 따름 🐾", "잘 따르는 편", "경계하는 편", "매우 경계함 😰"],
        "axis": "EI",
        "scores": [2, 1, -1, -2],
    },
    {
        "key": "active",
        "question": "활동성은?",
        "options": ["매우 활발함 🏃", "활발한 편", "조용한 편", "매우 조용함 😴"],
        "axis": "SN",
        "scores": [2, 1, -1, -2],
    },
    {
        "key": "affection",
        "question": "애정 표현은?",
        "options": ["매우 많음 💕", "있는 편", "적은 편", "거의 없음"],
        "axis": "TF",
        "scores": [2, 1, -1, -2],
    },
    {
        "key": "routine",
        "question": "생활 패턴은?",
        "options": ["매우 규칙적 🕐", "규칙적인 편", "즉흥적인 편", "매우 즉흥적 🎲"],
        "axis": "JP",
        "scores": [2, 1, -1, -2],
    },
    {
        "key": "curious",
        "question": "새로운 환경에 대한 반응은?",
        "options": ["매우 호기심 많음 👀", "호기심 있는 편", "조심스러운 편", "매우 무서워함 😱"],
        "axis": "SN",
        "scores": [2, 1, -1, -2],
    },
    {
        "key": "independent",
        "question": "독립성은?",
        "options": ["매우 독립적 🦅", "독립적인 편", "의존적인 편", "매우 의존적 🐣"],
        "axis": "TF",
        "scores": [-2, -1, 1, 2],
    },
]

def predict_animal_mbti(answers: dict) -> str:
    """설문 답변으로 동물 MBTI 예측"""
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for q in ANIMAL_QUESTIONS:
        key   = q["key"]
        axis  = q["axis"]
        score = q["scores"][answers.get(key, 0)]
        pos, neg = axis[0], axis[1]
        if score > 0: scores[pos] += score
        else:         scores[neg] += abs(score)
    result = ""
    for pos, neg in [("E","I"),("S","N"),("T","F"),("J","P")]:
        result += pos if scores[pos] >= scores[neg] else neg
    return result

BG_DECO = """
<style>
.bg-animals { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:0; overflow:hidden; }
.bg-pet { position:absolute; opacity:0.06; animation:float 7s ease-in-out infinite; }
.bg-pet:nth-child(2){animation-delay:1.5s;}
.bg-pet:nth-child(3){animation-delay:3s;}
.bg-pet:nth-child(4){animation-delay:2s;}
.bg-pet:nth-child(5){animation-delay:4s;}
.bg-pet:nth-child(6){animation-delay:0.5s;}
@keyframes float{0%,100%{transform:translateY(0) rotate(0deg);}50%{transform:translateY(-14px) rotate(4deg);}}
</style>
<div class="bg-animals">
  <div class="bg-pet" style="top:3%;left:2%;font-size:90px;">🐱</div>
  <div class="bg-pet" style="top:6%;right:3%;font-size:80px;">🐶</div>
  <div class="bg-pet" style="top:28%;left:0%;font-size:60px;">🐾</div>
  <div class="bg-pet" style="top:52%;right:1%;font-size:75px;">🐱</div>
  <div class="bg-pet" style="bottom:14%;left:3%;font-size:80px;">🐶</div>
  <div class="bg-pet" style="bottom:4%;right:4%;font-size:55px;">🐾</div>
</div>
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
/* 밝은 UI 유지: 다크 테마/시스템 다크에서도 글자가 밝은 배경 위에서 읽히게 */
.stApp {
  background: linear-gradient(160deg, #fff5f8 0%, #ffeef8 40%, #f0f4ff 100%);
  color: #262730;
  color-scheme: light;
}
[data-testid="stAppViewContainer"] { color: #262730; }
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6 { color: #333 !important; }
[data-testid="stMarkdownContainer"] p:not([style]) { color: #262730 !important; }
.stTabs [data-baseweb="tab"] { color: #444 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #c44dff !important; }
label[data-testid="stWidgetLabel"] p,
.stTextInput label p,
.stTextArea label p,
.stSelectbox label p { color: #333 !important; }
.stTextInput input,
.stTextArea textarea {
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  background-color: #ffffff !important;
}
/* ── Select (Streamlit 1.33+ : Styletron, class .stSelectbox — Base Web 아님) ── */
[data-testid="stSelectbox"] div[role="combobox"],
.stSelectbox div[role="combobox"],
[data-testid="stMain"] div[role="combobox"],
[data-testid="stAppViewContainer"] div[role="combobox"] {
  background-color: #ffffff !important;
  background-image: none !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  border-color: rgba(49, 51, 63, 0.28) !important;
  box-shadow: none !important;
}
[data-testid="stSelectbox"] div[role="combobox"] *,
.stSelectbox div[role="combobox"] * {
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
}
/* 접힌 상태 선택 문구: combobox 바깥·role 없는 Styletron div까지 포함 */
[data-testid="stSelectbox"] div,
.stSelectbox div {
  background-color: #ffffff !important;
  background-image: none !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  opacity: 1 !important;
}
[data-testid="stSelectbox"] span,
.stSelectbox span {
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  opacity: 1 !important;
}
[data-testid="stSelectbox"] input,
.stSelectbox input {
  background-color: #ffffff !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
}
[data-testid="stSelectbox"] div[role="listbox"],
.stSelectbox div[role="listbox"],
[data-testid="stSelectbox"] ul[role="listbox"],
.stSelectbox ul[role="listbox"] {
  background-color: #ffffff !important;
  color: #262730 !important;
  border: 1px solid rgba(49, 51, 63, 0.2) !important;
}
[data-testid="stSelectbox"] li[role="option"],
.stSelectbox li[role="option"],
div[role="listbox"] li[role="option"] {
  background-color: #ffffff !important;
  color: #262730 !important;
}
[data-testid="stSelectbox"] li[role="option"]:hover,
.stSelectbox li[role="option"]:hover,
div[role="listbox"] li[role="option"]:hover {
  background-color: #fff0f5 !important;
}
/* 구버전 Base Web select (혹시 남아 있으면) */
.stSelectbox [data-baseweb="select"],
.stSelectbox [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
  background-color: #ffffff !important;
  background-image: none !important;
  color: #262730 !important;
  border-color: rgba(49, 51, 63, 0.25) !important;
  -webkit-text-fill-color: #262730 !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] p,
.stSelectbox [data-baseweb="select"] div[role="combobox"],
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] p {
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
}
.stSelectbox svg,
[data-testid="stSelectbox"] svg { fill: #31333F !important; }
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] ul {
  background-color: #ffffff !important;
}
div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {
  color: #262730 !important;
  background-color: #ffffff !important;
}
div[data-baseweb="popover"] li:hover,
div[data-baseweb="menu"] li:hover {
  background-color: #fff0f5 !important;
}
.hero { text-align:center; padding:2rem 0 0.5rem; position:relative; z-index:1; }
.hero-title { font-size:2.8rem; font-weight:900; background:linear-gradient(135deg, #ff6b9d, #c44dff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0; line-height:1.2; }
.hero-sub { color:#999; font-size:1rem; margin-top:0.4rem; }
.species-card { background:white; border-radius:24px; padding:2.2rem 1rem; text-align:center; box-shadow:0 8px 30px rgba(0,0,0,0.08); border:2px solid transparent; transition:all 0.3s; }
.species-card:hover { border-color:#ff6b9d; transform:translateY(-6px); box-shadow:0 16px 40px rgba(255,107,157,0.2); }
.species-icon { font-size:4.5rem; display:block; margin-bottom:0.6rem; }
.species-name { font-size:1.3rem; font-weight:700; color:#333; }
.species-sub  { font-size:0.82rem; color:#aaa; margin-top:0.2rem; }
.q-wrap { background:white; border-radius:18px; padding:1.3rem 1.6rem; margin-bottom:0.8rem; box-shadow:0 4px 16px rgba(0,0,0,0.05); border-left:4px solid #ff6b9d; position:relative; z-index:1; }
.q-num  { color:#ff6b9d; font-size:0.78rem; font-weight:700; letter-spacing:0.1em; }
.q-text { color:#333; font-size:1.05rem; font-weight:500; margin-top:0.3rem; }
.reg-card { background:white; border-radius:18px; padding:1.3rem 1.6rem; margin-bottom:0.8rem; box-shadow:0 4px 16px rgba(0,0,0,0.05); border-left:4px solid #c44dff; position:relative; z-index:1; }
.reg-num  { color:#c44dff; font-size:0.78rem; font-weight:700; letter-spacing:0.1em; }
.reg-text { color:#333; font-size:1.05rem; font-weight:500; margin-top:0.3rem; }
.mbti-wrap { text-align:center; padding:1.5rem 0 1rem; position:relative; z-index:1; }
.mbti-badge { display:inline-block; background:linear-gradient(135deg, #ff6b9d, #c44dff); color:white; font-size:2.6rem; font-weight:900; padding:0.5rem 2rem; border-radius:50px; box-shadow:0 8px 24px rgba(196,77,255,0.3); letter-spacing:0.05em; }
.mbti-type-name { color:#c44dff; font-size:1rem; font-weight:500; margin-top:0.5rem; }
.result-card { background:white; border-radius:22px; padding:1.4rem 1.5rem; margin-bottom:1rem; box-shadow:0 6px 24px rgba(0,0,0,0.07); border:1px solid #f0e0ff; transition:transform 0.2s; position:relative; z-index:1; }
.result-card:hover { transform:translateY(-3px); box-shadow:0 12px 32px rgba(196,77,255,0.12); }
.result-img { width:100%; height:220px; object-fit:cover; border-radius:14px; margin-bottom:12px; background:#f3d2ff; }
.animal-name { color:#333; font-size:1.1rem; font-weight:700; }
.animal-mbti-tag { display:inline-block; background:linear-gradient(135deg, #ffe0f0, #f0e0ff); color:#c44dff; border-radius:20px; padding:0.18rem 0.8rem; font-size:0.82rem; font-weight:700; margin-left:0.4rem; }
.score-label { color:#aaa; font-size:0.8rem; margin-bottom:3px; }
.score-val   { color:#ff6b9d; font-weight:700; font-size:0.88rem; }
.score-bg    { background:#f5f0ff; border-radius:10px; height:7px; margin:3px 0 7px; }
.score-fill  { background:linear-gradient(90deg,#ff6b9d,#c44dff); border-radius:10px; height:7px; }
.comment-txt { color:#c44dff; font-size:0.88rem; font-style:italic; margin:0.3rem 0; }
.care-txt    { color:#bbb; font-size:0.8rem; margin-top:0.3rem; }
.stButton > button { background:linear-gradient(135deg,#ff6b9d,#c44dff) !important; color:white !important; font-weight:700 !important; border:none !important; border-radius:14px !important; padding:0.75rem 1.5rem !important; font-size:1rem !important; box-shadow:0 4px 16px rgba(196,77,255,0.25) !important; transition:all 0.2s !important; }
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 24px rgba(196,77,255,0.35) !important; }
.stProgress > div > div > div > div { background:linear-gradient(90deg,#ff6b9d,#c44dff) !important; }
div[data-testid="stRadio"] label p { color: #333 !important; font-size: 0.95rem !important; }
div[data-testid="stRadio"] label { background: #fff0f5 !important; border: 1.5px solid #ffd0e0 !important; border-radius: 10px !important; padding: 0.4rem 1rem !important; }
div[data-testid="stRadio"] > div { gap:0.5rem !important; flex-wrap:wrap !important; }
div[data-testid="stSpinner"] p { color: #c44dff !important; font-weight:600 !important; }
.reg-result-box { background:linear-gradient(135deg,#fff0f5,#f0e8ff); border-radius:20px; padding:2rem; text-align:center; border:2px solid #f0d0ff; margin:1rem 0; }
/* 커스텀 카드 텍스트: 테마 다크여도 밝은 카드 위에서 유지 */
.stApp .hero-sub { color:#999 !important; }
.stApp .species-name { color:#333 !important; }
.stApp .species-sub { color:#aaa !important; }
.stApp .q-text, .stApp .reg-text { color:#333 !important; }
.stApp .q-num { color:#ff6b9d !important; }
.stApp .reg-num { color:#c44dff !important; }
.stApp .animal-name { color:#333 !important; }
.stApp .animal-mbti-tag { color:#c44dff !important; }
.stApp .score-label { color:#aaa !important; }
.stApp .score-val { color:#ff6b9d !important; }
.stApp .comment-txt { color:#c44dff !important; }
.stApp .care-txt { color:#bbb !important; }
.stApp .mbti-type-name { color:#c44dff !important; }
</style>
"""

# Streamlit 기본(Emotion)보다 뒤에서 한 번 더 적용 — Select 드롭다운이 body 쪽 포털로 붙는 경우 포함
THEME_LATE_CSS = """
<style>
/* ── 셀렉트박스 전체 강제 라이트 ── */
[data-testid="stSelectbox"] *,
.stSelectbox * {
  background-color: #ffffff !important;
  background-image: none !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  opacity: 1 !important;
}

/* 드롭다운 팝오버 (body에 포털로 붙는 것) */
[data-baseweb="popover"],
[data-baseweb="popover"] *,
[data-baseweb="menu"],
[data-baseweb="menu"] * {
  background-color: #ffffff !important;
  background-image: none !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
}

[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="menu"] [aria-selected="true"] {
  background-color: #fff0f5 !important;
}

/* listbox 전역 */
body div[role="listbox"],
div[role="listbox"],
div[role="listbox"] * {
  background-color: #ffffff !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  border: 1px solid rgba(49, 51, 63, 0.2) !important;
}

div[role="listbox"] li[role="option"] {
  background-color: #ffffff !important;
  color: #262730 !important;
}

div[role="listbox"] li[role="option"]:hover {
  background-color: #fff0f5 !important;
}

/* combobox 닫힌 상태 */
[data-testid="stSelectbox"] div[role="combobox"],
.stSelectbox div[role="combobox"] {
  background-color: #ffffff !important;
  color: #262730 !important;
  -webkit-text-fill-color: #262730 !important;
  border-color: rgba(49, 51, 63, 0.28) !important;
}
</style>
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
        res = requests.post(f"{API_URL}/match/top3", json={"user_mbti": user_mbti, "species": species}, timeout=60)
        return res.json()
    except requests.exceptions.Timeout:
        return {"error": "서버 응답 시간 초과."}
    except requests.exceptions.ConnectionError as e:
        print(f"[DEBUG] ConnectionError: {e}")  # ← 추가
        return {"error": f"서버 연결 실패: {e}"}
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")  # ← 추가
        return {"error": f"오류: {e}"}

def call_one(user_mbti, desertion_no):
    try:
        res = requests.post(f"{API_URL}/match/one", json={"user_mbti": user_mbti, "desertionNo": desertion_no}, timeout=60)
        return res.json()
    except Exception as e:
        return {"error": f"오류: {e}"}

def call_register(animal_data):
    try:
        res = requests.post(f"{API_URL}/animal/register", json=animal_data, timeout=60)
        return res.json()
    except requests.exceptions.ConnectionError:
        return {"error": "서버 연결 실패."}
    except Exception as e:
        return {"error": f"오류: {e}"}

# ── 앱 시작 ──────────────────────────────────────────────────────────────────

st.set_page_config(page_title="궁합냥멍", page_icon="🐾", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(BG_DECO, unsafe_allow_html=True)

if "step" not in st.session_state:
    st.session_state.step      = 1
    st.session_state.species   = None
    st.session_state.answers   = []
    st.session_state.user_mbti = None
    st.session_state.results   = None

# 헤더
st.markdown(f"""
<div class="hero">
  <div class="hero-title">궁합냥멍 🐾</div>
  <div class="hero-sub">나의 MBTI로 찾는 나만의 유기동물 친구</div>
  {PETS_IMG}
</div>
""", unsafe_allow_html=True)

# 탭
tab1, tab2 = st.tabs(["🐾 궁합 찾기", "🏠 동물 등록 (보호소용)"])

# ── 탭1: 궁합 찾기 ───────────────────────────────────────────────────────────
with tab1:
    if st.session_state.step == 1:
        st.markdown("<h3 style='text-align:center;color:#666;margin:0.5rem 0 1.5rem;font-weight:500;'>어떤 친구를 찾고 있나요? 🔍</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('''<div class="species-card"><span class="species-icon">🐶</span><div class="species-name">강아지</div><div class="species-sub">활발하고 충성스러운</div></div>''', unsafe_allow_html=True)
            if st.button("강아지랑 궁합 보기 🐶", use_container_width=True, key="dog"):
                st.session_state.species = "dog"
                st.session_state.step    = 2
                st.rerun()
        with col2:
            st.markdown('''<div class="species-card"><span class="species-icon">🐱</span><div class="species-name">고양이</div><div class="species-sub">독립적이고 도도한</div></div>''', unsafe_allow_html=True)
            if st.button("고양이랑 궁합 보기 🐱", use_container_width=True, key="cat"):
                st.session_state.species = "cat"
                st.session_state.step    = 2
                st.rerun()

    elif st.session_state.step == 2:
        species_emoji = "🐶" if st.session_state.species == "dog" else "🐱"
        st.markdown(f"<h3 style='color:#333;margin-bottom:0.2rem;'>MBTI 검사 {species_emoji}</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#aaa;font-size:0.87rem;margin-bottom:1.2rem;'>솔직하게 답할수록 더 잘 맞는 친구를 찾을 수 있어요!</p>", unsafe_allow_html=True)
        answers = []
        for i, (axis, question, o1, o2, o3, o4) in enumerate(QUESTIONS):
            st.markdown(f'''<div class="q-wrap"><div class="q-num">Q {i+1} / {len(QUESTIONS)}</div><div class="q-text">{question}</div></div>''', unsafe_allow_html=True)
            ans = st.radio("선택", [o1, o2, o3, o4], key=f"q{i}", horizontal=True, label_visibility="collapsed")
            answers.append(ans)
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(1.0)
        st.markdown("<p style='color:#c44dff;text-align:center;font-size:0.88rem;margin-bottom:1rem;'>✨ 모든 문항 완료! 결과를 확인해보세요</p>", unsafe_allow_html=True)
        if st.button("내 궁합 동물 찾기 ✨", use_container_width=True):
            mbti = calc_mbti(answers)
            st.session_state.user_mbti = mbti
            st.session_state.answers   = answers
            with st.spinner("나와 찰떡궁합인 동물을 찾는 중이에요 🐾"):
                data = call_top3(mbti, st.session_state.species)
            st.session_state.results = data
            st.session_state.step    = 3
            st.rerun()

    elif st.session_state.step == 3:
        mbti          = st.session_state.user_mbti
        results       = st.session_state.results
        species_label = "강아지" if st.session_state.species == "dog" else "고양이"
        desc          = MBTI_DESC.get(mbti, "")
        st.markdown(f"""
        <div class="mbti-wrap">
          <p style="color:#aaa;font-size:0.88rem;margin:0.8rem 0 0.4rem;">나의 MBTI는</p>
          <div class="mbti-badge">{mbti}</div>
          <div class="mbti-type-name">✦ {desc} ✦</div>
          <p style="color:#bbb;font-size:0.83rem;margin-top:0.8rem;">나와 잘 맞는 {species_label} TOP 3를 찾았어요! 🎉</p>
        </div>
        """, unsafe_allow_html=True)
        if "error" in results:
            st.error(results["error"])
        else:
            for r in results.get("results", []):
                rank  = r["rank"]
                score = r["score"]
                image = r.get("image", "")
                if not image or str(image) == "nan":
                    local = pick_local_pet_image(str(r.get("desertionNo","")), r.get("species", st.session_state.species or ""))
                    image = local if local else PLACEHOLDER_IMG
                img_html = f'<img src="{image}" class="result-img" onerror="this.src=\'{PLACEHOLDER_IMG}\'"  >'
                st.markdown(f"""
                <div class="result-card">
                  {img_html}
                  <div style="margin-bottom:0.5rem;">{RANK_EMOJI.get(rank,rank)}</div>
                  <div><span class="animal-name">{r.get("kindNm","")}</span><span class="animal-mbti-tag">{r.get("mbti","")}</span></div>
                  <div style="margin:0.7rem 0 0.3rem;">
                    <div style="display:flex;justify-content:space-between;">
                      <span class="score-label">궁합 점수</span>
                      <span class="score-val">{score}점 💕</span>
                    </div>
                    <div class="score-bg"><div class="score-fill" style="width:{score}%;"></div></div>
                  </div>
                  <div class="comment-txt">"{r.get("comment","")}"</div>
                  <div class="care-txt">📍 {r.get("careNm","")} | 📞 {r.get("careTel","")}</div>
                  <div class="care-txt">{r.get("careAddr","")}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔍 자세한 궁합 보기", key=f"detail_{r['desertionNo']}"):
                    with st.spinner("궁합 계산 중... 💕"):
                        detail = call_one(mbti, r["desertionNo"])
                    st.success(f"💕 궁합 점수: {detail.get('score',0)}점 — {detail.get('comment','')}")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 다시 테스트하기", use_container_width=True):
            for key in ["step","species","answers","user_mbti","results"]:
                del st.session_state[key]
            st.rerun()

# ── 탭2: 동물 등록 ───────────────────────────────────────────────────────────
with tab2:
    st.markdown("<h3 style='color:#333;margin-bottom:0.3rem;'>🏠 새 동물 등록</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#aaa;font-size:0.87rem;margin-bottom:1.5rem;'>동물의 정보와 성격을 입력하면 MBTI를 자동으로 예측해드려요!</p>", unsafe_allow_html=True)

    # 기본 정보
    st.markdown("#### 📋 기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        species_reg = st.selectbox("종류", ["강아지 🐶", "고양이 🐱"], key="reg_species")
        kind_nm     = st.text_input("품종", placeholder="예: 믹스견, 말티즈, 코리안숏헤어", key="reg_kind")
    with col2:
        age         = st.text_input("나이", placeholder="예: 2살, 추정 3년", key="reg_age")
        sex         = st.selectbox("성별", ["수컷 ♂", "암컷 ♀"], key="reg_sex")

    neuter = st.selectbox("중성화 여부", ["완료 ✅", "미완료 ❌", "알 수 없음 ❓"], key="reg_neuter")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏢 보호소 정보")
    col3, col4 = st.columns(2)
    with col3:
        care_nm  = st.text_input("보호소 이름", placeholder="예: 밀양시 동물보호센터", key="reg_care_nm")
        care_tel = st.text_input("전화번호", placeholder="예: 070-4113-7288", key="reg_care_tel")
    with col4:
        care_addr = st.text_input("주소", placeholder="예: 경상남도 밀양시...", key="reg_care_addr")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🐾 성격 체크 (MBTI 예측용)")
    st.markdown("<p style='color:#aaa;font-size:0.85rem;margin-bottom:1rem;'>관찰한 동물의 성격을 체크해주세요!</p>", unsafe_allow_html=True)

    animal_answers = {}
    for i, q in enumerate(ANIMAL_QUESTIONS):
        st.markdown(f'''<div class="reg-card"><div class="reg-num">Q {i+1} / {len(ANIMAL_QUESTIONS)}</div><div class="reg-text">{q["question"]}</div></div>''', unsafe_allow_html=True)
        sel = st.radio("선택", q["options"], key=f"reg_q{i}", horizontal=True, label_visibility="collapsed")
        animal_answers[q["key"]] = q["options"].index(sel)

    st.markdown("<br>", unsafe_allow_html=True)
    special_mark = st.text_area("추가 특이사항 (선택)", placeholder="예: 다른 동물과 잘 어울림, 입양 후 적응 기간 필요 등", key="reg_special", height=100)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🐾 동물 등록 & MBTI 예측하기", use_container_width=True, key="reg_submit"):
        if not kind_nm:
            st.warning("품종을 입력해주세요!")
        elif not age:
            st.warning("나이를 입력해주세요!")
        else:
            predicted_mbti = predict_animal_mbti(animal_answers)
            species_val    = "dog" if "강아지" in species_reg else "cat"
            sex_val        = "M" if "수컷" in sex else "F"
            neuter_val     = "Y" if "완료" in neuter else "N"
            special_full   = special_mark

            animal_data = {
                "kindNm":      kind_nm,
                "age":         age,
                "sexCd":       sex_val,
                "neuterYn":    neuter_val,
                "species":     species_val,
                "specialMark": special_full,
                "careNm":      care_nm,
                "careAddr":    care_addr,
                "careTel":     care_tel,
                "mbti_label":  predicted_mbti,
            }

            with st.spinner("MBTI 예측 중... 🐾"):
                result = call_register(animal_data)

            if "error" in result:
                desc = MBTI_DESC.get(predicted_mbti, "")
                st.markdown(f"""
                <div class="reg-result-box">
                  <p style="color:#aaa;font-size:0.9rem;margin-bottom:0.5rem;">예측된 MBTI</p>
                  <div class="mbti-badge">{predicted_mbti}</div>
                  <div class="mbti-type-name" style="margin-top:0.5rem;">✦ {desc} ✦</div>
                  <p style="color:#bbb;font-size:0.8rem;margin-top:1rem;">⚠️ 서버 연결 실패 — DB 저장은 서버 실행 후 가능해요</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                desc = MBTI_DESC.get(predicted_mbti, "")
                st.markdown(f"""
                <div class="reg-result-box">
                  <p style="color:#aaa;font-size:0.9rem;margin-bottom:0.5rem;">예측된 MBTI</p>
                  <div class="mbti-badge">{predicted_mbti}</div>
                  <div class="mbti-type-name" style="margin-top:0.5rem;">✦ {desc} ✦</div>
                  <p style="color:#5a2bb8;font-size:0.9rem;margin-top:1rem;font-weight:600;">✅ DB에 저장 완료! 이제 궁합 매칭에 반영돼요 🎉</p>
                </div>
                """, unsafe_allow_html=True)

st.markdown(THEME_LATE_CSS, unsafe_allow_html=True)