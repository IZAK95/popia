"""
Generic list / detail / create / edit / delete pages for the compliance registers.

Each register is described declaratively by a Register instance; the views and
templates are shared so every register behaves the same way.
"""

from dataclasses import dataclass, field

from django import forms
from django.contrib import messages
from django.db import models
from django.forms import modelform_factory
from django.urls import path, reverse, reverse_lazy
from django.views import generic


def formfield_callback(db_field, **kwargs):
    if isinstance(db_field, models.DateTimeField):
        kwargs["widget"] = forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
    elif isinstance(db_field, models.DateField):
        kwargs["widget"] = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")
    elif isinstance(db_field, models.TextField):
        kwargs["widget"] = forms.Textarea(attrs={"rows": 3})
    elif isinstance(db_field, models.ManyToManyField):
        kwargs["widget"] = forms.CheckboxSelectMultiple
    return db_field.formfield(**kwargs)


@dataclass
class Column:
    label: str
    attr: str
    badge: dict = field(default_factory=dict)  # value -> css class

    def cell(self, obj):
        raw = getattr(obj, self.attr)
        display = getattr(obj, f"get_{self.attr}_display", None)
        value = display() if display else raw
        if isinstance(value, bool):
            return {"text": "Yes" if value else "No", "badge": "ok" if value else "warn"}
        if isinstance(value, (list, tuple)):
            return {"text": "; ".join(value) if value else "None", "badge": "warn" if value else "ok"}
        badge = self.badge.get(raw, "") if isinstance(raw, (str, int)) else ""
        return {"text": value if value not in (None, "") else "—", "badge": badge}


@dataclass
class Register:
    slug: str
    prefix: str
    model: type
    title: str
    singular: str
    intro: str
    fields: list
    columns: list
    help_page: str = ""
    detail_template: str = "compliance/register_detail.html"
    list_template: str = "compliance/register_list.html"
    list_context: object = None  # optional callable(queryset) -> dict
    create_initial: dict = field(default_factory=dict)

    @property
    def form_class(self):
        return modelform_factory(self.model, fields=self.fields, formfield_callback=formfield_callback)

    def url(self, action):
        return f"compliance:{self.slug}_{action}"

    def urlpatterns(self):
        base = self.prefix
        return [
            path(base, RegisterList.as_view(register=self), name=f"{self.slug}_list"),
            path(f"{base}new/", RegisterCreate.as_view(register=self), name=f"{self.slug}_create"),
            path(f"{base}<int:pk>/", RegisterDetail.as_view(register=self), name=f"{self.slug}_detail"),
            path(f"{base}<int:pk>/edit/", RegisterUpdate.as_view(register=self), name=f"{self.slug}_update"),
            path(f"{base}<int:pk>/delete/", RegisterDelete.as_view(register=self), name=f"{self.slug}_delete"),
        ]


class RegisterMixin:
    register = None

    def get_queryset(self):
        return self.register.model.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["register"] = self.register
        ctx["urls"] = {a: self.register.url(a) for a in ("list", "create", "detail", "update", "delete")}
        return ctx


class RegisterList(RegisterMixin, generic.ListView):
    def get_template_names(self):
        return [self.register.list_template]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["rows"] = [(obj, [(col.cell(obj), col) for col in self.register.columns]) for obj in ctx["object_list"]]
        ctx["drafts"] = sum(1 for obj in ctx["object_list"] if getattr(obj, "is_draft", False))
        if self.register.list_context:
            ctx.update(self.register.list_context(ctx["object_list"]))
        return ctx


class RegisterDetail(RegisterMixin, generic.DetailView):
    def get_template_names(self):
        return [self.register.detail_template]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        rows = []
        for name in self.register.fields:
            f = obj._meta.get_field(name)
            if isinstance(f, models.ManyToManyField):
                value = ", ".join(str(o) for o in getattr(obj, name).all()) or "—"
            elif f.choices:
                value = getattr(obj, f"get_{name}_display")() or "—"
            else:
                value = getattr(obj, name)
                if isinstance(value, bool):
                    value = "Yes" if value else "No"
                elif value in (None, ""):
                    value = "—"
            rows.append((f.verbose_name[:1].upper() + f.verbose_name[1:], value))
        ctx["rows"] = rows
        return ctx


class RegisterFormMixin(RegisterMixin):
    template_name = "compliance/register_form.html"

    def get_form_class(self):
        return self.register.form_class

    def get_success_url(self):
        return reverse(self.register.url("detail"), args=[self.object.pk])


class RegisterCreate(RegisterFormMixin, generic.CreateView):
    def get_initial(self):
        return {**self.register.create_initial, **self.request.GET.dict()}

    def form_valid(self, form):
        messages.success(self.request, f"{self.register.singular.capitalize()} added.")
        return super().form_valid(form)


class RegisterUpdate(RegisterFormMixin, generic.UpdateView):
    def form_valid(self, form):
        messages.success(self.request, "Changes saved.")
        return super().form_valid(form)


class RegisterDelete(RegisterMixin, generic.DeleteView):
    template_name = "compliance/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(self.register.url("list"))

    def form_valid(self, form):
        messages.success(self.request, f"{self.register.singular.capitalize()} deleted.")
        return super().form_valid(form)
