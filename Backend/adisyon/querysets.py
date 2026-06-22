from api.models import Category

from .models import AdisyonItem


def active_adisyon_items_queryset():
    return AdisyonItem.objects.filter(
        product__category__status=Category.Status.ACTIVE,
    )
