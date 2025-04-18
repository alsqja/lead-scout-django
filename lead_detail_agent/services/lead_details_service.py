import json
import logging
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger('scout_agent')


class LeadDetailsService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def search_company_details(self, company_name):
        """
        회사명을 기반으로 웹 서치를 수행하고 정보를 분석합니다.

        Args:
            company_name (str): 검색할 회사명

        Returns:
            dict: 분석된 회사 정보
        """
        try:
            # 웹 서치 프롬프트 생성
            search_prompt = f"""
            당신은 기업 정보 분석 전문가입니다. "{company_name}" 회사에 대한 최신 정보를 웹에서 검색하고 분석해주세요.

            다음 정보들을 최대한 정확하게 찾아 JSON 형식으로 반환해주세요:

            - company_name: 회사명
            - industry_keywords: 산업 키워드 (쉼표로 구분)
            - homepage_url: 회사 홈페이지 URL
            - company_address: 회사 주소
            - key_executives: 주요 경영진 (쉼표로 구분)
            - founded_date: 설립일
            - company_summary: 회사 요약 (500자 이내)
            - target_customers: 주요 타겟 고객 (쉼표로 구분)
            - financial_info: 재무 정보 (매출, 투자, 성장률 등 string 형식 / 로 구분)
            - recent_trends: 최근 동향 (300자 이내)
            - competitors: 주요 경쟁사 (쉼표로 구분)
            - strengths: 회사의 강점 (쉼표로 구분)
            - risk_factors: 위험 요인 (쉼표로 구분)
            - lead_score: 리드 점수 (1-10)
            - news_links: 최신 뉴스 목록 (최대 3개)
                - title: 뉴스 제목
                - url: 뉴스 URL
                - date: 뉴스 날짜
                - source: 뉴스 출처
            - logo_url: 회사 로고 URL

            텍스트에서 명확하게 확인할 수 없는 정보는 null로 표시하세요. 
            특히 매출액이나 투자금액은 확실한 숫자만 포함하고 추측하지 마세요.

            JSON 형식으로만 응답해주세요. 다른 텍스트나 설명은 포함하지 마세요.
            반드시 유효한 JSON 형식으로만 응답하세요. 모든 문자열은 쌍따옴표로 감싸고, 콤마와 중괄호가 올바르게 배치되어야 합니다. 
            코드 블록이나 마크다운 포맷팅 없이 순수한 JSON만 반환하세요.
            """

            # GPT-4 API 호출
            response = self.client.responses.create(
                model="gpt-4o",
                input=search_prompt,
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "medium",
                }],
                tool_choice={"type": "web_search_preview"},
            )

            # JSON 응답 추출 및 파싱
            result = response.output_text
            logger.info(f"회사 정보 응답: {result}")

            # 응답이 비어있는지 확인
            if not result.strip():
                logger.error("빈 응답이 반환되었습니다.")
                return {"status": "error", "message": "빈 응답"}

            # JSON 형식인지 확인 및 정리
            try:
                # JSON 부분만 추출 (응답에 다른 텍스트가 포함된 경우)
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
                if json_match:
                    result = json_match.group(1)

                company_info = json.loads(result)
                return company_info
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {str(e)}, 원본 텍스트: {result}")
                return {"status": "error", "message": f"JSON 파싱 오류: {str(e)}"}

        except Exception as e:
            logger.error(f"회사 정보 검색 중 오류 발생: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

