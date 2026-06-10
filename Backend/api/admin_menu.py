import json
import os

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .admin_branding import get_admin_site_name, get_admin_user_display
from .models import AdminAppMenuOrder, AdminModelMenuOrder
from .services.frontend_access import get_active_site_settings


def get_registered_app_labels():
    labels = set()
    for model in admin.site._registry:
        labels.add(model._meta.app_label)
    return labels


def get_registered_model_names(app_label):
    names = set()
    for model in admin.site._registry:
        if model._meta.app_label == app_label:
            names.add(model._meta.object_name)
    return names


def sort_app_list(app_list, user):
    if not user.is_authenticated:
        return app_list

    for app in app_list:
        order_map = dict(
            AdminModelMenuOrder.objects.filter(
                user=user,
                app_label=app["app_label"],
            ).values_list("model_name", "order")
        )
        if order_map:
            app["models"].sort(
                key=lambda model: (
                    order_map.get(model["object_name"], 10_000),
                    model["name"],
                )
            )

    app_order_map = dict(
        AdminAppMenuOrder.objects.filter(user=user).values_list("app_label", "order")
    )
    if app_order_map:
        app_list.sort(
            key=lambda app: (app_order_map.get(app["app_label"], 10_000), app["name"].lower())
        )

    return app_list


@require_POST
def save_model_menu_order(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz istek."}, status=400)

    app_label = payload.get("app_label")
    model_names = payload.get("model_names")

    if not isinstance(app_label, str) or not app_label:
        return JsonResponse({"error": "Uygulama gerekli."}, status=400)
    if not isinstance(model_names, list) or not model_names:
        return JsonResponse({"error": "Model listesi gerekli."}, status=400)

    valid_names = get_registered_model_names(app_label)
    if not valid_names:
        return JsonResponse({"error": "Geçersiz uygulama."}, status=400)

    ordered_names = []
    for model_name in model_names:
        if isinstance(model_name, str) and model_name in valid_names:
            if model_name not in ordered_names:
                ordered_names.append(model_name)

    if not ordered_names:
        return JsonResponse({"error": "Geçersiz model listesi."}, status=400)

    for index, model_name in enumerate(ordered_names):
        AdminModelMenuOrder.objects.update_or_create(
            user=request.user,
            app_label=app_label,
            model_name=model_name,
            defaults={"order": index},
        )

    AdminModelMenuOrder.objects.filter(
        user=request.user,
        app_label=app_label,
    ).exclude(model_name__in=ordered_names).delete()

    return JsonResponse({"ok": True})


@require_POST
def save_app_menu_order(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz istek."}, status=400)

    app_labels = payload.get("app_labels")
    if not isinstance(app_labels, list) or not app_labels:
        return JsonResponse({"error": "Uygulama listesi gerekli."}, status=400)

    valid_labels = get_registered_app_labels()
    ordered_labels = []
    for app_label in app_labels:
        if isinstance(app_label, str) and app_label in valid_labels:
            if app_label not in ordered_labels:
                ordered_labels.append(app_label)

    if not ordered_labels:
        return JsonResponse({"error": "Geçersiz uygulama listesi."}, status=400)

    for index, app_label in enumerate(ordered_labels):
        AdminAppMenuOrder.objects.update_or_create(
            user=request.user,
            app_label=app_label,
            defaults={"order": index},
        )

    AdminAppMenuOrder.objects.filter(user=request.user).exclude(
        app_label__in=ordered_labels
    ).delete()

    return JsonResponse({"ok": True})


@require_POST
def toggle_frontend_access(request):
    if not request.user.is_staff:
        raise PermissionDenied

    settings = get_active_site_settings()
    if settings is None:
        messages.error(request, "Aktif site ayarı bulunamadı.")
        return redirect("admin:index")

    settings.frontend_public_access = not settings.frontend_public_access
    settings.save(update_fields=["frontend_public_access", "updated_at"])

    if settings.frontend_public_access:
        messages.success(request, "Ön yüz erişimi açıldı.")
    else:
        messages.success(
            request,
            "Ön yüz erişimi kapatıldı. Yalnızca admin/supervisor kullanıcıları giriş yapabilir.",
        )
    next_url = request.META.get("HTTP_REFERER")
    if next_url and next_url.startswith(request.build_absolute_uri("/admin")):
        return redirect(next_url)
    return redirect("admin:index")


def patch_admin_site():
    site = admin.site
    if getattr(site, "_model_menu_order_patched", False):
        return
    site._model_menu_order_patched = True

    original_get_app_list = site.get_app_list
    original_get_urls = site.get_urls
    original_each_context = site.each_context

    def each_context(request):
        context = original_each_context(request)
        site_name = get_admin_site_name()
        context["site_header"] = site_name
        context["site_title"] = site_name
        context["admin_user_display"] = get_admin_user_display(request.user)
        settings = get_active_site_settings()
        context["frontend_public_access"] = (
            settings.frontend_public_access if settings else True
        )
        context["frontend_url"] = os.getenv(
            "FRONTEND_URL",
            "http://localhost:25489",
        )
        return context

    def get_app_list(request, app_label=None):
        app_list = original_get_app_list(request, app_label)
        return sort_app_list(app_list, request.user)

    def get_urls():
        from django.urls import path

        custom_urls = [
            path(
                "save-model-menu-order/",
                site.admin_view(save_model_menu_order),
                name="save_model_menu_order",
            ),
            path(
                "save-app-menu-order/",
                site.admin_view(save_app_menu_order),
                name="save_app_menu_order",
            ),
            path(
                "toggle-frontend-access/",
                site.admin_view(toggle_frontend_access),
                name="toggle_frontend_access",
            ),
        ]
        return custom_urls + original_get_urls()

    site.get_app_list = get_app_list
    site.get_urls = get_urls
    site.each_context = each_context
