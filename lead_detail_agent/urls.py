from django.urls import path
from .views import LeadDataView

urlpatterns = [
    path('details/', LeadDataView.as_view(), name='get_lead_detail_data'),
]