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
SECRET_KEY=your-secret-key
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

### 2. PDF 분석

#### PDF 분석 요청

```http
POST /api/analyze-pdf/
Content-Type: application/json

{
    "profile_id": 1
}
```

응답:

```json
{
  "status": "success",
  "message": "PDF analysis completed successfully",
  "analysis": {
    "industry": "소프트웨어",
    "sales": null,
    "total_funding": null,
    "homepage": null,
    "key_executive": "권태욱 대표이사",
    "address": null,
    "email": "david@goodai.kr",
    "phone_number": "010-8536-2267",
    "company_description": "더선한 주식회사는 AI 기반의 세일즈 인텔리전스 소프트웨어를 개발하여 B2B 세일즈 효율성을 극대화하는 솔루션을 제공합니다. 주요 기술로는 AI 에이전트, 자연어 처리, 데이터 레이크 구축 등이 있으며, 이를 통해 잠재고객 추천 및 거래 성사율을 높이는 데 주력하고 있습니다.",
    "products_services": "AI 기반 세일즈 인텔리전스 소프트웨어, 잠재고객 추천 알고리즘, 데이터 레이크 구축",
    "target_customers": "B2B 기업, 세일즈 팀, 마케팅 팀",
    "competitors": "줌인포, 링크드인, 마이크로소프트",
    "strengths": "AI 기반 기술, 세일즈 효율성 극대화, 잠재고객 추천",
    "business_model": "AI 기술을 활용하여 B2B 세일즈 프로세스를 자동화하고, 잠재고객 추천 및 거래 성사율을 높이는 소프트웨어 솔루션을 제공합니다."
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
    "sales": null,
    "total_funding": null,
    "homepage": null,
    "key_executive": "권태욱 대표이사",
    "address": null,
    "email": "david@goodai.kr",
    "phone_number": "010-8536-2267",
    "company_description": "더선한 주식회사는 AI 기반의 세일즈 인텔리전스 소프트웨어를 개발하여 B2B 세일즈 효율성을 극대화하는 솔루션을 제공합니다. 주요 기술로는 AI 에이전트, 자연어 처리, 데이터 레이크 구축 등이 있으며, 이를 통해 잠재고객 추천 및 거래 성사율을 높이는 데 주력하고 있습니다.",
    "products_services": "AI 기반 세일즈 인텔리전스 소프트웨어, 잠재고객 추천 알고리즘, 데이터 레이크 구축",
    "target_customers": "B2B 기업, 세일즈 팀, 마케팅 팀",
    "competitors": "줌인포, 링크드인, 마이크로소프트",
    "strengths": "AI 기반 기술, 세일즈 효율성 극대화, 잠재고객 추천",
    "business_model": "AI 기술을 활용하여 B2B 세일즈 프로세스를 자동화하고, 잠재고객 추천 및 거래 성사율을 높이는 소프트웨어 솔루션을 제공합니다.",
    "created_at": "2025-04-15T10:25:10.581634Z",
    "updated_at": "2025-04-15T10:25:10.581710Z"
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
    "message": "Found 5 potential leads",
    "source_used": "pdf_analysis",
    "leads": [
        {
            "company": "삼성전자",
            "industry": "전자제품 제조",
            "sales": 230000000000.0,
            "total_funding": 0.0,
            "homepage": "https://www.samsung.com/",
            "key_executive": "이재용",
            "relevance_score": 0.85,
            "reasoning": "삼성전자는 다양한 B2B 제품과 서비스를 제공하며, 대규모 세일즈 팀을 운영하고 있습니다. 더선한 주식회사의 AI 기반 세일즈 인텔리전스 소프트웨어를 활용하여 세일즈 리드 추천 및 거래 성사율을 높일 수 있습니다. 또한, 삼성전자의 글로벌 네트워크를 통해 더선한 주식회사의 솔루션을 해외 시장에 확장할 수 있는 기회도 있습니다."
        },
        .
        .
        .
        5개 출력
    ]
}
```

## 시스템 아키텍처

### 1. 데이터 흐름

1. 기업 프로필 생성(api x)
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
