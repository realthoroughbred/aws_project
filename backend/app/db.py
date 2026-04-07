"""
db.py  —  AWS RDS MySQL 연결 및 데이터 적재/조회
실행: python app/db.py  (테이블 생성 + CSV 데이터 적재)

필요:
    pip install pymysql pandas
    환경변수 설정 (또는 아래 직접 입력):
        DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
"""

import pymysql, pandas as pd, os

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "your-rds-endpoint.rds.amazonaws.com"),
    "user":     os.getenv("DB_USER",     "admin"),
    "password": os.getenv("DB_PASSWORD", "your-password"),
    "db":       os.getenv("DB_NAME",     "pawtype"),
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

def get_conn():
    return pymysql.connect(**DB_CONFIG)

# ── 테이블 생성 ───────────────────────────────────────────────────────────────

def create_tables():
    conn = get_conn()
    with conn.cursor() as cur:
        # 원본 동물 데이터
        cur.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            desertionNo VARCHAR(30) PRIMARY KEY,
            kindNm      VARCHAR(100),
            age         VARCHAR(50),
            age_group   VARCHAR(20),
            sexCd       VARCHAR(5),
            neuterYn    VARCHAR(5),
            specialMark TEXT,
            species     VARCHAR(10),
            careNm      VARCHAR(200),
            careAddr    VARCHAR(300),
            careTel     VARCHAR(50),
            filename    VARCHAR(500),
            processState VARCHAR(50)
        ) CHARACTER SET utf8mb4
        """)

        # MBTI 라벨 테이블
        cur.execute("""
        CREATE TABLE IF NOT EXISTS animals_mbti (
            desertionNo VARCHAR(30) PRIMARY KEY,
            mbti_label  VARCHAR(10),
            FOREIGN KEY (desertionNo) REFERENCES animals(desertionNo)
        ) CHARACTER SET utf8mb4
        """)
    conn.commit()
    conn.close()
    print("테이블 생성 완료")

# ── CSV → DB 적재 ─────────────────────────────────────────────────────────────

def load_raw_csv(csv_path: str = "data/animals_raw.csv"):
    df   = pd.read_csv(csv_path, encoding="utf-8-sig").fillna("")
    conn = get_conn()
    cnt  = 0
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO animals
                    (desertionNo, kindNm, age, age_group, sexCd, neuterYn,
                     specialMark, species, careNm, careAddr, careTel,
                     filename, processState)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    specialMark=VALUES(specialMark),
                    processState=VALUES(processState)
            """, (
                str(row.get("desertionNo","")),
                str(row.get("kindNm","")),
                str(row.get("age","")),
                str(row.get("age_group","")),
                str(row.get("sexCd","")),
                str(row.get("neuterYn","")),
                str(row.get("specialMark","")),
                str(row.get("species","")),
                str(row.get("careNm","")),
                str(row.get("careAddr","")),
                str(row.get("careTel","")),
                str(row.get("filename","")),
                str(row.get("processState","")),
            ))
            cnt += 1
    conn.commit()
    conn.close()
    print(f"animals 테이블 적재: {cnt}건")

def load_labeled_csv(csv_path: str = "data/animals_labeled.csv"):
    df   = pd.read_csv(csv_path, encoding="utf-8-sig").fillna("")
    conn = get_conn()
    cnt  = 0
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            if not row.get("mbti_label"):
                continue
            cur.execute("""
                INSERT INTO animals_mbti (desertionNo, mbti_label)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE mbti_label=VALUES(mbti_label)
            """, (str(row["desertionNo"]), str(row["mbti_label"])))
            cnt += 1
    conn.commit()
    conn.close()
    print(f"animals_mbti 테이블 적재: {cnt}건")

# ── 조회 함수 (matcher.py에서 사용) ──────────────────────────────────────────

def get_all_animals(species: str = None) -> list:
    """전체 동물 조회 (species: 'dog' or 'cat' or None=전체)"""
    conn = get_conn()
    with conn.cursor() as cur:
        if species:
            cur.execute("""
                SELECT a.*, m.mbti_label
                FROM animals a
                LEFT JOIN animals_mbti m ON a.desertionNo = m.desertionNo
                WHERE a.species = %s AND a.processState = '보호중'
            """, (species,))
        else:
            cur.execute("""
                SELECT a.*, m.mbti_label
                FROM animals a
                LEFT JOIN animals_mbti m ON a.desertionNo = m.desertionNo
                WHERE a.processState = '보호중'
            """)
        rows = cur.fetchall()
    conn.close()
    return rows

def get_animal_by_id(desertion_no: str) -> dict:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.*, m.mbti_label
            FROM animals a
            LEFT JOIN animals_mbti m ON a.desertionNo = m.desertionNo
            WHERE a.desertionNo = %s
        """, (desertion_no,))
        row = cur.fetchone()
    conn.close()
    return row

if __name__ == "__main__":
    print("DB 초기화 시작...")
    create_tables()
    load_raw_csv()
    load_labeled_csv()
    print("완료!")