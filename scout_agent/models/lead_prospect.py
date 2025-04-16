from django.db import models

from scout_agent.models import CompanyData


class LeadProspect(models.Model):
    source_company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name='discovered_leads')
    prospect_company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name='source_leads')
    relevance_score = models.FloatField(default=0.0)
    reasoning = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_company.company} → {self.prospect_company.company}"