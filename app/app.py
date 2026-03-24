"""
app.py  —  Flask REST API 서버
실행: python app/app.py
배포: AWS EC2

엔드포인트:
    POST /match/top3   — 사용자 MBTI + 종 → TOP 3
    POST /match/one    — 사용자 MBTI + 동물 ID → 궁합 점수
    GET  /health       — 서버 상태
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from app.matcher import PetMatcher

app     = Flask(__name__)
CORS(app)
matcher = PetMatcher()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/match/top3", methods=["POST"])
def top3():
    body      = request.get_json()
    user_mbti = body.get("user_mbti", "").upper()
    species   = body.get("species", None)   # "dog" or "cat"

    if len(user_mbti) != 4:
        return jsonify({"error": "유효하지 않은 MBTI입니다."}), 400

    results = matcher.get_top3(user_mbti, species=species)
    return jsonify({"user_mbti": user_mbti, "species": species, "results": results})

@app.route("/match/one", methods=["POST"])
def one_match():
    body          = request.get_json()
    user_mbti     = body.get("user_mbti", "").upper()
    desertion_no  = body.get("desertionNo", "")

    if len(user_mbti) != 4:
        return jsonify({"error": "유효하지 않은 MBTI입니다."}), 400

    result = matcher.get_one_compat(user_mbti, desertion_no)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)