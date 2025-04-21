import json
import logging

import requests
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger('scout_agent')


class LeadDetailsService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.tavily_api_key = settings.TAVILY_API_KEY

    def generate_queries(self, company_name):
        return {
            "industry_keywords": f"{company_name} 산업 분야",
            "homepage_url": f"{company_name} 공식 홈페이지",
            "key_executives": f"{company_name} CEO",
            "company_address": f"{company_name} 회사 주소",
            "company_summary": f"{company_name} 회사 설명",
            "target_customers": f"{company_name} 주요 타겟 고객층",
            "competitors": f"{company_name} 주요 경쟁사",
            "strengths": f"{company_name} 강점",
            "risk_factors": f"{company_name} 위험 요인",
            "recent_trends": f"{company_name} 최근 동향",
            "financial_info": f"{company_name} 재무 정보",
            "founded_date": f"{company_name} 설립일",
            "logo_url": f"{company_name} 로고 이미지 url"
        }

    def search_tavily(self, query, num_results=3):
        url = "https://api.tavily.com/search"
        headers = {
            "Authorization": f"Bearer {self.tavily_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "search_depth": "basic"
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])[:num_results]
            return [
                {"url": r.get("url"), "title": r.get("title"), "content": r.get("content", "")}
                for r in results if "content" in r and "url" in r
            ]
        except Exception as e:
            print(f"⚠️ Tavily 검색 실패: {e}")
            return []

    def get_latest_news_urls(self, company_name: str, count=3):
        query = f"{company_name} 최신 뉴스"
        url = "https://api.tavily.com/search"
        headers = {
            "Authorization": f"Bearer {self.tavily_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "search_depth": "basic"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])[:count]
            return [
                {
                    "title": r.get("title", "제목 없음"),
                    "url": r.get("url", "")
                }
                for r in results
            ]
        except Exception as e:
            print(f"❌ 최신 뉴스 검색 실패: {e}")
            return []

    def extract_info(self, company_name):
        queries = self.generate_queries(company_name)
        extracted_info = {}

        for field, query in queries.items():
            print(f"🔍 {field} → 검색 쿼리: {query}")
            sources = self.search_tavily(query)
            if not sources:
                print(f"⚠️ {field} 관련된 content 없음 (패스)")
                continue

            contents = [s["content"] for s in sources]
            urls = [
                {
                    "title": s.get("title", "제목 없음"),
                    "url": s.get("url", "")
                } for s in sources
            ]

            combined_content = "\n\n".join(contents)

            prompt = f"""
            당신은 회사 분석 전문가이며, '{company_name}'에 대한 내부 지식을 보유하고 있습니다.
            그러나 더 정확하고 최신 정보를 제공하기 위해 아래의 웹 검색 결과도 함께 참고해야 합니다.

            작업 목표:
            - '{field}' 항목에 대한 정확한 정보를 JSON 형식으로 추출합니다.
            - 내부 지식과 제공된 외부 웹 검색 내용을 통합하여 판단합니다.
            - 최신 정보나 수치(예: 매출, 대표자 등)는 아래 텍스트를 우선적으로 신뢰합니다.
            - 정보가 명확하지 않을 경우 null 또는 "정보 없음"으로 처리합니다.
            - 가능한 한 정확한 정보를 많이 제공하십시오.

            회사명: "{company_name}"
            요청 항목: "{field}"

            ### 참고용 외부 텍스트:
            {combined_content}

            ### 응답 형식 (JSON만 반환):
            {{
            "{field}": ...(내용은 문자열로 반환)
            }}
            """

            try:
                completion = self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": "You are a structured data extractor."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                field_result = json.loads(completion.choices[0].message.content)
                print(field_result)
                extracted_info[field] = field_result[field]
                extracted_info[f"{field}_sources"] = urls
            except Exception as e:
                print(f"❌ LLM 추출 실패 [{field}]: {e}")
                continue

        # 최신 뉴스 URL 리스트 추가
        # "url" 변수명 변경 가능
        extracted_info["news"] = self.get_latest_news_urls(company_name)
        extracted_info["company_name"] = company_name

        print(json.dumps(extracted_info, indent=2, ensure_ascii=False))

        return extracted_info
