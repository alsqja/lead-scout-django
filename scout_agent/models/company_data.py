from django.db import models

class CompanyData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, null=True, blank=True)
    sales = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_funding = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    key_executive = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name_plural = "Company Data"