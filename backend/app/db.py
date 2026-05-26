"""
db.py  —  AWS RDS MySQL 연결 및 데이터 적재/조회
실행: python app/db.py  (테이블 생성 + CSV 데이터 적재)

필요:
    pip install pymysql pandas
"""

import pymysql, pandas as pd, os

DB_CONFIG = {
    "host":     "cloud1.cnks84yq8hs3.ap-northeast-2.rds.amazonaws.com",
    "user":     "ttdmin",
    "password": "catsonchoae52**",
    "db":       "pawtype",
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

def get_conn():
    return pymysql.connect(**DB_CONFIG)


# ── 테이블 생성 ───────────────────────────────────────────────────────────────

def create_tables():
    conn = get_conn()
    with conn.cursor() as cur:
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

def load_labeled_csv(csv_path: str = "data/animals_labeled.csv"):
    df = pd.read_csv(csv_path, encoding="utf-8-sig", dtype={"desertionNo": str})

    # 소수점 .0 제거
    df["desertionNo"] = df["desertionNo"].str.replace(r'\.0$', '', regex=True)

    conn = get_conn()
    cnt_animals = 0
    cnt_mbti = 0

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            # animals 테이블 적재
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
                str(row.get("desertionNo", "")),
                str(row.get("kindNm", "")),
                str(row.get("age", "")),
                str(row.get("age_group", "")),
                str(row.get("sexCd", "")),
                str(row.get("neuterYn", "")),
                str(row.get("specialMark", "")),
                str(row.get("species", "")),
                str(row.get("careNm", "")),
                str(row.get("careAddr", "")),
                str(row.get("careTel", "")),
                str(row.get("filename", "")),
                str(row.get("processState", "")),
            ))
            cnt_animals += 1

            # animals_mbti 테이블 적재
            if row.get("mbti_label"):
                cur.execute("""
                    INSERT INTO animals_mbti (desertionNo, mbti_label)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE mbti_label=VALUES(mbti_label)
                """, (str(row["desertionNo"]), str(row["mbti_label"])))
                cnt_mbti += 1

    conn.commit()
    conn.close()
    print(f"animals 적재: {cnt_animals}건")
    print(f"animals_mbti 적재: {cnt_mbti}건")


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
    load_labeled_csv()
    print("완료!")