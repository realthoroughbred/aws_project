"""
matcher.py  —  MBTI 궁합 계산 + 동물 TOP 3 추천
app.py에서 import해서 사용
"""

import pickle, pandas as pd
from sentence_transformers import SentenceTransformer
from app.db import get_all_animals, get_animal_by_id
from app.train_model import build_text

MODEL_PATH = "data/knn_model.pkl"

# MBTI 궁합 점수표 (16x16 주요 조합)
COMPAT = {
    ("INFJ","ENFP"):95, ("INFJ","ENTP"):90, ("INFJ","INTJ"):85,
    ("ENFP","INFJ"):95, ("ENFP","INTJ"):88, ("ENFP","ENFJ"):82,
    ("INTJ","ENFP"):88, ("INTJ","INFJ"):85, ("INTJ","ENTP"):83,
    ("ISFJ","ESFP"):90, ("ISFJ","ESTP"):85, ("ISFJ","ENFP"):80,
    ("ESFJ","ISFP"):90, ("ESFJ","ISTP"):85, ("ESFJ","INFP"):80,
    ("ISTP","ESFJ"):85, ("ISTP","ESTJ"):82, ("ISTP","ENTJ"):80,
    ("INTP","ENTJ"):88, ("INTP","ENFJ"):85, ("INTP","ESTJ"):80,
}

def compat_score(user_mbti: str, animal_mbti: str) -> int:
    """궁합 점수 — 점수표에 없으면 공통 축 개수로 계산"""
    key = (user_mbti, animal_mbti)
    if key in COMPAT:
        return COMPAT[key]
    common = sum(a == b for a, b in zip(user_mbti, animal_mbti))
    return 40 + common * 15   # 40~100점

def compat_comment(score: int) -> str:
    if score >= 90: return "천생연분이에요!"
    if score >= 80: return "잘 맞아요"
    if score >= 70: return "괜찮은 궁합이에요"
    return "조금 다를 수 있어요"

class PetMatcher:
    def __init__(self):
        # KNN 모델 로딩
        with open(MODEL_PATH, "rb") as f:
            bundle = pickle.load(f)
        self.clf  = bundle["classifier"]
        self.le   = bundle["label_encoder"]
        self.embed_model = SentenceTransformer(bundle["embed_model"])

    def _predict_mbti(self, row: dict) -> str:
        """동물 row → MBTI 예측"""
        if row.get("mbti_label"):          # DB에 라벨 있으면 그거 사용
            return row["mbti_label"]
        text = build_text(row)
        vec  = self.embed_model.encode([text], normalize_embeddings=True)
        idx  = self.clf.predict(vec)[0]
        return self.le.inverse_transform([idx])[0]

    def get_top3(self, user_mbti: str, species: str = None) -> list:
        """사용자 MBTI + 종 → TOP 3 추천"""
        animals = get_all_animals(species=species)
        scored  = []
        for a in animals:
            mbti  = self._predict_mbti(a)
            score = compat_score(user_mbti, mbti)
            scored.append({
                "rank":        0,
                "desertionNo": a["desertionNo"],
                "kindNm":      a.get("kindNm",""),
                "age":         a.get("age",""),
                "sexCd":       a.get("sexCd",""),
                "species":     a.get("species",""),
                "mbti":        mbti,
                "score":       score,
                "comment":     compat_comment(score),
                "image":       a.get("filename",""),
                "careNm":      a.get("careNm",""),
                "careAddr":    a.get("careAddr",""),
                "careTel":     a.get("careTel",""),
            })
        top3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
        for i, r in enumerate(top3):
            r["rank"] = i + 1
        return top3

    def get_one_compat(self, user_mbti: str, desertion_no: str) -> dict:
        """특정 동물과의 1:1 궁합"""
        animal = get_animal_by_id(desertion_no)
        if not animal:
            return {"error": "동물을 찾을 수 없습니다."}
        mbti  = self._predict_mbti(animal)
        score = compat_score(user_mbti, mbti)
        return {
            "desertionNo": desertion_no,
            "kindNm":      animal.get("kindNm",""),
            "animal_mbti": mbti,
            "user_mbti":   user_mbti,
            "score":       score,
            "comment":     compat_comment(score),
            "image":       animal.get("filename",""),
            "careNm":      animal.get("careNm",""),
            "careAddr":    animal.get("careAddr",""),
        }