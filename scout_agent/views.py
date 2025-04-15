import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import CompanyData, CompanyProfile, PDFAnalysis
from .services.agent_service import LeadScoutAgent
from .services.pdf_service import PDFAnalysisService
from django.shortcuts import get_object_or_404

# 로깅 설정
logger = logging.getLogger('scout_agent')


class LeadScoutView(APIView):
    def post(self, request):
        logger.info("find_potential_leads 호출됨")
        company_id = request.data.get('company_id')

        logger.debug(f"요청 데이터: {request.data}")

        if not company_id:
            logger.error("company_id가 제공되지 않았습니다")
            return Response(
                {"error": "company_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"리드 스카우트 에이전트 초기화: company_id={company_id}")
        agent = LeadScoutAgent()

        logger.info(f"리드 검색 시작: company_id={company_id}")
        result = agent.find_potential_leads(company_id)

        if result["status"] == "error":
            logger.error(f"에이전트 오류 발생: {result['message']}")
            return Response(
                {"error": result["message"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"리드 검색 성공: {len(result.get('leads', []))}개 리드 발견")
        return Response(result, status=status.HTTP_200_OK)


class PDFAnalysisView(APIView):
    def post(self, request, profile_id=None):
        """
        PDF 파일을 분석하고 DB에 저장하는 API 엔드포인트
        """
        try:
            # profile_id가 URL에서 오지 않았다면 body에서 확인
            if profile_id is None:
                profile_id = request.data.get('profile_id')
                if not profile_id:
                    return Response(
                        {"error": "profile_id is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 프로필 확인
            profile = get_object_or_404(CompanyProfile, id=profile_id)

            # PDF 분석 서비스 실행
            pdf_service = PDFAnalysisService()
            analysis = pdf_service.analyze_company_pdf(profile)

            if not analysis:
                return Response(
                    {"error": "Failed to analyze PDF"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "status": "success",
                "message": "PDF analysis completed successfully",
                "analysis": analysis
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, profile_id):
        """
        저장된 PDF 분석을 조회하는 API 엔드포인트
        """
        try:
            # 분석본 조회
            analysis = get_object_or_404(PDFAnalysis, profile_id=profile_id)

            return Response({
                "status": "success",
                "analysis": {
                    "industry": analysis.industry,
                    "sales": analysis.sales,
                    "total_funding": analysis.total_funding,
                    "homepage": analysis.homepage,
                    "key_executive": analysis.key_executive,
                    "address": analysis.address,
                    "email": analysis.email,
                    "phone_number": analysis.phone_number,
                    "company_description": analysis.company_description,
                    "products_services": analysis.products_services,
                    "target_customers": analysis.target_customers,
                    "competitors": analysis.competitors,
                    "strengths": analysis.strengths,
                    "business_model": analysis.business_model,
                    "created_at": analysis.created_at,
                    "updated_at": analysis.updated_at
                },
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        