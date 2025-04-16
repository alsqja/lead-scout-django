# services/pdf_service.py
from openai import OpenAI
import fitz  # PyMuPDF
from django.conf import settings
import os
import json
import tempfile
import urllib.request
from django.db import transaction
from scout_agent.repository.PDFAnalysis_repository import post_pdf_analysis


class PDFAnalysisService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def analyze_company_pdf(self, company_profile):
        """
        PDF 파일을 분석하여 회사 정보를 추출하고 DB에 저장합니다.

        Returns:
            dict: 추출된 회사 정보
        """
        try:
            # PDF 텍스트 추출
            extracted_text = self._extract_text_from_pdf(company_profile.url)
            if not extracted_text:
                print("PDF에서 텍스트를 추출할 수 없습니다.")
                return {}

            # OpenAI를 사용하여 텍스트에서 회사 정보 추출
            company_info = self._extract_company_info_with_ai(extracted_text, company_profile.company.company)

            with transaction.atomic():
                pdf_analysis, created = post_pdf_analysis(
                    company_profile.company,
                    company_profile,
                    {
                        # 기본 회사 정보
                        'industry': company_info.get('industry'),
                        'sales': company_info.get('sales'),
                        'total_funding': company_info.get('total_funding'),
                        'homepage': company_info.get('homepage'),
                        'key_executive': company_info.get('key_executive'),
                        'address': company_info.get('address'),
                        'email': company_info.get('email'),
                        'phone_number': company_info.get('phone_number'),
                        
                        # 상세 정보
                        'company_description': company_info.get('company_description'),
                        'products_services': company_info.get('products_services'),
                        'target_customers': company_info.get('target_customers'),
                        'competitors': company_info.get('competitors'),
                        'strengths': company_info.get('strengths'),
                        'business_model': company_info.get('business_model')
                    }
                )

            return company_info

        except Exception as e:
            print(f"PDF 분석 중 오류 발생: {e}")
            return {}

    def _extract_text_from_pdf(self, pdf_path):
        """
        PyMuPDF를 사용하여 PDF에서 텍스트를 추출합니다.
        """
        try:
            downloaded_path = self._download_pdf(pdf_path)
            text = ""
            # PDF 파일 열기
            with fitz.open(downloaded_path) as doc:
                # 각 페이지의 텍스트 추출
                for page in doc:
                    text += page.get_text()

            # 텍스트가 너무 길면 잘라내기 (OpenAI API 제한 고려)
            max_length = 15000
            if len(text) > max_length:
                print(f"PDF 텍스트가 너무 길어 {max_length}자로 제한합니다.")
                text = text[:max_length]

            os.remove(downloaded_path)
            
            return text
        except Exception as e:
            print(f"PDF 텍스트 추출 오류: {e}")
            return ""

    def _download_pdf(self, url):
        """URL에서 PDF 파일을 다운로드하고 임시 파일 경로를 반환합니다."""
        try:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_path = temp_file.name

            # PDF 다운로드
            urllib.request.urlretrieve(url, temp_path)
            print(f"PDF 다운로드 완료: {url}")
            return temp_path
        except Exception as e:
            print(f"PDF 다운로드 오류: {e}")
            return None
        
    def _extract_company_info_with_ai(self, text, company_name):
        """
        OpenAI API를 사용하여 PDF 텍스트에서 회사 정보를 추출합니다.
        """
        try:
            prompt = f"""
            당신은 회사 분석 전문가입니다. 아래 제공된 PDF에서 추출한 텍스트를 분석하여 "{company_name}" 회사에 대한 상세 정보를 추출해주세요.

            다음 정보들을 최대한 정확하게 찾아 JSON 형식으로 반환해주세요:
            
            # 기본 회사 정보
            - industry: 회사의 산업 분야 (예: "소프트웨어", "제조업" 등)
            - sales: 연간 매출액 (숫자만, 단위 없이)
            - total_funding: 총 투자 유치 금액 (숫자만, 단위 없이)
            - homepage: 회사 홈페이지 URL
            - key_executive: 주요 경영진 (CEO 등)
            - address: 회사 주소
            - email: 연락 이메일
            - phone_number: 연락처
            
            # 상세 정보
            - company_description: 회사 설명 및 핵심 사업 분야 (500자 이내)
            - products_services: 주요 제품 및 서비스 (쉼표로 구분된 목록)
            - target_customers: 주요 타겟 고객층 (쉼표로 구분된 목록)
            - competitors: 주요 경쟁사 (쉼표로 구분된 목록)
            - strengths: 회사의 강점 (쉼표로 구분된 목록)
            - business_model: 비즈니스 모델 설명 (300자 이내)

            텍스트에서 명확하게 확인할 수 없는 정보는 null로 표시하거나 생략하세요. 
            특히 매출액이나 투자금액은 확실한 숫자만 포함하고 추측하지 마세요.

            분석할 PDF 텍스트:
            {text}

            JSON 형식으로만 응답해주세요. 다른 텍스트나 설명은 포함하지 마세요.
            """

            # GPT-4 API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "You are a company analysis expert that extracts structured information from PDF documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # JSON 응답 추출 및 파싱
            result = response.choices[0].message.content
            company_info = json.loads(result)
            print(f"회사 정보 추출 완료: {company_name} \n {company_info}")

            return company_info

        except Exception as e:
            print(f"AI를 사용한 정보 추출 오류: {e}")
            return {}