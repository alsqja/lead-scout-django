# services/openai_service.py
from openai import OpenAI
from django.conf import settings
import json

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_potential_leads(self, company_data):
        """
        OpenAI API의 Responses API와 웹서치 도구를 사용하여 주어진 회사 정보를 기반으로 잠재적인 리드를 생성합니다.
        """
        # 모델 지정
        model = "gpt-4o"

        # 회사 정보 준비
        company_context = {
            "name": company_data.company,
            "industry": company_data.industry,
            "sales": float(company_data.sales) if company_data.sales else None,
            "total_funding": float(company_data.total_funding) if company_data.total_funding else None,
            "homepage": company_data.homepage if company_data.homepage else None,
        }

        # 프롬프트 준비
        prompt = f"""
        당신은 영업 리드 스카우트 전문가입니다. 
        아래 회사 정보를 기반으로 잠재적인 영업 타겟이 될 수 있는 회사 5개를 찾아주세요.
        필요한 경우 웹 검색을 통해 최신 정보를 확인하세요.

        소스 회사 정보:
        - 회사명: {company_data.company}
        - 산업: {company_data.industry or "정보 없음"}
        - 매출: {company_data.sales or "정보 없음"}
        - 총 펀딩: {company_data.total_funding or "정보 없음"}
        - 홈페이지: {company_data.homepage or "정보 없음"}

        응답은 다음 JSON 형식으로 제공해주세요:
        {{
            "leads": [
                {{
                    "company": "회사명",
                    "industry": "산업",
                    "sales": 매출액(숫자),
                    "total_funding": 총 펀딩 금액(숫자),
                    "homepage": "웹사이트 URL", 
                    "key_executive": "주요 경영진",
                    "relevance_score": 0.0~1.0 사이의 관련성 점수,
                    "reasoning": "해당 회사가 좋은 타겟인 이유"
                }},
                ...
            ]
        }}

        중요: 
        1. 실제로 확인된 정보만 포함하세요. 
        2. 홈페이지 URL은 반드시 실제 존재하는 URL만 제공하고, 확실하지 않은 경우 빈 문자열("")로 남겨두세요.
        3. 단순히 회사명을 기반으로 URL을 추측하지 마세요.
        4. 웹 검색을 통해 확인된 정보만 포함하세요.
        
        소스 회사의 제품이나 서비스로부터 혜택을 받을 가능성이 높은 회사나 보완적인 산업에서 운영되는 회사에 집중해주세요.
        """

        # API 호출 전 로그 출력
        print(f"OpenAI Responses API 호출 - 웹서치 도구 활성화")

        try:
            # Responses API와 웹서치 도구 사용
            response = self.client.responses.create(
                model=model,
                input=prompt,
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "medium",
                }],
                tool_choice={"type": "web_search_preview"}  # 웹 검색 도구 강제 사용
            )

            # 응답 추출
            output_text = response.output_text
            print(f"OpenAI API 응답: {output_text}...")

            try:
                # JSON 파싱
                leads_data = json.loads(output_text)
                return leads_data
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                # JSON 형식이 아닌 경우 빈 리드 목록 반환
                try:
                    # { 부터 } 까지의 내용만 추출
                    json_start = output_text.find('{')
                    json_end = output_text.rfind('}') + 1

                    if 0 <= json_start < json_end:
                        cleaned_json = output_text[json_start:json_end]
                        print(f"정제된 JSON: {cleaned_json}...")
                        return json.loads(cleaned_json)
                    else:
                        return {"leads": []}
                except Exception as e2:
                    print(f"정제 시도 후에도 파싱 오류: {e2}")
                    return {"leads": []}

        except Exception as e:
            print(f"OpenAI API 호출 오류: {e}")
            return None