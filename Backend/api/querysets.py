from api.models import Category, ChefRecommendationProduct, Product


def public_products_queryset():
    return (
        Product.objects.filter(category__status=Category.Status.ACTIVE)
        .select_related(
            "category",
            "product_currency__currency",
        )
        .prefetch_related(
            "translations__language",
            "category__translations__language",
        )
    )


def public_chef_recommendation_product_links_queryset():
    return (
        ChefRecommendationProduct.objects.filter(
            product__category__status=Category.Status.ACTIVE,
        )
        .select_related(
            "product__category",
            "product__product_currency__currency",
        )
        .prefetch_related(
            "product__translations__language",
            "product__category__translations__language",
        )
        .order_by("order", "pk")
    )
