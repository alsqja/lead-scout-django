# services/agent_service.py
import json
import os
import tempfile
import urllib.request
from .openai_service import OpenAIService
from .pdf_service import PDFAnalysisService
from scout_agent.models import CompanyData, LeadProspect, CompanyProfile


class LeadScoutAgent:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pdf_service = PDFAnalysisService()

    def find_potential_leads(self, company_id):
        """
        주어진 회사 ID를 기반으로 잠재적인 리드를 찾고 저장합니다.

        1. 회사의 PDF 프로필이 있는지 확인하고 있으면 PDF 분석을 통해 상세 정보를 추출합니다.
        2. PDF 프로필이 없으면 기존 DB 정보와 웹 검색을 통해 회사 정보를 수집합니다.
        3. 수집된 정보를 바탕으로 OpenAI의 웹서치 도구를 활용하여 잠재적 리드를 생성합니다.
        """
        try:
            print(f"리드 검색 시작: company_id={company_id}")

            # 소스 회사 정보 가져오기
            source_company = CompanyData.objects.get(id=company_id)
            print(f"소스 회사: {source_company.company}")

            # 회사에 대한 PDF 프로필이 있는지 확인
            company_profiles = CompanyProfile.objects.filter(company=source_company)

            # 회사 정보를 저장할 딕셔너리
            company_context = {
                "name": source_company.company,
                "industry": source_company.industry,
                "sales": float(source_company.sales) if source_company.sales else None,
                "total_funding": float(source_company.total_funding) if source_company.total_funding else None,
                "homepage": source_company.homepage if source_company.homepage else None,
                "key_executive": source_company.key_executive if source_company.key_executive else None,
                "address": source_company.address if source_company.address else None,
                "email": source_company.email if source_company.email else None,
                "phone_number": source_company.phone_number if source_company.phone_number else None,
            }

            pdf_analysis_results = []

            # PDF 프로필이 있으면 분석하여 정보 추출
            if company_profiles.exists():
                print(f"PDF 프로필 발견: {company_profiles.count()}개")

                for profile in company_profiles:
                    try:
                        # PDF 다운로드 및 분석
                        pdf_path = self._download_pdf(profile.url)
                        if pdf_path:
                            pdf_analysis = self.pdf_service.analyze_company_pdf(pdf_path, source_company.company)
                            pdf_analysis_results.append(pdf_analysis)

                            # 임시 파일 삭제
                            os.remove(pdf_path)
                    except Exception as e:
                        print(f"PDF 처리 중 오류: {e}")

                # PDF 분석 결과가 있으면 회사 정보 업데이트
                if pdf_analysis_results:
                    enriched_info = self._enrich_company_info(company_context, pdf_analysis_results)

                    # DB에 회사 정보 업데이트
                    self._update_company_data(source_company, enriched_info)

                    # 업데이트된 정보로 company_context 갱신
                    company_context.update(enriched_info)
            else:
                print("PDF 프로필 없음, 기존 DB 정보 사용")

            # OpenAI 서비스를 통해 잠재적인 리드 생성
            has_pdf = len(pdf_analysis_results) > 0
            leads_data = self.openai_service.generate_potential_leads(source_company, pdf_analysis_results, has_pdf)

            if not leads_data:
                print("OpenAI 응답이 비어있습니다")
                return {"status": "error", "message": "Failed to generate leads - empty response"}

            # leads 키가 있는지 확인
            if 'leads' not in leads_data:
                print("'leads' 키를 찾을 수 없습니다")
                return {"status": "error", "message": "Invalid response format - 'leads' key not found"}

            # 각 리드에 대해 처리
            print(f"총 {len(leads_data['leads'])}개의 리드 처리 시작")
            created_leads = []

            for lead in leads_data['leads']:
                try:
                    # 회사 이름으로 기존 레코드 확인
                    company_name = lead.get('company', 'Unknown')
                    print(f"리드 처리 중: {company_name}")

                    prospect, created = CompanyData.objects.get_or_create(
                        company=company_name,
                        defaults={
                            'industry': lead.get('industry'),
                            'sales': lead.get('sales'),
                            'total_funding': lead.get('total_funding'),
                            'homepage': lead.get('homepage'),
                            'key_executive': lead.get('key_executive'),
                            'address': lead.get('address'),
                            'email': lead.get('email'),
                            'phone_number': lead.get('phone_number')
                        }
                    )

                    # 리드 관계 생성 또는 업데이트
                    lead_relation, relation_created = LeadProspect.objects.update_or_create(
                        source_company=source_company,
                        prospect_company=prospect,
                        defaults={
                            'relevance_score': lead.get('relevance_score', 0.0),
                            'reasoning': lead.get('reasoning', '')
                        }
                    )

                    created_leads.append({
                        'company': prospect.company,
                        'industry': prospect.industry,
                        'sales': prospect.sales,
                        'total_funding': prospect.total_funding,
                        'homepage': prospect.homepage,
                        'key_executive': prospect.key_executive,
                        'relevance_score': lead_relation.relevance_score,
                        'reasoning': lead_relation.reasoning
                    })

                except Exception as e:
                    print(f"리드 처리 중 오류: {e}")
                    # 개별 리드 처리 오류는 전체 프로세스를 중단하지 않음
                    continue

            print(f"총 {len(created_leads)}개의 리드 처리 완료")
            return {
                "status": "success",
                "message": f"Found {len(created_leads)} potential leads",
                "source_used": "pdf_analysis" if pdf_analysis_results else "web_search",
                "leads": created_leads
            }

        except CompanyData.DoesNotExist:
            print(f"회사 ID {company_id}를 찾을 수 없습니다")
            return {"status": "error", "message": "Source company not found"}
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return {"status": "error", "message": str(e)}

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

    def _enrich_company_info(self, base_info, pdf_analyses):
        """PDF 분석 결과를 기반으로 회사 정보를 강화합니다."""
        # 병합할 새 정보 초기화
        enriched_info = {}

        # 각 PDF 분석 결과에서 정보 추출
        for analysis in pdf_analyses:
            for key, value in analysis.items():
                # PDF에서 추출한 정보가 있고, 기존 정보가 없거나 덜 구체적인 경우 업데이트
                if value and (key not in base_info or not base_info[key]):
                    enriched_info[key] = value

        return enriched_info

    def _update_company_data(self, company, enriched_info):
        """회사 데이터를 업데이트합니다."""
        fields_to_update = {
            'industry': 'industry',
            'sales': 'sales',
            'total_funding': 'total_funding',
            'homepage': 'homepage',
            'key_executive': 'key_executive',
            'address': 'address',
            'email': 'email',
            'phone_number': 'phone_number',
        }

        update_fields = {}
        for model_field, info_field in fields_to_update.items():
            if info_field in enriched_info and enriched_info[info_field]:
                update_fields[model_field] = enriched_info[info_field]

        if update_fields:
            for field, value in update_fields.items():
                setattr(company, field, value)
            company.save()
            print(f"회사 정보 업데이트: {update_fields.keys()}")