from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from adisyon.models import Adisyon, AdisyonItem
from adisyon.querysets import active_adisyon_items_queryset
from adisyon.services import (
    AdisyonSessionLimitError,
    assert_can_add_to_adisyon,
    ensure_adisyon,
    resolve_session,
)
from api.models import Product
from api.querysets import public_products_queryset

from .serializers import AdisyonItemSerializer, AdisyonSerializer

SESSION_HEADER = "X-Session-Key"


def _language_code(request):
    return request.query_params.get("lang") or request.headers.get("Accept-Language", "tr")


def _session_key_from_request(request) -> str | None:
    return request.headers.get(SESSION_HEADER) or request.COOKIES.get("adisyon_session")


def _attach_session_header(response: Response, session_key: str) -> Response:
    response[SESSION_HEADER] = session_key
    return response


def _serialize_adisyon(adisyon: Adisyon, request) -> dict:
    serializer = AdisyonSerializer(
        adisyon,
        context={"request": request, "language_code": _language_code(request)},
    )
    return serializer.data


def _get_adisyon_queryset():
    active_items = active_adisyon_items_queryset().select_related(
        "product__category",
        "product__product_currency__currency",
        "currency",
        "campaign_rule__campaign",
    ).prefetch_related(
        "product__translations",
        "product__category__translations",
        "campaign_rule__campaign__translations__language",
    )
    return Adisyon.objects.select_related("session_key", "currency").prefetch_related(
        Prefetch("items", queryset=active_items),
    )


class AdisyonView(APIView):
    """Mevcut adisyonu getirir; oturum yoksa oluşturur."""

    def get(self, request):
        session_key, created = resolve_session(_session_key_from_request(request))
        adisyon = _get_adisyon_queryset().get(pk=ensure_adisyon(session_key).pk)
        response = Response(_serialize_adisyon(adisyon, request))
        if created:
            _attach_session_header(response, session_key.key)
        return response


class AdisyonToggleProductView(APIView):
    """Ürünü adisyona ekler veya çıkarır."""

    def post(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"detail": "product_id gerekli."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            public_products_queryset().filter(is_available=True),
            pk=product_id,
        )
        session_key, created = resolve_session(_session_key_from_request(request))
        adisyon = ensure_adisyon(session_key)

        item = AdisyonItem.objects.filter(adisyon=adisyon, product=product).first()
        if item:
            item.delete()
            added = False
        else:
            try:
                assert_can_add_to_adisyon(session_key)
            except AdisyonSessionLimitError as exc:
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            AdisyonItem.objects.create(
                adisyon=adisyon,
                product=product,
                quantity=1,
            )
            added = True

        adisyon = _get_adisyon_queryset().get(pk=adisyon.pk)
        data = _serialize_adisyon(adisyon, request)
        data["added"] = added
        response = Response(data)
        if created:
            _attach_session_header(response, session_key.key)
        return response


class AdisyonItemDetailView(APIView):
    """Adisyon kalemi adet güncelleme veya silme."""

    def patch(self, request, item_id):
        quantity = request.data.get("quantity")
        if quantity is None:
            return Response(
                {"detail": "quantity gerekli."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {"detail": "quantity geçerli bir sayı olmalı."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity < 1:
            return Response(
                {"detail": "quantity en az 1 olmalı."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_key, created = resolve_session(_session_key_from_request(request))
        item = get_object_or_404(
            active_adisyon_items_queryset(),
            pk=item_id,
            adisyon__session_key=session_key,
        )
        item.quantity = quantity
        item.save()

        adisyon = _get_adisyon_queryset().get(pk=ensure_adisyon(session_key).pk)
        response = Response(_serialize_adisyon(adisyon, request))
        if created:
            _attach_session_header(response, session_key.key)
        return response

    def delete(self, request, item_id):
        session_key, created = resolve_session(_session_key_from_request(request))
        item = get_object_or_404(
            active_adisyon_items_queryset(),
            pk=item_id,
            adisyon__session_key=session_key,
        )
        item.delete()

        adisyon = _get_adisyon_queryset().get(pk=ensure_adisyon(session_key).pk)
        response = Response(_serialize_adisyon(adisyon, request))
        if created:
            _attach_session_header(response, session_key.key)
        return response
