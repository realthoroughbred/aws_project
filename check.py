import pandas as pd

raw     = pd.read_csv("data/animals_raw.csv", encoding="utf-8-sig")
labeled = pd.read_csv("data/animals_labeled.csv", encoding="utf-8-sig")

print("=== animals_raw desertionNo 샘플 ===")
print(raw["desertionNo"].head(5).tolist())

print("\n=== animals_labeled desertionNo 샘플 ===")
print(labeled["desertionNo"].head(5).tolist())

raw_ids     = set(raw["desertionNo"].astype(str))
labeled_ids = set(labeled["desertionNo"].astype(str))
overlap     = raw_ids.intersection(labeled_ids)
print(f"\n=== 겹치는 건: {len(overlap)}건 ===")
