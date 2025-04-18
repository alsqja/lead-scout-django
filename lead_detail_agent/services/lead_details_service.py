import json
import logging
import re

from django.conf import settings
from openai import OpenAI

from scout_agent.repository.PDFAnalysis_repository import get_pdf_analysis_by_company_id

logger = logging.getLogger('scout_agent')


class LeadDetailsService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def search_company_details(self, search_company_name, company_id):
        """
        회사명을 기반으로 4개의 카테고리로 나눠 검색하고, 정보를 통합하여 반환합니다.
        """
        combined_data = {}

        # 설명 포함 필드 정의
        prompt_categories = {
            "basic": {
                "company_name": "회사명",
                "industry_keywords": "산업 키워드 (쉼표로 구분)",
                "homepage_url": "회사 홈페이지 URL",
                "company_address": "회사 주소",
                "key_executives": "주요 경영진 (쉼표로 구분)",
                "founded_date": "설립일"
            },
            "summary_finance": {
                "company_summary": "회사 요약 (500자 이내)",
                "target_customers": "주요 타겟 고객 (쉼표로 구분)",
                "financial_info": "재무 정보 (매출, 투자, 성장률 등 string 형식 / 로 구분)",
                "recent_trends": "최근 동향 (300자 이내)"
            },
            "competition": {
                "competitors": "주요 경쟁사 (쉼표로 구분)",
                "strengths": "회사의 강점 (쉼표로 구분)",
                "risk_factors": "위험 요인 (쉼표로 구분)",
                "lead_score": "리드 점수 (1-10)"
            },
            "news": {
                "news_links": "최신 뉴스 목록 (최대 3개)\n  - title: 뉴스 제목\n  - url: 뉴스 URL\n  - date: 뉴스 날짜\n  - source: 뉴스 출처"
            }
        }

        existing_analysis = get_pdf_analysis_by_company_id(company_id).first()

        company_data = {
            'company': existing_analysis.company.company,
            'industry': existing_analysis.industry,
            'sales': existing_analysis.sales,
            'total_funding': existing_analysis.total_funding,
            'homepage': existing_analysis.homepage,
            'key_executive': existing_analysis.key_executive,
            'address': existing_analysis.address,
            'email': existing_analysis.email,
            'phone_number': existing_analysis.phone_number,
            'company_description': existing_analysis.company_description,
            'products_services': existing_analysis.products_services,
            'target_customers': existing_analysis.target_customers,
            'competitors': existing_analysis.competitors,
            'strengths': existing_analysis.strengths,
            'business_model': existing_analysis.business_model
        }

        # 각 그룹에 대해 순차적으로 GPT 호출
        for category, field_map in prompt_categories.items():
            prompt = self._build_prompt(search_company_name, field_map, company_data)

            try:
                result_json = self._call_gpt(prompt)
                print(prompt)
                print(result_json)
                combined_data.update(result_json)
            except Exception as e:
                logger.error(f"{category} 정보 처리 중 오류 발생: {str(e)}")
                combined_data[category] = {"status": "error", "message": str(e)}

        print(f"회사 정보 응답: {combined_data}")

        return combined_data

    def _build_prompt(self, company_name, field_map, company_data):
        """
        설명 포함된 프롬프트를 구성합니다.
        """
        field_str = "\n".join([f"- {key}: {desc}" for key, desc in field_map.items()])
        return f"""
당신은 {company_data.get('company')} 회사에 재직중인 기업 정보 분석 전문가입니다. 

{company_data.get('company')} 회사 자료는 다음과 같습니다.

{company_data}

회사 자료를 바탕으로 소스 회사가 "{company_name}" 회사에 영업 미팅을 할 수 있게 정보를 구성해주세요.
"{company_name}" 회사에 대한 최신 정보들을 웹에서 검색하고 분석해주세요.

다음 정보들을 최대한 정확하게 찾아 JSON 형식으로 반환해주세요:

{field_str}

조건:
- JSON 형식으로만 응답해주세요.
- 정보가 명확하지 않거나 확인할 수 없다면 정보 없음 으로 표시해주세요.
- 텍스트 외 다른 포맷 (코드블록, 마크다운 등)은 절대 포함하지 마세요.
- 모든 문자열은 반드시 쌍따옴표로 감싸주세요.
        """.strip()

    def _call_gpt(self, prompt):
        """
        OpenAI GPT-4o 모델을 통해 프롬프트에 대한 응답을 요청하고 JSON 파싱합니다.
        """
        response = self.client.responses.create(
            model="gpt-4o",
            input=prompt,
            tools=[{
                "type": "web_search_preview",
                "search_context_size": "medium",
            }],
            tool_choice={"type": "web_search_preview"},
        )

        result = response.output_text.strip()

        result = self._extract_json(result)

        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {str(e)}\n원본 응답:\n{result}")

    def _extract_json(self, text):
        """
        응답에서 JSON 부분만 추출 (코드 블록 제거)
        """
        json_match = re.search(r'```json\s*([\s\S]*?)```', text)
        if json_match:
            return json_match.group(1).strip()
        return text  # 그냥 텍스트 전체가 JSON일 경우
