import pandas as pd
import numpy as np

raw     = pd.read_csv('data/animals_raw.csv', encoding='utf-8-sig')
labeled = pd.read_csv('data/animals_labeled.csv', encoding='utf-8-sig')

img_pool = raw[raw['filename'].notna() & (raw['filename'] != '')][['species','filename']].reset_index(drop=True)

def get_img(species):
    pool = img_pool[img_pool['species'] == species]['filename'].tolist()
    return np.random.choice(pool) if pool else ''

labeled['filename'] = labeled['species'].apply(get_img)
labeled.to_csv('data/animals_labeled.csv', index=False, encoding='utf-8-sig')
print('완료!', (labeled['filename'] != '').sum(), '건 이미지 매칭됨')