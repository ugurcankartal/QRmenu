from django.db.models import Prefetch, Q
from django.utils import timezone

from rest_framework import generics, viewsets

from .models import (
    Campaign,
    Category,
    ChefRecommendation,
    ChefRecommendationProduct,
    Product,
    SiteSettings,
)
from .pagination import FlexiblePageNumberPagination
from .serializers import (
    CampaignSerializer,
    CategorySerializer,
    ChefRecommendationSerializer,
    ProductSerializer,
    SiteSettingsSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related(
        "translations__language",
    ).all()
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["language_code"] = self.request.query_params.get("lang")
        return context


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related(
        "category",
        "product_currency__currency",
    ).prefetch_related(
        "translations__language",
    ).all()
    serializer_class = ProductSerializer
    pagination_class = FlexiblePageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category")
        if category_id:
            try:
                category = Category.objects.get(pk=int(category_id))
            except (Category.DoesNotExist, TypeError, ValueError):
                return queryset.none()
            category_ids = category.get_descendants(include_self=True).values_list(
                "pk",
                flat=True,
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
        product_qs = Product.objects.select_related(
            "category",
            "product_currency__currency",
        ).prefetch_related(
            "translations__language",
            "category__translations__language",
        )
        queryset = Campaign.objects.prefetch_related(
            Prefetch("products", queryset=product_qs),
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
        product_qs = Product.objects.select_related(
            "category",
            "product_currency__currency",
        ).prefetch_related(
            "translations__language",
            "category__translations__language",
        )
        return ChefRecommendation.objects.filter(
            status=ChefRecommendation.Status.ACTIVE,
        ).prefetch_related(
            Prefetch(
                "product_links",
                queryset=ChefRecommendationProduct.objects.select_related(
                    "product__category",
                    "product__product_currency__currency",
                ).prefetch_related(
                    "product__translations__language",
                    "product__category__translations__language",
                ).order_by("order", "pk"),
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
