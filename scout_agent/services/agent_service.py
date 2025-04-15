# services/agent_service.py
import json
from .openai_service import OpenAIService
from .pdf_service import PDFAnalysisService
from scout_agent.models import CompanyData, LeadProspect, CompanyProfile, PDFAnalysis


class LeadScoutAgent:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pdf_service = PDFAnalysisService()

    def find_potential_leads(self, company_id):
        """
        주어진 회사 ID를 기반으로 잠재적인 리드를 찾고 저장합니다.

        1. 회사의 PDF 프로필이 있는지 확인
        2. PDF 프로필이 있으면 분석본이 있는지 확인
        3. 분석본이 있으면 바로 사용, 없으면 분석 생성
        4. 수집된 정보를 바탕으로 OpenAI의 웹서치 도구를 활용하여 잠재적 리드를 생성
        """
        try:
            print(f"리드 검색 시작: company_id={company_id}")

            # 소스 회사 정보 가져오기
            source_company = CompanyData.objects.get(id=company_id)
            print(f"소스 회사: {source_company.company}")

            # 회사에 대한 PDF 프로필이 있는지 확인
            company_profiles = CompanyProfile.objects.filter(company=source_company)
            pdf_analyses = []

            if company_profiles.exists():
                print(f"PDF 프로필 발견: {company_profiles.count()}개")
                
                for profile in company_profiles:
                    try:
                        # 기존 분석본 확인
                        existing_analysis = PDFAnalysis.objects.filter(
                            company=source_company,
                            profile=profile
                        ).first()
                        
                        if existing_analysis:
                            print(f"기존 PDF 분석본 사용: {profile.url}")
                            pdf_analyses.append({
                                'company': profile.company,
                                'profile': profile,
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
                            })
                        else:
                            print(f"새로운 PDF 분석 생성: {profile.url}")
                            
                            analysis = self.pdf_service.analyze_company_pdf(profile)
                            if analysis:
                                pdf_analyses.append({
                                    'company': profile.company,
                                    'profile': profile,
                                    'industry': analysis.get('industry'),
                                    'sales': analysis.get('sales'),
                                    'total_funding': analysis.get('total_funding'),
                                    'homepage': analysis.get('homepage'),
                                    'key_executive': analysis.get('key_executive'),
                                    'address': analysis.get('address'),
                                    'email': analysis.get('email'),
                                    'phone_number': analysis.get('phone_number'),
                                    'company_description': analysis.get('company_description'),
                                    'products_services': analysis.get('products_services'),
                                    'target_customers': analysis.get('target_customers'),
                                    'competitors': analysis.get('competitors'),
                                    'strengths': analysis.get('strengths'),
                                    'business_model': analysis.get('business_model')
                                })
                    except Exception as e:
                        print(f"PDF 처리 중 오류: {e}")

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

            # OpenAI 서비스를 통해 잠재적인 리드 생성
            has_pdf = len(pdf_analyses) > 0
            leads_data = self.openai_service.generate_potential_leads(
                source_company, 
                pdf_analyses, 
                has_pdf
            )

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
                    continue

            print(f"총 {len(created_leads)}개의 리드 처리 완료")
            return {
                "status": "success",
                "message": f"Found {len(created_leads)} potential leads",
                "source_used": "pdf_analysis" if pdf_analyses else "web_search",
                "leads": created_leads
            }

        except CompanyData.DoesNotExist:
            print(f"회사 ID {company_id}를 찾을 수 없습니다")
            return {"status": "error", "message": "Source company not found"}
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return {"status": "error", "message": str(e)}

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