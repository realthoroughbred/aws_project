from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from matcher import PetMatcher

app = Flask(__name__, template_folder="../frontend")
CORS(app)

matcher = PetMatcher()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/match/top3", methods=["POST"])
def top3():
    body = request.get_json()
    user_mbti = body.get("user_mbti", "").upper()
    results = matcher.get_top3(user_mbti)
    return jsonify({"user_mbti": user_mbti, "results": results})

@app.route("/match/one", methods=["POST"])
def one_match():
    body = request.get_json()
    user_mbti  = body.get("user_mbti", "").upper()
    animal_id  = body.get("animal_id", "")
    result = matcher.get_one_compat(user_mbti, animal_id)
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "animals": len(matcher.df)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)