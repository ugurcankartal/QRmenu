from django.http import JsonResponse

from security.services.sql_injection import (
    find_sql_injection_match,
    record_sql_injection_attempt,
    should_scan_request,
)


class SqlInjectionDetectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if should_scan_request(request):
            match = find_sql_injection_match(request)
            if match:
                pattern_name, matched_value, source = match
                record_sql_injection_attempt(
                    request,
                    matched_pattern=pattern_name,
                    matched_value=matched_value,
                    source=source,
                )
                return JsonResponse(
                    {"detail": "Geçersiz istek."},
                    status=400,
                )

        return self.get_response(request)
