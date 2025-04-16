from ..models import CompanyData

def get_company_data_by_id(company_id):
    return CompanyData.objects.get(id=company_id)

def create_or_update_company_data(company_name, defaults):
    return CompanyData.objects.update_or_create(company=company_name, defaults=defaults)