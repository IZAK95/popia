from urllib.parse import urlencode

from django.shortcuts import redirect
from django.urls import reverse

# Paths a password-authenticated (but not yet 2FA-verified) user may reach.
ALLOWED_URL_NAMES = ("accounts:two_factor_setup", "accounts:two_factor_verify", "accounts:logout")


class RequireTwoFactorMiddleware:
    """Every signed-in user must pass a TOTP check before seeing any page."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and not user.is_verified():
            allowed = {reverse(name) for name in ALLOWED_URL_NAMES}
            if request.path not in allowed and not request.path.startswith("/static/"):
                name = "accounts:two_factor_verify" if user.totpdevice_set.filter(confirmed=True).exists() else "accounts:two_factor_setup"
                url = reverse(name)
                # Remember the page the user was heading to, so they land there after the code check.
                if request.method == "GET" and request.path != "/":
                    url += "?" + urlencode({"next": request.get_full_path()})
                return redirect(url)
        return self.get_response(request)
