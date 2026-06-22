from django.db.models import Prefetch, Q
from django.utils import timezone

from rest_framework import generics, viewsets

from .models import (
    Campaign,
    Category,
    ChefRecommendation,
    Product,
    SiteSettings,
)
from .pagination import FlexiblePageNumberPagination
from .querysets import (
    public_chef_recommendation_product_links_queryset,
    public_products_queryset,
)
from .serializers import (
    CampaignSerializer,
    CategorySerializer,
    ChefRecommendationSerializer,
    ProductSerializer,
    SiteSettingsSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(
            status=Category.Status.ACTIVE,
        ).prefetch_related(
            "translations__language",
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language_code"] = self.request.query_params.get("lang")
        return context


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = FlexiblePageNumberPagination

    def get_queryset(self):
        queryset = public_products_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            try:
                category = Category.objects.get(
                    pk=int(category_id),
                    status=Category.Status.ACTIVE,
                )
            except (Category.DoesNotExist, TypeError, ValueError):
                return queryset.none()
            category_ids = (
                category.get_descendants(include_self=True)
                .filter(status=Category.Status.ACTIVE)
                .values_list("pk", flat=True)
            )
            queryset = queryset.filter(category_id__in=category_ids)

        is_available = self.request.query_params.get("available")
        if is_available in ("true", "1"):
            queryset = queryset.filter(is_available=True)

        search = self.request.query_params.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(translations__name__icontains=search)
                | Q(translations__description__icontains=search)
            ).distinct()

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language_code"] = self.request.query_params.get("lang")
        return context


class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CampaignSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Campaign.objects.prefetch_related(
            Prefetch("products", queryset=public_products_queryset()),
            "rules",
            "translations__language",
        ).all()
        is_active = self.request.query_params.get("active")
        if is_active in ("true", "1"):
            queryset = queryset.filter(is_active=True)
            now = timezone.now()
            queryset = queryset.filter(
                Q(starts_at__isnull=True) | Q(starts_at__lte=now),
                Q(ends_at__isnull=True) | Q(ends_at__gte=now),
            )
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language_code"] = self.request.query_params.get("lang")
        return context


class ChefRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChefRecommendationSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return ChefRecommendation.objects.filter(
            status=ChefRecommendation.Status.ACTIVE,
        ).prefetch_related(
            Prefetch(
                "product_links",
                queryset=public_chef_recommendation_product_links_queryset(),
            ),
            "translations__language",
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language_code"] = self.request.query_params.get("lang")
        return context


class SiteSettingsView(generics.RetrieveAPIView):
    serializer_class = SiteSettingsSerializer

    def get_object(self):
        return (
            SiteSettings.objects.filter(is_active=True)
            .prefetch_related(
                "translations__language",
                "contacts",
                "highlights__translations__language",
            )
            .order_by("-updated_at")
            .first()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language_code"] = self.request.query_params.get("lang")
        return context
