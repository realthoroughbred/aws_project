# 🐾 궁합냥멍

> 동물 MBTI 기반 반려동물 매칭 서비스

---

## 📋 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트 유형 | 팀 프로젝트 (4인) |
| 개발 기간 | 2026.03 ~ 2026.06 |
| 배포 환경 | AWS EC2 |

---

## 🏗️ 아키텍처

```
사용자 (Streamlit)
    ↓
Frontend (Streamlit, port 8501)
    ↓ HTTP 요청
Backend (Flask API, port 5000)
    ↓
모델 (sentence-transformers)
    ↓
AWS EC2 + Docker
```

---

## 📁 폴더 구조

```
aws_project/
├── frontend/         ← Streamlit UI
├── backend/          ← Flask API 서버
├── data/             ← 동물 MBTI 데이터
├── scripts/          ← 유틸리티 스크립트
├── Dockerfile.frontend
├── Dockerfile.backend
└── docker-compose.yml
```

---

## ⚙️ 주요 기능

- 사용자 설문을 통한 동물 MBTI 유형 분류
- `sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)` 기반 유사도 매칭
- 상위 3개 반려동물 추천 결과 제공
- Docker 컨테이너 기반 배포

---

## 🛠️ 기술 스택

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_EC2-232F3E?logo=amazonaws&logoColor=white)
