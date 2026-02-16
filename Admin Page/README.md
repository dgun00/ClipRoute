# Clirpoute Admin Page

관리자 전용 데이터 관리 페이지입니다. Streamlit을 사용하여 데이터를 시각적으로 조회하고 GUI로 수정/삭제할 수 있습니다.

## 기능
- 🔐 관리자 인증 시스템
- 📊 데이터 시각화 및 필터링
- ✏️ 데이터 생성, 수정, 삭제
- 📈 통계 및 차트 (추가 예정)

## 설치 및 실행

### 1. 가상환경 생성
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일에서 관리자 계정 정보 수정
```

### 4. 실행
```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

## 프로젝트 구조
```
Clirpoute_admin_page/
├── app.py              # 메인 애플리케이션
├── pages/              # 멀티페이지
│   ├── 1_데이터_조회.py
│   ├── 2_데이터_관리.py
│   └── 3_설정.py
├── utils/              # 유틸리티
│   ├── auth.py
│   └── api.py
└── requirements.txt
```

## TODO
- [ ] 실제 API 연동
- [ ] 데이터 내보내기 기능
- [ ] 더 많은 차트 및 통계
- [ ] 사용자 활동 로그
