"""
matcher.py  —  MBTI 궁합 계산 + 동물 TOP 3 추천
RDS 연결 전 임시: CSV 파일 직접 읽기
"""

import base64
import os
import pickle
from pathlib import Path

import pandas as pd
import requests
from sentence_transformers import SentenceTransformer
from train_model import build_text

MODEL_PATH = "data/knn_model.pkl"
CSV_PATH   = "data/animals_labeled.csv"
CACHE_DIR = Path("data/generated_images")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_TIMEOUT_SEC = int(os.getenv("HF_TIMEOUT_SEC", "90"))


def _to_data_uri(png_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")


def _cache_path(desertion_no: str, species: str) -> Path:
    safe_species = species or "pet"
    safe_id = str(desertion_no or "unknown")
    return CACHE_DIR / f"{safe_species}_{safe_id}.png"


def _build_prompt(row: dict) -> str:
    species = row.get("species", "")
    kind = row.get("kindNm", "mixed breed")
    sex = row.get("sexCd", "")
    age = row.get("age", "")
    animal = "dog" if species == "dog" else "cat"
    return (
        f"cute {animal} portrait, semi-realistic digital illustration, "
        f"soft natural lighting, detailed fur, centered face, plain pastel background, "
        f"high quality, no text, no watermark, {kind}, {sex}, {age}"
    )


def _generate_hf_png(prompt: str) -> bytes | None:
    if not HF_API_TOKEN:
        return None
    url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=HF_TIMEOUT_SEC)
        if res.status_code != 200:
            return None
        content_type = res.headers.get("content-type", "")
        if "image" not in content_type:
            return None
        return res.content
    except Exception:
        return None


def resolve_image(row: dict) -> str:
    """Return existing image, or generated/cached data URI when possible."""
    existing = row.get("filename", "")
    if existing:
        return str(existing)

    desertion_no = str(row.get("desertionNo", ""))
    species = str(row.get("species", ""))
    cache_file = _cache_path(desertion_no, species)
    if cache_file.exists():
        return _to_data_uri(cache_file.read_bytes())

    png = _generate_hf_png(_build_prompt(row))
    if not png:
        return ""

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_bytes(png)
    return _to_data_uri(png)

# ── CSV 임시 DB 함수 (RDS 세팅 전까지 사용) ──────────────────────────────────

def get_all_animals(species=None):
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    if species:
        df = df[df["species"] == species]
    return df.to_dict("records")

def get_animal_by_id(desertion_no):
    df  = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    row = df[df["desertionNo"].astype(str) == str(desertion_no)]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

# ── MBTI 궁합 점수표 ──────────────────────────────────────────────────────────

COMPAT = {
    ("ENFP","INFJ"):95, ("ENFP","INTJ"):90, ("ENFP","ENFJ"):85,
    ("ENFP","INFP"):80, ("ENFP","ENTP"):78, ("ENFP","ISFJ"):75,
    ("ENFP","ENTJ"):72, ("ENFP","ENFP"):70, ("ENFP","INTP"):70,
    ("ENFP","ESFJ"):68, ("ENFP","ISFP"):65, ("ENFP","ESFP"):65,
    ("ENFP","ESTJ"):60, ("ENFP","ISTP"):58, ("ENFP","ESTP"):55,
    ("ENFP","ISTJ"):52,
    ("INFJ","ENFP"):95, ("INFJ","ENTP"):90, ("INFJ","INTJ"):88,
    ("INFJ","INFP"):82, ("INFJ","ENFJ"):80, ("INFJ","INFJ"):75,
    ("INFJ","INTP"):73, ("INFJ","ENTJ"):72, ("INFJ","ISFJ"):70,
    ("INFJ","ESFJ"):68, ("INFJ","ISFP"):65, ("INFJ","ESFP"):62,
    ("INFJ","ESTJ"):58, ("INFJ","ISTP"):55, ("INFJ","ESTP"):53,
    ("INFJ","ISTJ"):50,
    ("ENTP","INFJ"):90, ("ENTP","INTJ"):88, ("ENTP","ENFJ"):85,
    ("ENTP","INTP"):80, ("ENTP","ENFP"):78, ("ENTP","ENTJ"):75,
    ("ENTP","INFP"):73, ("ENTP","ENTP"):70, ("ENTP","ISFJ"):65,
    ("ENTP","ESFJ"):63, ("ENTP","ISFP"):60, ("ENTP","ESTJ"):58,
    ("ENTP","ESFP"):55, ("ENTP","ISTP"):53, ("ENTP","ESTP"):52,
    ("ENTP","ISTJ"):50,
    ("INTJ","ENFP"):90, ("INTJ","ENTP"):88, ("INTJ","INFJ"):88,
    ("INTJ","ENTJ"):82, ("INTJ","INTP"):80, ("INTJ","INFP"):75,
    ("INTJ","INTJ"):72, ("INTJ","ENFJ"):70, ("INTJ","ISFJ"):65,
    ("INTJ","ISTJ"):63, ("INTJ","ESFJ"):60, ("INTJ","ISFP"):58,
    ("INTJ","ESTJ"):57, ("INTJ","ISTP"):55, ("INTJ","ESFP"):52,
    ("INTJ","ESTP"):50,
    ("ENFJ","INFP"):95, ("ENFJ","ISFP"):90, ("ENFJ","ENFP"):85,
    ("ENFJ","INFJ"):80, ("ENFJ","ENTP"):75, ("ENFJ","ENFJ"):73,
    ("ENFJ","INTJ"):70, ("ENFJ","ESFJ"):70, ("ENFJ","INTP"):68,
    ("ENFJ","ISFJ"):65, ("ENFJ","ESFP"):63, ("ENFJ","ENTJ"):62,
    ("ENFJ","ESTP"):58, ("ENFJ","ISTP"):55, ("ENFJ","ESTJ"):53,
    ("ENFJ","ISTJ"):52,
    ("INFP","ENFJ"):95, ("INFP","ESFJ"):88, ("INFP","INFJ"):82,
    ("INFP","ENFP"):80, ("INFP","INFP"):75, ("INFP","ISFP"):73,
    ("INFP","INTJ"):72, ("INFP","ENTJ"):70, ("INFP","INTP"):68,
    ("INFP","ISFJ"):65, ("INFP","ENTP"):63, ("INFP","ESFP"):60,
    ("INFP","ESTJ"):55, ("INFP","ISTP"):53, ("INFP","ESTP"):50,
    ("INFP","ISTJ"):48,
    ("ESFJ","ISFP"):92, ("ESFJ","ISTP"):88, ("ESFJ","INFP"):85,
    ("ESFJ","ESFJ"):78, ("ESFJ","ISFJ"):75, ("ESFJ","ESFP"):73,
    ("ESFJ","ENFJ"):70, ("ESFJ","ENFP"):68, ("ESFJ","ESTJ"):65,
    ("ESFJ","ESTP"):63, ("ESFJ","INFJ"):62, ("ESFJ","ISTJ"):60,
    ("ESFJ","ENTP"):58, ("ESFJ","INTP"):55, ("ESFJ","ENTJ"):53,
    ("ESFJ","INTJ"):50,
    ("ISFJ","ESFP"):92, ("ISFJ","ESTP"):88, ("ISFJ","ENFP"):80,
    ("ISFJ","ESFJ"):75, ("ISFJ","ISFJ"):73, ("ISFJ","ISFP"):70,
    ("ISFJ","ESTJ"):68, ("ISFJ","ISTP"):65, ("ISFJ","ISTJ"):63,
    ("ISFJ","INFJ"):62, ("ISFJ","ENFJ"):60, ("ISFJ","INFP"):58,
    ("ISFJ","ENTP"):55, ("ISFJ","INTP"):53, ("ISFJ","ENTJ"):50,
    ("ISFJ","INTJ"):48,
    ("ENTJ","INTP"):90, ("ENTJ","INFP"):85, ("ENTJ","ISTP"):82,
    ("ENTJ","INTJ"):80, ("ENTJ","ENTP"):75, ("ENTJ","ENTJ"):72,
    ("ENTJ","INFJ"):70, ("ENTJ","ESTJ"):65, ("ENTJ","ENFP"):63,
    ("ENTJ","ISTJ"):62, ("ENTJ","ESFJ"):58, ("ENTJ","ENFJ"):55,
    ("ENTJ","ISFP"):53, ("ENTJ","ESFP"):50, ("ENTJ","ISFJ"):48,
    ("ENTJ","ESTP"):45,
    ("INTP","ENTJ"):90, ("INTP","ENFJ"):85, ("INTP","ESTJ"):80,
    ("INTP","INTJ"):78, ("INTP","ENTP"):75, ("INTP","INTP"):72,
    ("INTP","INFJ"):70, ("INTP","INFP"):65, ("INTP","ISTP"):63,
    ("INTP","ENFP"):62, ("INTP","ESFJ"):55, ("INTP","ISTJ"):53,
    ("INTP","ISFJ"):50, ("INTP","ESFP"):48, ("INTP","ESTP"):45,
    ("INTP","ISFP"):43,
    ("ESTJ","ISTP"):90, ("ESTJ","INTP"):85, ("ESTJ","ISFP"):82,
    ("ESTJ","ENTJ"):78, ("ESTJ","ISTJ"):75, ("ESTJ","ESFJ"):70,
    ("ESTJ","ESTJ"):68, ("ESTJ","ESTP"):65, ("ESTJ","ISFJ"):63,
    ("ESTJ","ESFP"):60, ("ESTJ","INTJ"):58, ("ESTJ","ENFJ"):55,
    ("ESTJ","ENTP"):53, ("ESTJ","INFJ"):50, ("ESTJ","ENFP"):48,
    ("ESTJ","INFP"):45,
    ("ISTJ","ESFP"):88, ("ISTJ","ESTP"):85, ("ISTJ","ISFP"):80,
    ("ISTJ","ESTJ"):75, ("ISTJ","ISFJ"):73, ("ISTJ","ISTJ"):70,
    ("ISTJ","ISTP"):68, ("ISTJ","ESFJ"):65, ("ISTJ","ENTJ"):63,
    ("ISTJ","INTP"):58, ("ISTJ","INTJ"):55, ("ISTJ","ENFJ"):53,
    ("ISTJ","INFP"):50, ("ISTJ","ENTP"):48, ("ISTJ","INFJ"):45,
    ("ISTJ","ENFP"):43,
    ("ESFP","ISFJ"):92, ("ESFP","ISTJ"):88, ("ESFP","ESFJ"):78,
    ("ESFP","ISFP"):75, ("ESFP","ESFP"):72, ("ESFP","ESTP"):70,
    ("ESFP","ENFJ"):65, ("ESFP","INFJ"):62, ("ESFP","ESTJ"):60,
    ("ESFP","ENFP"):58, ("ESFP","ENTP"):50, ("ESFP","INTP"):48,
    ("ESFP","ENTJ"):45, ("ESFP","INTJ"):43,
    ("ISFP","ESFJ"):92, ("ISFP","ENFJ"):90, ("ISFP","ESTJ"):82,
    ("ISFP","ESFP"):75, ("ISFP","ISFP"):72, ("ISFP","ISFJ"):70,
    ("ISFP","ISTP"):68, ("ISFP","ISTJ"):65, ("ISFP","INFP"):63,
    ("ISFP","ESTP"):60, ("ISFP","ENFP"):58, ("ISFP","INFJ"):55,
    ("ISFP","ENTP"):50, ("ISFP","INTJ"):48, ("ISFP","INTP"):45,
    ("ISFP","ENTJ"):43,
    ("ESTP","ISFJ"):88, ("ESTP","ISTJ"):85, ("ESTP","ISTP"):82,
    ("ESTP","ESFP"):75, ("ESTP","ESTP"):72, ("ESTP","ESFJ"):70,
    ("ESTP","ESTJ"):68, ("ESTP","ISFP"):65, ("ESTP","ENFP"):60,
    ("ESTP","INFJ"):55, ("ESTP","ENFJ"):53, ("ESTP","ENTP"):48,
    ("ESTP","INTP"):45, ("ESTP","ENTJ"):43, ("ESTP","INTJ"):40,
    ("ESTP","INFP"):38,
    ("ISTP","ESFJ"):88, ("ISTP","ESTJ"):85, ("ISTP","ENTJ"):82,
    ("ISTP","ESTP"):80, ("ISTP","ISTP"):72, ("ISTP","ISFP"):70,
    ("ISTP","ISTJ"):68, ("ISTP","ESFP"):65, ("ISTP","INTP"):63,
    ("ISTP","ISFJ"):60, ("ISTP","INTJ"):58, ("ISTP","ENFP"):55,
    ("ISTP","INFP"):53, ("ISTP","ENTP"):50, ("ISTP","INFJ"):48,
    ("ISTP","ENFJ"):45,
}

def compat_score(user_mbti: str, animal_mbti: str) -> int:
    key    = (user_mbti, animal_mbti)
    if key in COMPAT:
        return COMPAT[key]
    common = sum(a == b for a, b in zip(user_mbti, animal_mbti))
    return 40 + common * 15

def compat_comment(score: int) -> str:
    if score >= 90: return "천생연분이에요! 💕"
    if score >= 80: return "정말 잘 맞아요! 😊"
    if score >= 70: return "꽤 잘 맞는 편이에요 🙂"
    if score >= 60: return "무난하게 잘 지낼 수 있어요"
    return "서로 다르지만 배울 점이 있어요"

class PetMatcher:
    def __init__(self):
        with open(MODEL_PATH, "rb") as f:
            bundle = pickle.load(f)
        self.clf         = bundle["classifier"]
        self.le          = bundle["label_encoder"]
        self.embed_model = SentenceTransformer(bundle["embed_model"])

    def _predict_mbti(self, row: dict) -> str:
        if row.get("mbti_label") and str(row.get("mbti_label")) != "nan":
            return str(row["mbti_label"])
        text = build_text(row)
        vec  = self.embed_model.encode([text], normalize_embeddings=True)
        idx  = self.clf.predict(vec)[0]
        return self.le.inverse_transform([idx])[0]

    def get_top3(self, user_mbti: str, species: str = None) -> list:
        animals = get_all_animals(species=species)
        scored  = []
        for a in animals:
            mbti  = self._predict_mbti(a)
            score = compat_score(user_mbti, mbti)
            scored.append({
                "rank":        0,
                "desertionNo": a.get("desertionNo", ""),
                "kindNm":      a.get("kindNm", ""),
                "age":         a.get("age", ""),
                "sexCd":       a.get("sexCd", ""),
                "species":     a.get("species", ""),
                "mbti":        mbti,
                "score":       score,
                "comment":     compat_comment(score),
                "image":       a.get("filename", ""),
                "careNm":      a.get("careNm", ""),
                "careAddr":    a.get("careAddr", ""),
                "careTel":     a.get("careTel", ""),
            })
        top3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
        for i, r in enumerate(top3):
            r["rank"] = i + 1
            if not r.get("image"):
                r["image"] = resolve_image(r)
        return top3

    def get_one_compat(self, user_mbti: str, desertion_no: str) -> dict:
        animal = get_animal_by_id(desertion_no)
        if not animal:
            return {"error": "동물을 찾을 수 없습니다."}
        mbti  = self._predict_mbti(animal)
        score = compat_score(user_mbti, mbti)
        return {
            "desertionNo": desertion_no,
            "kindNm":      animal.get("kindNm", ""),
            "animal_mbti": mbti,
            "user_mbti":   user_mbti,
            "score":       score,
            "comment":     compat_comment(score),
            "image":       resolve_image(animal),
            "careNm":      animal.get("careNm", ""),
            "careAddr":    animal.get("careAddr", ""),
        }