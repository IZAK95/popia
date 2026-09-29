from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def ph(value, label):
    """Show a highlighted [placeholder] when a company profile value is still empty."""
    if value in (None, ""):
        return format_html('<mark class="ph">[{}]</mark>', label)
    return value


@register.filter
def filesize(num):
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.0f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


@register.simple_tag
def status_class(status):
    return {"done": "ok", "progress": "info", "todo": "", "na": "muted"}.get(status, "")
