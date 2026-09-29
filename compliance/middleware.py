import threading

_local = threading.local()


def get_current_username():
    user = getattr(_local, "user", None)
    return user.get_username() if user is not None and user.is_authenticated else "system"


class CurrentUserMiddleware:
    """Makes the signed-in user available to the audit-log signal handlers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _local.user = getattr(request, "user", None)
        try:
            return self.get_response(request)
        finally:
            _local.user = None


class SecurityHeadersMiddleware:
    CSP = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Content-Security-Policy", self.CSP)
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        if request.user.is_authenticated if hasattr(request, "user") else False:
            response.setdefault("Cache-Control", "no-store")
        return response
