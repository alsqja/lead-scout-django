# services/agent_service.py
import json
from .openai_service import OpenAIService
from scout_agent.models import CompanyData, LeadProspect


class LeadScoutAgent:
    def __init__(self):
        self.openai_service = OpenAIService()

    def find_potential_leads(self, company_id):
        """
        주어진 회사 ID를 기반으로 잠재적인 리드를 찾고 저장합니다.
        OpenAI의 웹서치 도구를 활용하여 최신 정보를 기반으로 리드를 생성합니다.
        """
        try:
            print(f"리드 검색 시작: company_id={company_id}")

            # 소스 회사 정보 가져오기
            source_company = CompanyData.objects.get(id=company_id)
            print(f"소스 회사: {source_company.company}")
            print(f"홈페이지 : {source_company.homepage}")

            # OpenAI 서비스를 통해 잠재적인 리드 생성
            leads_data = self.openai_service.generate_potential_leads(source_company)

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

                    # 리드 관계 생성
                    lead_relation, relation_created = LeadProspect.objects.get_or_create(
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
                "leads": created_leads
            }

        except CompanyData.DoesNotExist:
            print(f"회사 ID {company_id}를 찾을 수 없습니다")
            return {"status": "error", "message": "Source company not found"}
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return {"status": "error", "message": str(e)}