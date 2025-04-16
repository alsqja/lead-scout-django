from django.db import models

from scout_agent.models import CompanyData

class CompanyProfile(models.Model):
    company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name='profiles')
    file_name = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.company} - {self.file_name}"

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"