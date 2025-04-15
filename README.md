# Lead Scout Project

## 프로젝트 개요

Lead Scout는 기업 정보를 분석하고 잠재 고객을 발굴하는 AI 기반 리드 스카우팅 시스템입니다. PDF 문서, 웹사이트, 뉴스 기사 등의 다양한 소스에서 기업 정보를 수집하고 분석하여 잠재 고객을 식별합니다.

## 주요 기능

- PDF 문서 분석 및 정보 추출
- 기업 프로필 관리
- 잠재 고객 발굴 및 분석

## 기술 스택

- Python 3.11
- Django 4.2
- Django REST Framework
- OpenAI GPT-4
- MySQL

## 설치 및 설정

### 1. 환경 설정

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정합니다:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
OPENAI_API_KEY=your-openai-api-key
```

### 3. 데이터베이스 설정

```bash
python manage.py migrate
```

### 4. 서버 실행

```bash
python manage.py runserver
```

## API 문서

### 1. 기업 프로필 관리

#### 기업 프로필 생성

```http
POST /api/profiles/
Content-Type: application/json

{
    "company": 1,
    "url": "https://example.com",
    "source_type": "website"
}
```

#### 기업 프로필 조회

```http
GET /api/profiles/{profile_id}/
```

### 2. PDF 분석

#### PDF 분석 요청

```http
POST /api/analyze-pdf/
Content-Type: application/json

{
    "pdf_url": "https://example.com/document.pdf",
    "profile_id": 1
}
```

응답:

```json
{
  "status": "success",
  "analysis": {
    "industry": "소프트웨어",
    "sales": "1000000000",
    "total_funding": "500000000",
    "homepage": "https://example.com",
    "key_executive": "홍길동",
    "address": "서울시 강남구",
    "email": "contact@example.com",
    "phone_number": "02-1234-5678",
    "company_description": "회사 설명...",
    "products_services": "제품1, 제품2, 제품3",
    "target_customers": "고객1, 고객2, 고객3",
    "competitors": "경쟁사1, 경쟁사2",
    "strengths": "강점1, 강점2, 강점3",
    "business_model": "비즈니스 모델 설명..."
  }
}
```

#### PDF 분석 결과 조회

```http
GET /api/get-pdf-analysis/?profile_id=1
```

응답:

```json
{
  "status": "success",
  "analysis": {
    "industry": "소프트웨어",
    "sales": "1000000000",
    "total_funding": "500000000",
    "homepage": "https://example.com",
    "key_executive": "홍길동",
    "address": "서울시 강남구",
    "email": "contact@example.com",
    "phone_number": "02-1234-5678",
    "company_description": "회사 설명...",
    "products_services": "제품1, 제품2, 제품3",
    "target_customers": "고객1, 고객2, 고객3",
    "competitors": "경쟁사1, 경쟁사2",
    "strengths": "강점1, 강점2, 강점3",
    "business_model": "비즈니스 모델 설명..."
  }
}
```

### 3. 잠재 고객 발굴

#### 잠재 고객 검색

```http
POST /api/find-leads/
Content-Type: application/json

{
    "company_id": 1
}
```

응답:

```json
{
  "status": "success",
  "leads": [
    {
      "company_name": "잠재 고객 기업명",
      "industry": "산업 분야",
      "description": "기업 설명",
      "match_score": 0.85,
      "match_reasons": ["매칭 이유 1", "매칭 이유 2"]
    }
  ]
}
```

## 시스템 아키텍처

### 1. 데이터 흐름

1. 기업 프로필 생성
2. PDF/웹사이트 데이터 수집
3. AI 기반 정보 분석
4. 잠재 고객 식별
5. 결과 저장 및 반환

### 2. 주요 컴포넌트

- **CompanyProfile**: 기업 프로필 관리
- **PDFAnalysis**: PDF 문서 분석 결과 저장
- **LeadScoutAgent**: 잠재 고객 발굴 로직
- **PDFAnalysisService**: PDF 분석 서비스

## 작동 로직

### 1. PDF 분석 프로세스

1. PDF URL에서 문서 다운로드
2. 텍스트 추출
3. OpenAI를 통한 정보 분석
4. 분석 결과 DB 저장
5. 결과 반환

### 2. 잠재 고객 발굴 프로세스

1. 기업 프로필 조회
2. 관련 PDF 문서 분석
3. AI 기반 잠재 고객 식별
4. 결과 정제 및 저장
5. 응답 생성

## 보안 고려사항

- API 키 보안
- 데이터 암호화
- 접근 제어
- 로깅 및 모니터링

## 개발 가이드라인

### 1. 코드 스타일

- PEP 8 준수
- Django 코딩 스타일 가이드 준수
- 타입 힌팅 사용

### 2. 테스트

```bash
# 테스트 실행
python manage.py test
```

### 3. 문서화

- 함수/클래스 문서화
- API 문서 유지
- 변경 이력 관리

## 라이센스

MIT License

## 연락처

프로젝트 관련 문의사항은 이슈를 통해 문의해주세요.
