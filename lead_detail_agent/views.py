from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.lead_details_service import LeadDetailsService


class LeadDataView(APIView):
    def post(self, request):
        """
        회사 이름을 받아 해당 회사의 상세 정보를 반환합니다.
        """
        search_company_name = request.data.get('search_company_name')
        company_id = request.data.get('company_id')

        if not search_company_name:
            return Response(
                {"error": "company_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 여기서 비즈니스 로직을 통해 회사 정보를 가져옵니다
        result = LeadDetailsService().extract_info(search_company_name)

        # HTML 템플릿 렌더링
        html_content = render_to_string('lead_data_template.html', result)

        # HTML 콘텐츠 직접 반환
        return HttpResponse(html_content, content_type='text/html')
