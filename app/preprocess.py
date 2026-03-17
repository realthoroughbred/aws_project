import pandas as pd
from kiwipiepy import Kiwi
import pickle
import os

kiwi = Kiwi()

MBTI_MAP = {
    "활발": {"E": 2}, "명랑": {"E": 2}, "붙임": {"E": 1},
    "사교": {"E": 2}, "낯가림": {"I": 2}, "소심": {"I": 2},
    "겁": {"I": 1}, "조용": {"I": 1},
    "활동": {"S": 2}, "에너지": {"S": 2}, "장난": {"S": 1},
    "얌전": {"N": 2}, "순함": {"N": 2}, "차분": {"N": 2},
    "애교": {"F": 2}, "안김": {"F": 2}, "따름": {"F": 1},
    "사람": {"F": 1}, "독립": {"T": 2}, "도도": {"T": 2},
    "적응": {"P": 2}, "유연": {"P": 1},
    "예민": {"J": 2}, "민감": {"J": 1},
}

def text_to_vector(text):
    scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    tokens = kiwi.tokenize(str(text))
    words = [token.form for token in tokens]
    for word in words:
        for key, mapping in MBTI_MAP.items():
            if key in word:
                for axis, val in mapping.items():
                    scores[axis] += val
    return [scores["E"], scores["I"], scores["S"], scores["N"],
            scores["T"], scores["F"], scores["J"], scores["P"]]

def get_mbti_type(vec):
    axes = [("E","I"), ("S","N"), ("T","F"), ("J","P")]
    result = ""
    for i, (pos, neg) in enumerate(axes):
        result += pos if vec[i*2] >= vec[i*2+1] else neg
    return result

def run_preprocessing():
    print("전처리 시작...")
    df = pd.read_csv("data/animals_raw.csv", encoding="utf-8-sig")
    print(f"원본 데이터: {len(df)}건")
    print("MBTI 벡터 변환 중... (1~2분 걸려요!)")
    df["mbti_vector"] = df["specialMark"].apply(text_to_vector)
    df["mbti_type"] = df["mbti_vector"].apply(get_mbti_type)
    os.makedirs("data", exist_ok=True)
    with open("data/animals_processed.pkl", "wb") as f:
        pickle.dump(df, f)
    print(f"저장 완료 → data/animals_processed.pkl")
    print("\nMBTI 타입 분포:")
    print(df["mbti_type"].value_counts().head(10))
    print("\n샘플 확인:")
    print(df[["kindCd", "specialMark", "mbti_type"]].head())

if __name__ == "__main__":
    run_preprocessing()