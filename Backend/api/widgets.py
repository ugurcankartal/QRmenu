import json

from django import forms
from django.utils.html import format_html


def normalize_tag_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [
            part.strip()
            for part in stripped.replace("\n", ",").replace(";", ",").split(",")
            if part.strip()
        ]
    return [str(value).strip()] if str(value).strip() else []


class TagListWidget(forms.Widget):
    template_name = None

    class Media:
        css = {"all": ("admin/api/tag_list_input.css",)}
        js = ("admin/api/tag_list_input.js",)

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(attrs, extra_attrs={"name": name})
        widget_id = final_attrs.get("id", name)
        tags = normalize_tag_list(value)
        json_value = json.dumps(tags, ensure_ascii=False)
        placeholder = final_attrs.pop("placeholder", "Yazıp dışarı tıklayın veya Enter'a basın")

        return format_html(
            '<div class="tag-list-widget" data-input-id="{}">'
            '<div class="tag-list-chips" aria-live="polite"></div>'
            '<input type="text" class="tag-list-entry" placeholder="{}" autocomplete="off" />'
            '<input type="hidden" name="{}" id="{}" value="{}" />'
            "</div>",
            widget_id,
            placeholder,
            name,
            widget_id,
            json_value,
        )


class TagListFormField(forms.JSONField):
    widget = TagListWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        return normalize_tag_list(value)

    def bound_data(self, data, initial):
        if data is None:
            return normalize_tag_list(initial)
        if isinstance(data, str):
            return normalize_tag_list(data)
        return normalize_tag_list(data)

    def to_python(self, value):
        if value in self.empty_values:
            return []
        if isinstance(value, str):
            if not value.strip():
                return []
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise forms.ValidationError("Geçersiz etiket listesi.") from exc
        if not isinstance(value, list):
            raise forms.ValidationError("Etiket listesi bir dizi olmalıdır.")
        return normalize_tag_list(value)
