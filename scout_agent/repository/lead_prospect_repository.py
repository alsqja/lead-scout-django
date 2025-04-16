from ..models import LeadProspect

def create_or_update_prospect_data(company, prospect, defaults):
    return LeadProspect.objects.update_or_create(
        source_company=company,
        prospect_company=prospect,
        defaults=defaults
    )