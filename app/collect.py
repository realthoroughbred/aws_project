import requests
import pandas as pd
import time
import os

API_KEY = "f88bc16de6c9ce5e6a4eb47edc307403046264f6467b94dc6c9212acb13f95b1"
BASE_URL = "https://apis.data.go.kr/1543061/abandonmentPublicService_v2/abandonmentPublic_v2"

def fetch_animals(total_pages=50):
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
    df = df[df["specialMark"].notna() & (df["specialMark"] != "")]
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/animals_raw.csv", index=False, encoding="utf-8-sig")
    print(f"저장 완료: {len(df)}건 → data/animals_raw.csv")
    return df

if __name__ == "__main__":
    print("데이터 수집 시작...")
    items = fetch_animals(total_pages=10)
    df = save_csv(items)
    if df is not None:
        print("\n샘플 데이터 확인:")
        print(df[["kindCd", "sexCd", "age", "specialMark"]].head())