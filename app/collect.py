import requests
import pandas as pd
import time
import os

API_KEY = "f88bc16de6c9ce5e6a4eb47edc307403046264f6467b94dc6c9212acb13f95b1"
BASE_URL = "https://apis.data.go.kr/1543061/abandonmentPublicService_v2/abandonmentPublic_v2"

def fetch_animals(total_pages=10):
    all_items = []
    for page in range(1, total_pages + 1):
        try:
            url = f"{BASE_URL}?serviceKey={API_KEY}&pageNo={page}&numOfRows=100&_type=json"
            res = requests.get(url, timeout=10)
            data = res.json()
            items = data["response"]["body"]["items"]["item"]
            if isinstance(items, dict):
                items = [items]
            all_items.extend(items)
            print(f"{page}페이지 수집 완료 ({len(items)}건)")
            time.sleep(0.3)
        except Exception as e:
            print(f"{page}페이지 오류: {e}")
    return all_items

def save_csv(items):
    if not items:
        print("수집된 데이터가 없어요.")
        return None
    df = pd.DataFrame(items)

    # 있는 컬럼만 선택
    cols = [
        "desertionNo",   # 동물 고유번호
        "happenDt",      # 발생일
        "happenPlace",   # 발생장소
        "kindCd",        # 품종코드
        "kindNm",        # 품종명
        "colorCd",       # 색상
        "age",           # 나이
        "weight",        # 체중
        "noticeNo",      # 공고번호
        "noticeSdt",     # 공고시작일
        "noticeEdt",     # 공고종료일
        "processState",  # 처리상태
        "sexCd",         # 성별
        "neuterYn",      # 중성화여부
        "specialMark",   # 특이사항 (성격)
        "careNm",        # 보호소이름
        "careAddr",      # 보호소주소
        "careTel",       # 보호소전화
        "orgNm",         # 관할기관
        "filename",      # 이미지 URL
    ]
    df = df[[c for c in cols if c in df.columns]]
    df = df[df["specialMark"].notna() & (df["specialMark"] != "")]

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/animals_raw.csv", index=False, encoding="utf-8-sig")
    print(f"저장 완료: {len(df)}건 → data/animals_raw.csv")
    print(f"포함된 컬럼: {list(df.columns)}")
    return df

if __name__ == "__main__":
    print("데이터 수집 시작...")
    items = fetch_animals(total_pages=10)
    df = save_csv(items)
    if df is not None:
        print("\n샘플 데이터 확인:")
        print(df[["kindNm", "sexCd", "age", "specialMark"]].head())
        print("\n전체 컬럼 목록:")
        print(list(df.columns))
        # 이미지 URL 확인
        if "filename" in df.columns:
            print("\n이미지 URL 샘플:")
            print(df["filename"].head())