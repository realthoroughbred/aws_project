"""
train_model.py  —  임베딩 + SVM 분류 모델 학습
실행: python app/train_model.py
결과: data/svm_model.pkl  +  data/confusion_matrix.png (발표 자료)

필요:
    pip install sentence-transformers scikit-learn pandas matplotlib seaborn
"""

import pandas as pd, numpy as np, pickle, os, time
from sentence_transformers import SentenceTransformer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
DATA_PATH = "data/animals_labeled_full.csv"
MODEL_PATH  = "data/svm_model.pkl"

def build_text(row) -> str:
    """학습 입력 텍스트 구성 — 모든 컬럼 활용"""
    return (f"{row.get('kindNm','')} "
            f"{row.get('age_group','')} "
            f"{'수컷' if row.get('sexCd')=='M' else '암컷'} "
            f"{'중성화완료' if row.get('neuterYn')=='Y' else ''} "
            f"{row.get('specialMark','')}")

# ── 1. 데이터 로드 ─────────────────────────────────────────────────────────────

def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df = df[df["mbti_label"].notna() & (df["mbti_label"] != "UNKNOWN")]
    print(f"학습 데이터: {len(df)}건")
    print(f"MBTI 분포:\n{df['mbti_label'].value_counts()}\n")
    return df

# ── 2. 임베딩 ─────────────────────────────────────────────────────────────────

def embed(texts: list, model: SentenceTransformer) -> np.ndarray:
    print("임베딩 변환 중... (첫 실행 시 모델 다운로드 ~90MB)")
    t = time.time()
    vecs = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=64,
        normalize_embeddings=True,
    )
    print(f"완료: {vecs.shape}  ({time.time()-t:.1f}초)\n")
    return vecs

# ── 3. SVM 학습 ───────────────────────────────────────────────────────────────

def train_clf(X_train, y_train) -> SVC:
    print("SVM 학습 중 (class_weight='balanced' 적용)...")

    clf = SVC(
        kernel="rbf",
        C=10,
        gamma="scale",
        class_weight="balanced",
        probability=True,
        random_state=42,
    )

    scores = cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")
    print(f"  5-fold CV: {scores.mean()*100:.1f}% (±{scores.std()*100:.1f}%)\n")

    clf.fit(X_train, y_train)
    return clf

# ── 4. 평가 ───────────────────────────────────────────────────────────────────

def evaluate(clf, X_test, y_test, le):
    y_pred   = clf.predict(X_test)
    acc      = accuracy_score(y_test, y_pred)
    classes  = le.classes_
    print(f"{'='*50}\n테스트 정확도: {acc*100:.1f}%\n{'='*50}\n")
    print(classification_report(y_test, y_pred, labels=list(range(len(set(y_test)))), target_names=[classes[i] for i in sorted(set(y_test))]))

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
        cm  = confusion_matrix(y_test, y_pred, labels=list(range(len(classes))))
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt="d", xticklabels=classes,
                    yticklabels=classes, cmap="Blues", ax=ax)
        ax.set_xlabel("예측값"); ax.set_ylabel("실제값")
        ax.set_title(f"MBTI 분류 혼동 행렬 (정확도: {acc*100:.1f}%)")
        plt.tight_layout()
        plt.savefig("data/confusion_matrix.png", dpi=150)
        print("혼동 행렬 저장: data/confusion_matrix.png  (발표 자료로 활용)")
    except ImportError:
        print("(matplotlib 없으면 pip install matplotlib seaborn)")
    return acc

# ── 5. 저장 ───────────────────────────────────────────────────────────────────

def save_model(clf, le):
    os.makedirs("data", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"classifier": clf, "embed_model": EMBED_MODEL, "label_encoder": le}, f)
    print(f"\n모델 저장: {MODEL_PATH}")

# ── 추론 함수 (matcher.py에서 import) ─────────────────────────────────────────

def predict_mbti(text: str) -> str:
    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
    model = SentenceTransformer(bundle["embed_model"])
    vec   = model.encode([text], normalize_embeddings=True)
    idx   = bundle["classifier"].predict(vec)[0]
    return bundle["label_encoder"].inverse_transform([idx])[0]

# ── 메인 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("PawType MBTI 분류 모델 학습")
    print("=" * 50 + "\n")

    df     = load_data()
    texts  = df.apply(build_text, axis=1).tolist()

    le = LabelEncoder()
    y  = le.fit_transform(df["mbti_label"].tolist())

    model = SentenceTransformer(EMBED_MODEL)
    X     = embed(texts, model)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"학습: {len(X_train)}건  /  테스트: {len(X_test)}건\n")

    clf = train_clf(X_train, y_train)
    evaluate(clf, X_test, y_test, le)
    save_model(clf, le)

    print("\n완료. 다음: python backend/app/app.py")