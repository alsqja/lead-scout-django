# views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CompanyData
from .services.agent_service import LeadScoutAgent

# 로깅 설정
logger = logging.getLogger('scout_agent')


class FindLeadsView(APIView):
    def post(self, request, format=None):
        logger.info("FindLeadsView.post 호출됨")
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