from ..models import CompanyProfile

def get_company_profile_by_company(company):
    return CompanyProfile.objects.filter(company=company)