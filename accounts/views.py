import base64
from io import BytesIO

import qrcode
import qrcode.image.svg
from django import forms
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django_otp import login as otp_login
from django_otp import match_token
from django_otp.plugins.otp_totp.models import TOTPDevice


class TokenForm(forms.Form):
    token = forms.CharField(
        label="6-digit code from your authenticator app",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={"autocomplete": "one-time-code", "inputmode": "numeric", "pattern": "[0-9]{6}", "autofocus": True}
        ),
    )


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def _qr_data_uri(text):
    img = qrcode.make(text, image_factory=qrcode.image.svg.SvgPathImage, box_size=12, border=2)
    buffer = BytesIO()
    img.save(buffer)
    return "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue()).decode()


@login_required
def two_factor_setup(request):
    """First login: enrol an authenticator app (Google Authenticator, Microsoft Authenticator, 1Password, ...)."""
    if request.user.totpdevice_set.filter(confirmed=True).exists():
        return redirect("accounts:two_factor_verify")

    device, _ = TOTPDevice.objects.get_or_create(user=request.user, confirmed=False, defaults={"name": "Authenticator app"})
    form = TokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if device.verify_token(form.cleaned_data["token"]):
            device.confirmed = True
            device.save()
            otp_login(request, device)
            messages.success(request, "Two-factor authentication is set up. Keep your phone safe.")
            return redirect("compliance:dashboard")
        form.add_error("token", "That code didn't match. Check the time on your phone and try the newest code.")

    secret = base64.b32encode(device.bin_key).decode().rstrip("=")
    return render(
        request,
        "accounts/two_factor_setup.html",
        {"form": form, "qr": _qr_data_uri(device.config_url), "secret": secret},
    )


@login_required
def two_factor_verify(request):
    if request.user.is_verified():
        return redirect("compliance:dashboard")
    form = TokenForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        device = match_token(request.user, form.cleaned_data["token"])
        if device is not None:
            otp_login(request, device)
            return redirect(request.GET.get("next") or "compliance:dashboard")
        form.add_error("token", "Invalid or expired code.")
    return render(request, "accounts/two_factor_verify.html", {"form": form})
