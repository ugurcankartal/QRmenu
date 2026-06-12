from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from security.models import SitePageVisit
from security.services.visit_audit import log_site_page_visit, normalize_page_path


class PageVisitLogView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return self._log_visit(request)

    def post(self, request):
        return self._log_visit(request)

    def _log_visit(self, request):
        page_path = request.query_params.get("path") or request.data.get("path", "")
        if not page_path:
            return Response(
                {"detail": "path gerekli."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        referer = request.query_params.get("referrer") or request.data.get("referrer", "")
        search = request.query_params.get("search") or request.data.get("search", "")
        visit = log_site_page_visit(
            request,
            page_path=normalize_page_path(page_path),
            visit_source=SitePageVisit.VisitSource.FRONTEND_ROUTE,
            referer=referer,
            query_string=search,
        )
        if visit is None:
            return Response({"logged": False})
        return Response({"logged": True, "id": visit.pk})
