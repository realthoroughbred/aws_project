import pandas as pd
from kiwipiepy import Kiwi
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
import pickle
import os

kiwi = Kiwi()

MBTI_MAP = {
    # E/I 축 (사교성)
    "사람":   {"E": 3},
    "따르":   {"E": 2},
    "좋아하": {"E": 2},
    "활발":   {"E": 2},
    "애교":   {"E": 2},
    "겁":     {"I": 3},
    "경계심": {"I": 3},
    "소심":   {"I": 2},
    "경계":   {"I": 2},
    "심하":   {"I": 1},
    "입질":   {"I": 2},
    # S/N 축 (활동성)
    "활발":   {"S": 2},
    "순하":   {"N": 3},
    "온순":   {"N": 3},
    "얌전":   {"N": 2},
    "착하":   {"N": 2},
    # T/F 축 (친화성)
    "따르":   {"F": 2},
    "좋아하": {"F": 2},
    "애교":   {"F": 2},
    "경계심": {"T": 2},
    "경계":   {"T": 2},
    "입질":   {"T": 2},
    # J/P 축 (적응력)
    "양호":   {"P": 2},
    "경계심": {"J": 2},
    "심하":   {"J": 1},
    "경계":   {"J": 1},
}

DEFAULT_VECTOR = [1,1,0,2,0,1,1,0]
DEFAULT_MBTI = "INFP"

def text_to_vector(text):
    scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
    tokens = kiwi.tokenize(str(text))
    words = [token.form for token in tokens]
    matched = False
    for word in words:
        for key, mapping in MBTI_MAP.items():
            if key in word:
                for axis, val in mapping.items():
                    scores[axis] += val
                matched = True
    if not matched:
        return DEFAULT_VECTOR
    return [scores["E"], scores["I"], scores["S"], scores["N"],
            scores["T"], scores["F"], scores["J"], scores["P"]]

def get_mbti_type(vec):
    if vec == DEFAULT_VECTOR:
        return DEFAULT_MBTI
    defaults = ["I", "N", "F", "P"]
    axes = [("E","I"), ("S","N"), ("T","F"), ("J","P")]
    result = ""
    for i, ((pos, neg), default) in enumerate(zip(axes, defaults)):
        pos_score = vec[i*2]
        neg_score = vec[i*2+1]
        if pos_score > neg_score:
            result += pos
        elif neg_score > pos_score:
            result += neg
        else:
            result += default
    return result

def train_knn_model(df):
    print("\nKNN 모델 학습 시작...")
    X = np.array(df["mbti_vector"].tolist())
    Y = df["mbti_type"].tolist()

    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, random_state=42
    )

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, Y_train)

    Y_pred = knn.predict(X_test)
    accuracy = accuracy_score(Y_test, Y_pred)
    print(f"KNN 모델 정확도: {accuracy * 100:.1f}%")

    with open("data/knn_model.pkl", "wb") as f:
        pickle.dump(knn, f)
    print("KNN 모델 저장 완료 → data/knn_model.pkl")
    return knn, accuracy

def run_preprocessing():
    print("전처리 시작...")
    df = pd.read_csv("data/animals_raw.csv", encoding="utf-8-sig")
    print(f"원본 데이터: {len(df)}건")
    print("MBTI 벡터 변환 중...")

    df["mbti_vector"] = df["specialMark"].apply(text_to_vector)
    df["mbti_type"] = df["mbti_vector"].apply(get_mbti_type)

    os.makedirs("data", exist_ok=True)
    with open("data/animals_processed.pkl", "wb") as f:
        pickle.dump(df, f)
    print(f"저장 완료 → data/animals_processed.pkl")

    print("\nMBTI 타입 분포:")
    print(df["mbti_type"].value_counts().head(10))

    print("\n샘플 확인:")
    show_cols = ["kindNm", "specialMark", "mbti_type"]
    if "filename" in df.columns:
        show_cols.append("filename")
    print(df[show_cols].head(5))

    knn, accuracy = train_knn_model(df)
    return df

if __name__ == "__main__":
    run_preprocessing()