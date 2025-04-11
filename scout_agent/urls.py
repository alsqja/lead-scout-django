from django.urls import path
from .views import FindLeadsView

urlpatterns = [
    path('find-leads/', FindLeadsView.as_view(), name='find-leads'),
]
