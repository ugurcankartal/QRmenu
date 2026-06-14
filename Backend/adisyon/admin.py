from django.contrib import admin

from adisyon.models import Adisyon, AdisyonItem, SessionKey, SessionKeyPolicy
from security.models import SitePageVisit


class SitePageVisitInline(admin.TabularInline):
    model = SitePageVisit
    fk_name = "session_key"
    extra = 0
    can_delete = False
    show_change_link = True
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "page_path",
        "query_string",
        "visit_source",
        "ip_address",
        "location_label",
        "browser_name",
        "device_type",
        "is_mobile",
        "referer",
    )
    fields = readonly_fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class AdisyonSitePageVisitInline(SitePageVisitInline):
    fk_name = "adisyon"
    verbose_name = "Site ziyareti"
    verbose_name_plural = "Site ziyaretleri"


class AdisyonItemInline(admin.TabularInline):
    model = AdisyonItem
    extra = 1
    autocomplete_fields = ["product"]
    readonly_fields = (
        "price",
        "discounted_price",
        "campaign_rule",
        "currency",
        "amount",
        "total_price",
    )
    fields = (
        "product",
        "quantity",
        "price",
        "discounted_price",
        "campaign_rule",
        "currency",
        "amount",
        "total_price",
        "order",
    )


@admin.register(SessionKeyPolicy)
class SessionKeyPolicyAdmin(admin.ModelAdmin):
    list_display = [
        "refresh_duration_minutes",
        "max_concurrent_adisyon_sessions",
        "updated_at",
    ]
    readonly_fields = ["created_at", "updated_at"]
    fields = [
        "refresh_duration_minutes",
        "max_concurrent_adisyon_sessions",
        "created_at",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return not SessionKeyPolicy.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SessionKey)
class SessionKeyAdmin(admin.ModelAdmin):
    list_display = [
        "key_short",
        "refresh_duration_minutes",
        "page_visit_count",
        "last_activity_at",
        "expires_at",
        "created_at",
    ]
    list_filter = ["expires_at", "created_at"]
    search_fields = ["key"]
    readonly_fields = [
        "key",
        "page_visit_count",
        "last_activity_at",
        "expires_at",
        "created_at",
        "updated_at",
    ]
    ordering = ["-last_activity_at"]
    inlines = [SitePageVisitInline]

    @admin.display(description="Anahtar")
    def key_short(self, obj):
        return f"{obj.key[:12]}…"

    @admin.display(description="Site ziyareti")
    def page_visit_count(self, obj):
        return obj.page_visits.count()


@admin.register(Adisyon)
class AdisyonAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "session_key",
        "display_total_price",
        "product_count",
        "item_count",
        "updated_at",
    ]
    search_fields = ["session_key__key", "items__product__slug"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "total_price",
        "discounted_total_price",
        "currency",
    ]
    autocomplete_fields = ["session_key"]
    inlines = [AdisyonItemInline, AdisyonSitePageVisitInline]

    @admin.display(description="Toplam")
    def display_total_price(self, obj):
        if obj.currency:
            if obj.discounted_total_price != obj.total_price:
                return (
                    f"{obj.currency.symbol}{obj.discounted_total_price} "
                    f"(liste: {obj.currency.symbol}{obj.total_price})"
                )
            return f"{obj.currency.symbol}{obj.total_price}"
        return str(obj.discounted_total_price)

    @admin.display(description="Ürün çeşidi")
    def product_count(self, obj):
        return obj.products.count()

    @admin.display(description="Toplam kalem")
    def item_count(self, obj):
        return obj.items.count()


@admin.register(AdisyonItem)
class AdisyonItemAdmin(admin.ModelAdmin):
    list_display = [
        "adisyon",
        "product",
        "quantity",
        "display_unit_price",
        "display_line_total",
        "updated_at",
    ]
    list_filter = ["created_at"]
    search_fields = [
        "adisyon__session_key__key",
        "product__slug",
        "product__translations__name",
    ]
    autocomplete_fields = ["adisyon", "product"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "price",
        "discounted_price",
        "campaign_rule",
        "currency",
        "amount",
        "total_price",
    ]

    @admin.display(description="Birim fiyat")
    def display_unit_price(self, obj):
        if obj.currency:
            return f"{obj.currency.symbol}{obj.price}"
        return str(obj.price)

    @admin.display(description="Satır toplamı")
    def display_line_total(self, obj):
        if obj.currency:
            return f"{obj.currency.symbol}{obj.total_price}"
        return str(obj.total_price)
