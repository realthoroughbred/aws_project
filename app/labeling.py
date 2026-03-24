"""
labeling.py  —  Claude API로 동물 MBTI 라벨링
실행: python app/labeling.py
결과: data/animals_labeled.csv

필요:
    pip install anthropic pandas
    export ANTHROPIC_API_KEY="sk-ant-..."
"""

import anthropic, pandas as pd, re, time, os
from collections import Counter

client = anthropic.Anthropic()

VALID_MBTI = {
    "ENFP","ENFJ","ENTP","ENTJ","ESFP","ESFJ","ESTP","ESTJ",
    "INFP","INFJ","INTP","INTJ","ISFP","ISFJ","ISTP","ISTJ"
}

SYSTEM_PROMPT = """당신은 동물 행동 전문가입니다.
유기동물의 정보를 보고 성격을 MBTI로 분류하세요.

판단 기준:
E vs I: 사람·동물과 잘 어울리면 E, 겁 많거나 경계심 강하면 I
S vs N: 안정적·루틴을 좋아하면 S, 호기심 많고 활발하면 N
T vs F: 독립적·경계심 있으면 T, 애정표현 풍부하고 잘 따르면 F
J vs P: 예측 가능하고 규칙적이면 J, 즉흥적이고 자유로우면 P

나이 참고:
- 새끼: 호기심 많고 활발 → N 성향
- 성체: 안정적 → S 성향
- 노령: 조용하고 루틴 선호 → S, J 성향

품종 정보와 특이사항을 종합해서 판단하세요.
정보가 부족한 축은 나이·품종 평균 성격으로 추정하세요.
반드시 MBTI 4글자만 출력하세요. 예: ISFJ"""

def build_input(row) -> str:
    return (f"품종: {row.get('kindNm', '알 수 없음')}\n"
            f"나이: {row.get('age', '알 수 없음')} ({row.get('age_group', '성체')})\n"
            f"성별: {row.get('sexCd', '알 수 없음')} / "
            f"중성화: {row.get('neuterYn', '알 수 없음')}\n"
            f"특이사항: {row.get('specialMark', '없음')}")

def label_one(text: str) -> str:
    try:
        msg = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=10,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}]
        )
        raw = msg.content[0].text.strip().upper()
        m   = re.search(r'\b([EI][NS][TF][JP])\b', raw)
        if m and m.group(1) in VALID_MBTI:
            return m.group(1)
        return "ISFJ"   # 판단 불가 시 기본값
    except Exception as e:
        print(f"  API 오류: {e}")
        return None

def label_with_vote(text: str, n: int = 3) -> str:
    """같은 텍스트 n번 호출 → 다수결로 채택"""
    results = [r for _ in range(n) if (r := label_one(text))]
    if not results:
        return "ISFJ"
    vote, _ = Counter(results).most_common(1)[0]
    return vote

def run_labeling(
    input_csv:  str   = "data/animals_raw.csv",
    output_csv: str   = "data/animals_labeled.csv",
    sample_n:   int   = None,
    n_votes:    int   = 3,
    delay:      float = 0.3,
):
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    print(f"원본: {len(df)}건")

    # 이어서 진행 (중단돼도 안 날아감)
    if os.path.exists(output_csv):
        done    = pd.read_csv(output_csv, encoding="utf-8-sig")
        done_ids = set(done["desertionNo"].astype(str))
        df      = df[~df["desertionNo"].astype(str).isin(done_ids)].reset_index(drop=True)
        print(f"이어서: {len(done)}건 완료, {len(df)}건 남음")
    else:
        done = pd.DataFrame()

    if sample_n:
        df = df.head(sample_n)
        print(f"샘플 모드: {sample_n}건")

    labels = []
    for i, row in df.iterrows():
        text  = build_input(row)
        mbti  = label_with_vote(text, n=n_votes)
        labels.append(mbti)
        print(f"[{i+1}/{len(df)}] {mbti}  ←  {str(row.get('specialMark',''))[:40]}...")

        # 50건마다 중간 저장
        if (i + 1) % 50 == 0:
            tmp = df.iloc[:i+1].copy()
            tmp["mbti_label"] = labels
            pd.concat([done, tmp], ignore_index=True).to_csv(output_csv, index=False, encoding="utf-8-sig")
            print(f"  → 중간 저장 ({i+1}건)")

        time.sleep(delay)

    df["mbti_label"] = labels
    final = pd.concat([done, df], ignore_index=True)
    final.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"\n완료: {len(df)}건")
    print(f"MBTI 분포:\n{df['mbti_label'].value_counts()}")
    return final

if __name__ == "__main__":
    # 테스트: sample_n=30, n_votes=1
    # 전체:   sample_n=None, n_votes=3
    run_labeling(sample_n=30, n_votes=1)