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

class LeadProspect(models.Model):
    source_company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name='discovered_leads')
    prospect_company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name='source_leads')
    relevance_score = models.FloatField(default=0.0)
    reasoning = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_company.company} → {self.prospect_company.company}"

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

class PDFAnalysis(models.Model):
    company = models.ForeignKey(CompanyData, on_delete=models.CASCADE, related_name='pdf_analyses')
    profile = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='analyses')
    
    # 기본 회사 정보
    industry = models.CharField(max_length=255, null=True, blank=True)
    sales = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    total_funding = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    key_executive = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    
    # 상세 정보
    company_description = models.TextField(null=True, blank=True)
    products_services = models.TextField(null=True, blank=True)
    target_customers = models.TextField(null=True, blank=True)
    competitors = models.TextField(null=True, blank=True)
    strengths = models.TextField(null=True, blank=True)
    business_model = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'profile')
        verbose_name = 'PDF 분석'
        verbose_name_plural = 'PDF 분석들'

    def __str__(self):
        return f"{self.company.company} - {self.profile.url}"