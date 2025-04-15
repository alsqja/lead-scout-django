# services/openai_service.py
from openai import OpenAI
from django.conf import settings
import json


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_potential_leads(self, company_data, pdf_analyses=None, has_pdf=False):
        """
        OpenAI API의 Responses API와 웹서치 도구를 사용하여 주어진 회사 정보를 기반으로 잠재적인 리드를 생성합니다.
        PDF 분석 결과가 있는 경우 이를 함께 활용합니다.
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
            "key_executive": company_data.key_executive if company_data.key_executive else None,
            "address": company_data.address if company_data.address else None,
            "email": company_data.email if company_data.email else None,
            "phone_number": company_data.phone_number if company_data.phone_number else None,
        }

        # PDF 분석 결과가 있는 경우 추가 정보 구성
        additional_info = ""
        if pdf_analyses and has_pdf:
            additional_info = self._prepare_pdf_analysis_info(pdf_analyses)

        # 프롬프트 준비
        prompt = f"""
        당신은 B2B 영업 리드 스카우트 전문가입니다. 
        아래 회사 정보를 기반으로 이 회사에 제품이나 서비스를 판매하기에 적합한 잠재적인 영업 타겟이 될 수 있는 회사 5개를 찾아주세요.

        소스 회사 정보:
        - 회사명: {company_data.company}
        - 산업: {company_data.industry or "정보 없음"}
        - 매출: {company_data.sales or "정보 없음"}
        - 총 펀딩: {company_data.total_funding or "정보 없음"}
        - 홈페이지: {company_data.homepage or "정보 없음"}
        - 주요 경영진: {company_data.key_executive or "정보 없음"}
        - 주소: {company_data.address or "정보 없음"}
        - 이메일: {company_data.email or "정보 없음"}
        - 연락처: {company_data.phone_number or "정보 없음"}

        {additional_info}

        웹 검색을 통해 소스 회사에 대한 추가 정보를 확인하고, 다음과 같은 기준으로 잠재적 리드 대상 회사를 찾아주세요:

        1. 산업 시너지: 소스 회사와 상호보완적인 산업 또는 동일 산업 내에서 협력 가능성이 있는 회사, 산업군은 NCS 기준으로 경쟁업체이면 배제
        2. 비즈니스 모델 적합성: 소스 회사의 제품/서비스를 활용하여 비즈니스를 개선할 수 있는 회사
        3. 성장 단계 적합성: 소스 회사의 솔루션을 필요로 할 가능성이 높은 성장 단계에 있는 회사
        4. 잠재적 파트너십 가능성: 전략적 제휴나 협업을 통해 상호 이익을 얻을 수 있는 회사
        5. 시장 접근성: 비즈니스 네트워크상 소스 회사가 접근하기 좋은 회사
        6. 장소: 국가는 대한민국, 지역은 소스 회사와 가까울수록 선호
        7. 직원수, 매출, 순이익: 많을수록 선호
        8. 당면 문제: 소스 회사가 해결하는 문제와 유사할수록 선호

        리드 대상 회사의 관련성 점수(relevance_score)는 다음 항목 기준 가중치를 적용하여 산출해주세요:
        
        | 항목 | 기준 | 가중치(%) | 설명 |
        |------|------|-----------|------|
        | 산업군 적합성 | 코어 타깃 산업군 포함 여부 | 30% | 예: IT, 제조, 환경 분야 등 |
        | 매출 규모 | 최근 매출 규모 | 20% | 일정 매출 이상일수록 가산점 |
        | 성장성 | 최근 3년 평균 성장률 | 20% | 고성장 기업에 가산점 |
        | 지역성 | 특정 지역(예: 수도권, 해외시장) 여부 | 10% | 전략 지역 포함 시 추가 점수 |
        | 뉴스/이슈 노출 | 최근 1년 내 긍정 뉴스 기사 수 | 10% | 긍정적 이슈 많은 기업 우대 |
        | 비즈니스 적합성 | 소스 회사 제품/서비스 활용 가능성 | 10% | 활용 시나리오가 명확할수록 가산점 |
        
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
                    "address": "회사 주소",
                    "email": "연락 이메일",
                    "phone_number": "연락처",
                    "relevance_score": 0.0~1.0 사이의 관련성 점수,
                    "reasoning": "이 회사가 소스 회사에게 좋은 영업 타겟인 이유를 구체적으로 설명 (산업 시너지, 비즈니스 모델 적합성 등을 기반으로)"
                }},
                ...
            ]
        }}

        중요: 
        1. 실제로 확인된 정보만 포함하세요. 
        2. 홈페이지 URL은 반드시 실제 존재하는 URL만 제공하고, 확실하지 않은 경우 빈 문자열("")로 남겨두세요.
        3. 단순히 회사명을 기반으로 URL을 추측하지 마세요.
        4. 웹 검색을 통해 확인된 정보만 포함하세요.
        5. 추천하는 회사가 실제로 소스 회사의 제품/서비스로 혜택을 얻을 수 있는지, 구체적인 협업 가능성이 있는지 명확히 설명하세요.
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
            print(f"OpenAI API 응답 시작: {output_text}...")

            try:
                # JSON 파싱
                leads_data = json.loads(output_text)
                return leads_data
            except json.JSONDecodeError as e:
                print(f"JSON 파싱 오류: {e}")
                # JSON 형식이 아닌 경우 파싱 시도
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

    def _prepare_pdf_analysis_info(self, pdf_analyses):
        """
        PDF 분석 결과를 프롬프트에 포함할 수 있는 형태로 가공합니다.
        """
        if not pdf_analyses:
            return ""

        # 여러 PDF 분석 결과를 통합
        combined_info = {}

        for analysis in pdf_analyses:
            for key, value in analysis.items():
                if value and key not in combined_info:
                    combined_info[key] = value

        # 프롬프트에 추가할 정보 구성
        additional_info = "\nPDF 분석에서 추출한 추가 정보:\n"

        if 'company_description' in combined_info:
            additional_info += f"- 회사 설명: {combined_info['company_description']}\n"

        if 'products_services' in combined_info:
            additional_info += f"- 주요 제품/서비스: {combined_info['products_services']}\n"

        if 'target_customers' in combined_info:
            additional_info += f"- 주요 고객층: {combined_info['target_customers']}\n"

        if 'competitors' in combined_info:
            additional_info += f"- 주요 경쟁사: {combined_info['competitors']}\n"

        if 'strengths' in combined_info:
            additional_info += f"- 회사 강점: {combined_info['strengths']}\n"

        if 'business_model' in combined_info:
            additional_info += f"- 비즈니스 모델: {combined_info['business_model']}\n"

        return additional_info