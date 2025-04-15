from django.urls import path
from .views import LeadScoutView, PDFAnalysisView

urlpatterns = [
    path('find-leads/', LeadScoutView.as_view(), name='find_potential_leads'),
    path('analyze-pdf/', PDFAnalysisView.as_view(), name='analyze_pdf'),
    path('analyze-pdf/<int:profile_id>/', PDFAnalysisView.as_view(), name='pdf_analysis_detail'),
]