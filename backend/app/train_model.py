"""
train_model.py  —  임베딩 + SVM 분류 모델 학습
실행: python backend/app/train_model.py
결과: data/svm_model.pkl  +  data/confusion_matrix.png (발표 자료)

필요:
    pip install sentence-transformers scikit-learn pandas matplotlib seaborn
"""

import pandas as pd, numpy as np, pickle, os, time
from sentence_transformers import SentenceTransformer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
DATA_PATH   = "data/animals__labeled.csv" # 기존 코드의 animals__labeled.csv 파일명 확인 필요
MODEL_PATH  = "data/svm_model.pkl"

def build_text(row) -> str:
    """학습 입력 텍스트 구성 (결측치 nan이 문자열로 들어가는 것 방지)"""
    kind = str(row['kindNm']) if pd.notna(row.get('kindNm')) else ""
    age = str(row['age_group']) if pd.notna(row.get('age_group')) else ""
    sex = '수컷' if row.get('sexCd') == 'M' else ('암컷' if row.get('sexCd') == 'F' else '성별미상')
    neuter = '중성화완료' if row.get('neuterYn') == 'Y' else ('중성화안됨' if row.get('neuterYn') == 'N' else '중성화미상')
    mark = str(row['specialMark']) if pd.notna(row.get('specialMark')) else ""
    
    # 텍스트들을 하나의 문장으로 결합 후 양옆 공백 제거
    return f"{kind} {age} {sex} {neuter} {mark}".strip()

# ── 1. 데이터 로드 및 전처리 (멘토링 피드백 반영) ──────────────────────────────────

def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    print(f"[전처리 전] 최초 데이터: {len(df)}건")

    # 1. 결측치 및 잘못된 라벨 제거
    df = df[df["mbti_label"].notna() & (df["mbti_label"] != "UNKNOWN")]
    
    # 2. 텍스트 컬럼 미리 생성 (중복 및 이상치 검사를 위해)
    df['combined_text'] = df.apply(build_text, axis=1)

    # 3. 중복된 값 제거 (과적합 방지의 핵심)
    # 만들어진 텍스트(특징)가 완전히 똑같은 데이터는 중복으로 보고 하나만 남김
    initial_len = len(df)
    df = df.drop_duplicates(subset=['combined_text'])
    print(f"[전처리] 중복 데이터 제거: {initial_len - len(df)}건 삭제")

    # 4. 이상치 제거 (말이 안 되는 값 거르기)
    # 특징 텍스트가 너무 짧은 경우 (예: 정보가 거의 없어서 10자 이하인 경우) 학습에서 제외
    initial_len = len(df)
    df = df[df['combined_text'].str.replace(" ", "").str.len() > 5] # 공백 제외 5글자 초과만 남김
    print(f"[전처리] 정보 부족(이상치) 텍스트 제거: {initial_len - len(df)}건 삭제")

    # (선택) 만약 age나 weight 같은 숫자형 데이터 컬럼이 있다면 여기서 범위 필터링 추가 가능
    # 예: df = df[(df['age'] >= 0) & (df['age'] <= 30)]

    print(f"\n[전처리 후] 최종 학습 데이터: {len(df)}건")
    print(f"최종 MBTI 분포:\n{df['mbti_label'].value_counts()}\n")
    
    # K-Fold를 위해 최소 데이터 수 확인 (5-fold이므로 한 클래스당 최소 5개 이상이어야 함)
    min_class_count = df['mbti_label'].value_counts().min()
    if min_class_count < 5:
        print(f"⚠️ 경고: 일부 MBTI 라벨의 데이터 수가 5개 미만입니다 (최소: {min_class_count}개).")
        print("교차 검증(Cross Validation)시 에러가 발생할 수 있으니 데이터 생성을 더 해주세요.")

    return df

# ── 2. 임베딩 ─────────────────────────────────────────────────────────────────

def embed(texts: list, model: SentenceTransformer) -> np.ndarray:
    print("임베딩 변환 중...")
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

def train_svm(X_train, y_train) -> SVC:
    print("SVM 학습 중...")
    print("5-fold Cross Validation 수행 중...")

    clf = SVC(
        kernel="rbf",
        C=10,
        gamma="scale",
        class_weight="balanced",
        probability=True,
        random_state=42,
    )

    # Stratified K-Fold: 각 클래스 비율 유지하면서 5등분
    skf    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_train, y_train, cv=skf, scoring="accuracy")

    print(f"\n  Fold별 정확도:")
    for i, s in enumerate(scores):
        print(f"    Fold {i+1}: {s*100:.1f}%")
    print(f"\n  평균: {scores.mean()*100:.1f}% (±{scores.std()*100:.1f}%)\n")

    clf.fit(X_train, y_train)
    return clf

# ── 4. 평가 ───────────────────────────────────────────────────────────────────

def evaluate(clf, X_test, y_test, le):
    y_pred  = clf.predict(X_test)
    acc     = accuracy_score(y_test, y_pred)
    classes = le.classes_

    print(f"{'='*50}")
    print(f"테스트 정확도: {acc*100:.1f}%  (테스트 데이터 {len(y_test)}건)")
    print(f"{'='*50}\n")
    print(classification_report(
        y_test, y_pred,
        labels=list(range(len(classes))),
        target_names=classes,
        zero_division=0
    ))

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        import seaborn as sns

        # 한글 폰트 깨짐 방지 (맑은 고딕 등 환경에 맞게 설정)
        plt.rc('font', family='Malgun Gothic') 
        plt.rcParams['axes.unicode_minus'] = False

        cm  = confusion_matrix(y_test, y_pred, labels=list(range(len(classes))))
        fig, ax = plt.subplots(figsize=(14, 12))
        sns.heatmap(cm, annot=True, fmt="d", xticklabels=classes,
                    yticklabels=classes, cmap="Blues", ax=ax)
        ax.set_xlabel("예측값")
        ax.set_ylabel("실제값")
        ax.set_title(f"MBTI 분류 혼동 행렬 (테스트 정확도: {acc*100:.1f}%)")
        plt.tight_layout()
        plt.savefig("data/confusion_matrix.png", dpi=150)
        print("혼동 행렬 이미지 저장: data/confusion_matrix.png")
    except Exception as e:
        print(f"(혼동 행렬 저장 실패: {e})")

    return acc

# ── 5. 저장 ───────────────────────────────────────────────────────────────────

def save_model(clf, le):
    os.makedirs("data", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "classifier":   clf,
            "embed_model":  EMBED_MODEL,
            "label_encoder": le
        }, f)
    print(f"\n모델 저장 완료: {MODEL_PATH}")

# ── 추론 함수 (matcher.py에서 import) ────────────────────────────────────────

def predict_mbti(text: str) -> str:
    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
    model = SentenceTransformer(bundle["embed_model"])
    vec   = model.encode([text], normalize_embeddings=True)
    idx   = bundle["classifier"].predict(vec)[0]
    return bundle["label_encoder"].inverse_transform([idx])[0]

# ── 메인 ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("궁합냥멍 MBTI 분류 모델 학습 (SVM)")
    print("=" * 50 + "\n")

    df    = load_data()
    # 전처리 단계에서 이미 combined_text를 만들어 두었으므로 바로 사용
    texts = df['combined_text'].tolist()

    le = LabelEncoder()
    y  = le.fit_transform(df["mbti_label"].tolist())

    model = SentenceTransformer(EMBED_MODEL)
    X     = embed(texts, model)

    # 70% 학습 / 30% 테스트 (stratify=y: 클래스 비율 유지)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.3,
        random_state=42,
        stratify=y      # 각 MBTI 비율 유지
    )
    print(f"학습에 사용될 훈련 데이터: {len(X_train)}건 (70%)")
    print(f"평가에 사용될 테스트 데이터: {len(X_test)}건 (30%)\n")

    clf = train_svm(X_train, y_train)
    evaluate(clf, X_test, y_test, le)
    save_model(clf, le)

    print("\n완료! 모델 학습이 성공적으로 끝났습니다.")