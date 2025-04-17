from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.http import HttpResponse


class LeadDataView(APIView):
    def post(self, request):
        """
        회사 이름을 받아 해당 회사의 상세 정보를 반환합니다.
        """
        company_name = request.data.get('company_name')

        if not company_name:
            return Response(
                {"error": "company_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 여기서 비즈니스 로직을 통해 회사 정보를 가져옵니다
        # 예시 데이터
        company_data = {
            'company_name': company_name,
            'industry_keywords': '인공지능, 빅데이터, 클라우드 컴퓨팅',
            'homepage_url': 'https://example.com',
            'company_address': '서울특별시 강남구 테헤란로 123',
            'key_executives': '홍길동 대표이사, 김철수 CTO',
            'founded_date': '2015년 3월 12일',
            'company_summary': '본 기업은 인공지능 기반 빅데이터 분석 솔루션을 제공하는 기술 기업입니다. 특히 금융 및 헬스케어 분야에서 뛰어난 성과를 보여주고 있으며, 최근 글로벌 시장 진출을 시작했습니다.',
            'target_customers': 'B2B 엔터프라이즈, 중견기업, 금융기관, 의료기관',
            'financial_info': '연매출 약 50억원 (2023년 기준), 시리즈 B 100억원 투자 유치(2022년), 연간 성장률 35%',
            'recent_trends': '최근 동남아시아 시장 진출, AI 기반 신규 서비스 출시 예정',
            'competitors': '데이터인사이트(주), AI솔루션즈, 글로벌테크',
            'strengths': '독자적인 AI 알고리즘 보유, 높은 데이터 처리 효율성, 산업별 특화 솔루션 제공',
            'risk_factors': '클라우드 서비스 의존도가 높음, 최근 인력 구조조정 소문, 주요 기술 특허 관련 소송 진행 중',
            'lead_score': 8,
            'news_links': [
                {
                    'title': f'{company_name}, 50억 규모 시리즈 B 투자 유치',
                    'url': 'https://example.com/news/1',
                    'date': '2023-11-15',
                    'source': '테크뉴스'
                },
                {
                    'title': f'{company_name} 동남아 시장 진출 본격화',
                    'url': 'https://example.com/news/2',
                    'date': '2023-09-22',
                    'source': '비즈니스저널'
                },
                {
                    'title': f'{company_name}-글로벌테크, 전략적 제휴 체결',
                    'url': 'https://example.com/news/3',
                    'date': '2023-07-03',
                    'source': '경제매거진'
                }
            ],
            'logo_url': f'https://logo.clearbit.com/{company_name.lower().replace(" ", "")}.com'
        }

        # HTML 템플릿 렌더링
        html_content = render_to_string('lead_data_template.html', company_data)

        # HTML 콘텐츠 직접 반환
        return HttpResponse(html_content, content_type='text/html')