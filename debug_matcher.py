import sys
sys.path.insert(0, 'backend/app')
from matcher import PetMatcher, compat_score, get_all_animals

m = PetMatcher()
animals = get_all_animals(species='dog')

scored = []
for a in animals:
    mbti  = m._predict_mbti(a)
    score = compat_score('ESTJ', mbti)
    scored.append((mbti, score, a.get('kindNm','')))

scored.sort(key=lambda x: x[1], reverse=True)

print("=== MBTI별 분포 ===")
from collections import Counter
print(Counter(x[0] for x in scored))

print("\n=== TOP 10 ===")
best = {}
for mbti, score, kind in scored:
    if mbti not in best:
        best[mbti] = (score, kind)

for mbti, (score, kind) in sorted(best.items(), key=lambda x: x[1][0], reverse=True)[:5]:
    print(f"{mbti}: {score}점 - {kind}")