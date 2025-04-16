from ..models import PDFAnalysis

def get_pdf_analysis_by_company_and_profile(company, profile):
    return PDFAnalysis.objects.filter(company=company, profile=profile)

def post_pdf_analysis(company, profile, defaults):
    return PDFAnalysis.objects.update_or_create(company=company, profile=profile, defaults=defaults)