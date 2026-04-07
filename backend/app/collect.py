"""
collect.py  —  공공 API 유기동물 데이터 수집
실행: python app/collect.py
결과: data/animals_raw.csv
"""

import requests, pandas as pd, time, os, re

API_KEY  = "f88bc16de6c9ce5e6a4eb47edc307403046264f6467b94dc6c9212acb13f95b1"
BASE_URL = "https://apis.data.go.kr/1543061/abandonmentPublicService_v2/abandonmentPublic_v2"

COLS = [
    "desertionNo", "kindNm", "age", "sexCd", "neuterYn",
    "specialMark", "careNm", "careAddr", "careTel",
    "processState", "popfile1", "popfile2",
]

def parse_age_group(age_str: str) -> str:
    try:
        year = int(re.search(r'\d{4}', str(age_str)).group())
        age  = 2026 - year
        if age <= 1:   return "새끼"
        elif age <= 7: return "성체"
        else:          return "노령"
    except:
        return "성체"

def fetch_animals(total_pages: int = 10) -> list:
    all_items = []
    for page in range(1, total_pages + 1):
        try:
            url   = (f"{BASE_URL}?serviceKey={API_KEY}"
                     f"&pageNo={page}&numOfRows=100&_type=json")
            resp  = requests.get(url, timeout=10).json()
            items = resp["response"]["body"]["items"]["item"]
            if isinstance(items, dict):
                items = [items]
            all_items.extend(items)
            print(f"  {page}페이지 수집 완료 ({len(items)}건)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  {page}페이지 오류: {e}")
    return all_items

def save_csv(items: list) -> pd.DataFrame:
    if not items:
        print("수집된 데이터가 없습니다.")
        return None

    df = pd.DataFrame(items)

    # 이미지 URL: popfile1 우선, 없으면 popfile2
    df["filename"] = df.get("popfile1", "").fillna("")
    if "popfile2" in df.columns:
        df["filename"] = df["filename"].replace("", None).fillna(df["popfile2"])
    df["filename"] = df["filename"].fillna("").astype(str).replace("nan", "")

    keep_cols = [c for c in COLS if c in df.columns] + ["filename"]
    df = df[[c for c in keep_cols if c in df.columns]]

    df["specialMark"] = df["specialMark"].fillna("").astype(str)
    df["age_group"]   = df["age"].apply(parse_age_group)
    df["species"]     = df["kindNm"].apply(
        lambda x: "cat" if ("고양이" in str(x) or "묘" in str(x)) else "dog"
    )

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/animals_raw.csv", index=False, encoding="utf-8-sig")
    print(f"\n저장: {len(df)}건 → data/animals_raw.csv")
    print(f"강아지: {(df['species']=='dog').sum()}건  고양이: {(df['species']=='cat').sum()}건")
    print(f"이미지 URL 있는 건수: {(df['filename'] != '').sum()}건")
    print(f"\n이미지 URL 샘플:")
    print(df[df['filename'] != '']['filename'].head(3).tolist())
    return df

if __name__ == "__main__":
    print("데이터 수집 시작...")
    df = save_csv(fetch_animals(total_pages=10))
    if df is not None:
        print(df[["kindNm", "age_group", "species", "filename"]].head())