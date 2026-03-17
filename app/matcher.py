import pickle
import numpy as np

COMPAT_MATRIX = {
    "INTJ": {"INTJ":85,"INTP":80,"ENTJ":80,"ENTP":65,"INFJ":95,"INFP":65,"ENFJ":65,"ENFP":50,"ISTJ":80,"ISFJ":65,"ESTJ":80,"ESFJ":50,"ISTP":65,"ISFP":50,"ESTP":50,"ESFP":35},
    "INTP": {"INTJ":80,"INTP":85,"ENTJ":65,"ENTP":80,"INFJ":65,"INFP":95,"ENFJ":50,"ENFP":65,"ISTJ":65,"ISFJ":50,"ESTJ":65,"ESFJ":35,"ISTP":80,"ISFP":65,"ESTP":65,"ESFP":50},
    "ENTJ": {"INTJ":80,"INTP":65,"ENTJ":85,"ENTP":80,"INFJ":65,"INFP":50,"ENFJ":95,"ENFP":65,"ISTJ":80,"ISFJ":65,"ESTJ":95,"ESFJ":65,"ISTP":65,"ISFP":50,"ESTP":80,"ESFP":65},
    "ENTP": {"INTJ":65,"INTP":80,"ENTJ":80,"ENTP":85,"INFJ":50,"INFP":65,"ENFJ":65,"ENFP":95,"ISTJ":65,"ISFJ":50,"ESTJ":65,"ESFJ":50,"ISTP":65,"ISFP":50,"ESTP":95,"ESFP":65},
    "INFJ": {"INTJ":95,"INTP":65,"ENTJ":65,"ENTP":50,"INFJ":85,"INFP":80,"ENFJ":80,"ENFP":95,"ISTJ":65,"ISFJ":80,"ESTJ":50,"ESFJ":65,"ISTP":50,"ISFP":65,"ESTP":35,"ESFP":50},
    "INFP": {"INTJ":65,"INTP":95,"ENTJ":50,"ENTP":65,"INFJ":80,"INFP":85,"ENFJ":95,"ENFP":80,"ISTJ":50,"ISFJ":65,"ESTJ":35,"ESFJ":65,"ISTP":65,"ISFP":80,"ESTP":50,"ESFP":65},
    "ENFJ": {"INTJ":65,"INTP":50,"ENTJ":95,"ENTP":65,"INFJ":80,"INFP":95,"ENFJ":85,"ENFP":80,"ISTJ":65,"ISFJ":80,"ESTJ":80,"ESFJ":95,"ISTP":50,"ISFP":65,"ESTP":65,"ESFP":80},
    "ENFP": {"INTJ":50,"INTP":65,"ENTJ":65,"ENTP":95,"INFJ":95,"INFP":80,"ENFJ":80,"ENFP":85,"ISTJ":50,"ISFJ":65,"ESTJ":65,"ESFJ":80,"ISTP":65,"ISFP":95,"ESTP":80,"ESFP":95},
    "ISTJ": {"INTJ":80,"INTP":65,"ENTJ":80,"ENTP":65,"INFJ":65,"INFP":50,"ENFJ":65,"ENFP":50,"ISTJ":85,"ISFJ":80,"ESTJ":95,"ESFJ":80,"ISTP":80,"ISFP":65,"ESTP":65,"ESFP":50},
    "ISFJ": {"INTJ":65,"INTP":50,"ENTJ":65,"ENTP":50,"INFJ":80,"INFP":65,"ENFJ":80,"ENFP":65,"ISTJ":80,"ISFJ":85,"ESTJ":80,"ESFJ":95,"ISTP":65,"ISFP":80,"ESTP":65,"ESFP":80},
    "ESTJ": {"INTJ":80,"INTP":65,"ENTJ":95,"ENTP":65,"INFJ":50,"INFP":35,"ENFJ":80,"ENFP":65,"ISTJ":95,"ISFJ":80,"ESTJ":85,"ESFJ":80,"ISTP":65,"ISFP":50,"ESTP":80,"ESFP":65},
    "ESFJ": {"INTJ":50,"INTP":35,"ENTJ":65,"ENTP":50,"INFJ":65,"INFP":65,"ENFJ":95,"ENFP":80,"ISTJ":80,"ISFJ":95,"ESTJ":80,"ESFJ":85,"ISTP":50,"ISFP":65,"ESTP":65,"ESFP":80},
    "ISTP": {"INTJ":65,"INTP":80,"ENTJ":65,"ENTP":65,"INFJ":50,"INFP":65,"ENFJ":50,"ENFP":65,"ISTJ":80,"ISFJ":65,"ESTJ":65,"ESFJ":50,"ISTP":85,"ISFP":80,"ESTP":95,"ESFP":80},
    "ISFP": {"INTJ":50,"INTP":65,"ENTJ":50,"ENTP":50,"INFJ":65,"INFP":80,"ENFJ":65,"ENFP":95,"ISTJ":65,"ISFJ":80,"ESTJ":50,"ESFJ":65,"ISTP":80,"ISFP":85,"ESTP":80,"ESFP":95},
    "ESTP": {"INTJ":50,"INTP":65,"ENTJ":80,"ENTP":95,"INFJ":35,"INFP":50,"ENFJ":65,"ENFP":80,"ISTJ":65,"ISFJ":65,"ESTJ":80,"ESFJ":65,"ISTP":95,"ISFP":80,"ESTP":85,"ESFP":80},
    "ESFP": {"INTJ":35,"INTP":50,"ENTJ":65,"ENTP":65,"INFJ":50,"INFP":65,"ENFJ":80,"ENFP":95,"ISTJ":50,"ISFJ":80,"ESTJ":65,"ESFJ":80,"ISTP":80,"ISFP":95,"ESTP":80,"ESFP":85},
}

COMPAT_DESC = {
    (95, 100): ("천생연분 ★★★★★", "서로의 에너지가 완벽하게 맞아요!"),
    (80,  94): ("잘 맞아요 ★★★★",  "함께하면 편안하고 즐거울 거예요."),
    (65,  79): ("무난해요 ★★★",    "조금씩 맞춰가면 좋은 파트너가 될 수 있어요."),
    (50,  64): ("노력이 필요해요 ★★","서로 다른 부분이 있지만 배울 점도 많아요."),
    (0,   49): ("도전적인 궁합 ★",  "차이가 크지만 불가능하지 않아요!"),
}

def get_compat_desc(score):
    for (lo, hi), (label, msg) in COMPAT_DESC.items():
        if lo <= score <= hi:
            return label, msg
    return "알 수 없음", ""

class PetMatcher:
    def __init__(self, data_path="data/animals_processed.pkl"):
        with open(data_path, "rb") as f:
            self.df = pickle.load(f)
        print(f"매처 로드 완료: {len(self.df)}마리")

    def get_top3(self, user_mbti: str):
        """나와 궁합 TOP 3 동물 추천"""
        user_mbti = user_mbti.upper()
        if user_mbti not in COMPAT_MATRIX:
            return {"error": f"{user_mbti} 타입 정보 없음"}
        results = []
        for _, row in self.df.iterrows():
            animal_mbti = str(row.get("mbti_type", ""))
            if animal_mbti not in COMPAT_MATRIX.get(user_mbti, {}):
                continue
            score = COMPAT_MATRIX[user_mbti][animal_mbti]
            label, msg = get_compat_desc(score)
            results.append({
                "id":           str(row.get("desertionNo", "")),
                "name":         str(row.get("kindCd", "")),
                "age":          str(row.get("age", "")),
                "sex":          str(row.get("sexCd", "")),
                "animal_mbti":  animal_mbti,
                "user_mbti":    user_mbti,
                "compat_score": score,
                "compat_label": label,
                "compat_msg":   msg,
                "specialMark":  str(row.get("specialMark", ""))[:60],
                "image_url":    str(row.get("photoUrl", "")),
                "shelter":      str(row.get("careNm", "")),
                "shelter_addr": str(row.get("careAddr", "")),
            })
        results.sort(key=lambda x: x["compat_score"], reverse=True)
        return results[:3]

    def get_one_compat(self, user_mbti: str, animal_id: str):
        """선택한 동물과 1:1 궁합 확인"""
        user_mbti = user_mbti.upper()
        row = self.df[self.df["desertionNo"].astype(str) == animal_id]
        if row.empty:
            return {"error": "해당 동물을 찾을 수 없어요"}
        row = row.iloc[0]
        animal_mbti = str(row.get("mbti_type", ""))
        score = COMPAT_MATRIX.get(user_mbti, {}).get(animal_mbti, 50)
        label, msg = get_compat_desc(score)
        return {
            "id":           animal_id,
            "name":         str(row.get("kindCd", "")),
            "animal_mbti":  animal_mbti,
            "user_mbti":    user_mbti,
            "compat_score": score,
            "compat_label": label,
            "compat_msg":   msg,
            "specialMark":  str(row.get("specialMark", ""))[:60],
            "image_url":    str(row.get("photoUrl", "")),
            "shelter":      str(row.get("careNm", "")),
        }

if __name__ == "__main__":
    matcher = PetMatcher()
    results = matcher.get_top3("INFP")
    for i, r in enumerate(results, 1):
        print(f"{i}위: {r['name']} | {r['animal_mbti']} | {r['compat_score']}점 | {r['compat_label']}")