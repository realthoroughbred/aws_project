"""
app.py  —  Flask REST API 서버
실행: python app/app.py
배포: AWS EC2
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

matcher = None

def get_matcher():
    global matcher
    if matcher is not None:
        return matcher
    try:
        from matcher import PetMatcher
        matcher = PetMatcher()
        print("모델 로딩 성공")
        return matcher
    except FileNotFoundError:
        print("경고: svm_model.pkl 없음 → 학습 먼저 실행하세요")
        return None
    except Exception as e:
        print(f"경고: 모델 로딩 실패 → {e}")
        return None

get_matcher()

VALID_MBTI = {
    "ENFP","ENFJ","ENTP","ENTJ","ESFP","ESFJ","ESTP","ESTJ",
    "INFP","INFJ","INTP","INTJ","ISFP","ISFJ","ISTP","ISTJ"
}

def validate_mbti(mbti: str):
    if not mbti or len(mbti) != 4:
        return False, "MBTI 4글자를 입력해주세요."
    if mbti.upper() not in VALID_MBTI:
        return False, f"유효하지 않은 MBTI입니다: {mbti}"
    return True, None

# ── 엔드포인트 ────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    model_ready = matcher is not None
    return jsonify({
        "status":      "ok",
        "model_ready": model_ready,
        "message":     "모델 준비 완료" if model_ready else "모델 미로딩 (학습 필요)"
    })

@app.route("/match/top3", methods=["POST"])
def top3():
    body = request.get_json()
    if not body:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    user_mbti = body.get("user_mbti", "").upper()
    species   = body.get("species", None)

    ok, err = validate_mbti(user_mbti)
    if not ok:
        return jsonify({"error": err}), 400

    if species not in ("dog", "cat", None):
        return jsonify({"error": "species는 'dog' 또는 'cat'이어야 합니다."}), 400

    m = get_matcher()
    if m is None:
        return jsonify({"error": "모델이 준비되지 않았어요."}), 503

    try:
        results = m.get_top3(user_mbti, species=species)
        return jsonify({"user_mbti": user_mbti, "species": species, "results": results})
    except Exception as e:
        return jsonify({"error": f"궁합 계산 중 오류: {str(e)}"}), 500

@app.route("/match/one", methods=["POST"])
def one_match():
    body = request.get_json()
    if not body:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    user_mbti    = body.get("user_mbti", "").upper()
    desertion_no = body.get("desertionNo", "")

    ok, err = validate_mbti(user_mbti)
    if not ok:
        return jsonify({"error": err}), 400

    if not desertion_no:
        return jsonify({"error": "desertionNo가 필요합니다."}), 400

    m = get_matcher()
    if m is None:
        return jsonify({"error": "모델이 준비되지 않았어요."}), 503

    try:
        result = m.get_one_compat(user_mbti, desertion_no)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"궁합 계산 중 오류: {str(e)}"}), 500

@app.route("/animal/register", methods=["POST"])
def register_animal():
    body = request.get_json()
    if not body:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    if not body.get("kindNm"):
        return jsonify({"error": "품종을 입력해주세요."}), 400

    m = get_matcher()
    if m is None:
        return jsonify({"error": "모델이 준비되지 않았어요."}), 503

    try:
        import uuid
        from db import get_conn

        mbti = body.get("mbti_label") or m._predict_mbti(body)
        desertion_no = str(uuid.uuid4())[:12].replace("-", "")

        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO animals
                    (desertionNo, kindNm, age, age_group, sexCd, neuterYn,
                     specialMark, species, careNm, careAddr, careTel,
                     filename, processState)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                desertion_no,
                body.get("kindNm", ""),
                body.get("age", ""),
                "성체",
                body.get("sexCd", "M"),
                body.get("neuterYn", "N"),
                body.get("specialMark", ""),
                body.get("species", "dog"),
                body.get("careNm", ""),
                body.get("careAddr", ""),
                body.get("careTel", ""),
                "",
                "보호중",
            ))
            cur.execute("""
                INSERT INTO animals_mbti (desertionNo, mbti_label)
                VALUES (%s, %s)
            """, (desertion_no, mbti))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "mbti": mbti, "desertionNo": desertion_no})
    except Exception as e:
        return jsonify({"error": f"등록 중 오류: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)