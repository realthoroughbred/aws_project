import pandas as pd

raw     = pd.read_csv('data/animals_raw.csv', encoding='utf-8-sig')
labeled = pd.read_csv('data/animals_labeled.csv', encoding='utf-8-sig')

merged = raw.merge(labeled[['kindNm','age','mbti_label']], on=['kindNm','age'], how='left')
merged.to_csv('data/animals_labeled.csv', index=False, encoding='utf-8-sig')

print('완료!')
print('이미지 URL 있는 건수:', merged['filename'].notna().sum())
print('MBTI 있는 건수:', merged['mbti_label'].notna().sum())
print('전체 건수:', len(merged))