from django.contrib import admin

from currency.models import Currency, CurrencyExchangeRate, ProductCurrency


class CurrencyExchangeRateFromInline(admin.TabularInline):
    model = CurrencyExchangeRate
    fk_name = "from_currency"
    fields = ("to_currency", "buy_rate", "sell_rate", "is_active")
    extra = 1
    verbose_name = "Diğer Para Birimleri (Kaynak→Hedef)"
    verbose_name_plural = "Diğer Para Birimleri (Kaynak→Hedef)"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "to_currency" and request.resolver_match:
            obj_id = request.resolver_match.kwargs.get("object_id")
            if obj_id:
                field.queryset = Currency.objects.exclude(pk=obj_id)
        return field


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "symbol", "is_active", "order", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["code", "name", "symbol"]
    list_editable = ["is_active", "order"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["order", "code"]
    inlines = [CurrencyExchangeRateFromInline]
    fieldsets = (
        (
            "Para Birimi Bilgileri",
            {"fields": ("code", "name", "symbol")},
        ),
        (
            "Durum",
            {"fields": ("is_active", "order")},
        ),
        (
            "Tarih Bilgileri",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ProductCurrency)
class ProductCurrencyAdmin(admin.ModelAdmin):
    list_display = ["product", "currency", "created_at"]
    list_filter = ["currency", "created_at"]
    search_fields = [
        "product__slug",
        "product__translations__name",
        "currency__code",
        "currency__name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    fieldsets = (
        (
            "Ürün ve Para Birimi",
            {
                "fields": ("product", "currency"),
                "description": "Her ürün için yalnızca bir para birimi seçilebilir.",
            },
        ),
        (
            "Tarih Bilgileri",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
