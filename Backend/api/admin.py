from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin

from .forms import (
    CampaignTranslationForm,
    CategoryAdminForm,
    ChefRecommendationTranslationForm,
    ContactInlineForm,
    get_default_language,
    ImageGaleriAdminForm,
    ProductAdminForm,
    ProductTranslationForm,
    SiteSettingsTranslationForm,
)
from .models import (
    Campaign,
    CampaignRule,
    CampaignTranslation,
    Category,
    CategoryTranslation,
    ChefRecommendation,
    ChefRecommendationProduct,
    ChefRecommendationTranslation,
    Contact,
    ContactTranslation,
    ImageGaleri,
    Product,
    ProductTranslation,
    SiteSettings,
    SiteSettingsTranslation,
    SiteHighlight,
    SiteHighlightTranslation,
)
from currency.models import ProductCurrency
from localization.admin_mixins import GroqTranslateAdminMixin


def _render_admin_image(image_field, size):
    if image_field:
        return format_html(
            '<img src="{}" alt="" style="height:{}px;width:auto;max-width:100%;object-fit:contain;" />',
            image_field.url,
            size,
        )
    return "—"


class CategoryTranslationInline(admin.StackedInline):
    model = CategoryTranslation
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    fields = ("language", "name", "title", "description")

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class CategoryImageGaleriInline(admin.StackedInline):
    model = ImageGaleri
    fk_name = "category"
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 1
    fields = ("image", "image_preview", "alt_text", "order", "is_active")
    readonly_fields = ("image_preview",)
    ordering = ("order", "pk")
    verbose_name = "Galeri görseli"
    verbose_name_plural = "Kategori galerisi"

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}

    @admin.display(description="Önizleme")
    def image_preview(self, obj):
        return _render_admin_image(obj.image, size=120)


class ImageGaleriOwnerFilter(admin.SimpleListFilter):
    title = "Tür"
    parameter_name = "owner"

    def lookups(self, request, model_admin):
        return (
            ("product", "Ürün"),
            ("category", "Kategori"),
        )

    def queryset(self, request, queryset):
        if self.value() == "product":
            return queryset.filter(product__isnull=False)
        if self.value() == "category":
            return queryset.filter(category__isnull=False)
        return queryset


@admin.register(ImageGaleri)
class ImageGaleriAdmin(admin.ModelAdmin):
    form = ImageGaleriAdminForm
    list_display = (
        "image_preview",
        "owner_type",
        "linked_target",
        "alt_text",
        "order",
        "is_active",
    )
    list_filter = (ImageGaleriOwnerFilter, "is_active")
    list_editable = ("order", "is_active")
    list_select_related = ("product", "category")
    readonly_fields = ("image_preview_detail",)
    search_fields = ("alt_text", "category__slug", "product__slug")
    ordering = ("order", "pk")
    autocomplete_fields = ("category", "product")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "product",
                    "image",
                    "image_preview_detail",
                    "alt_text",
                    "order",
                    "is_active",
                ),
            },
        ),
    )

    @admin.display(description="Tür")
    def owner_type(self, obj):
        if obj.product_id:
            return "Ürün"
        if obj.category_id:
            return "Kategori"
        return "—"

    @admin.display(description="Bağlı kayıt")
    def linked_target(self, obj):
        if obj.category_id:
            return obj.category
        if obj.product_id:
            return obj.product
        return "—"

    @admin.display(description="Görsel")
    def image_preview(self, obj):
        return _render_admin_image(obj.image, size=48)

    @admin.display(description="Görsel önizleme")
    def image_preview_detail(self, obj):
        return _render_admin_image(obj.image, size=120)


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    form = CategoryAdminForm
    inlines = [CategoryTranslationInline, CategoryImageGaleriInline]
    readonly_fields = ("image_preview_detail",)
    fieldsets = (
        (
            None,
            {
                "fields": ("status", "slug", "parent", "image", "image_preview_detail"),
            },
        ),
    )
    list_display = (
        "tree_actions",
        "image_preview",
        "indented_title",
        "slug",
        "status",
        "order",
    )
    list_editable = ("status",)
    list_filter = ("status",)
    list_display_links = ("indented_title",)
    search_fields = (
        "slug",
        "translations__name",
        "translations__title",
        "translations__description",
    )
    mptt_level_indent = 24
    expand_tree_by_default = True

    @admin.display(description="Görsel")
    def image_preview(self, obj):
        return self._render_image_preview(obj, size=48)

    @admin.display(description="Görsel önizleme")
    def image_preview_detail(self, obj):
        return self._render_image_preview(obj, size=120)

    def _render_image_preview(self, obj, size):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="height:{}px;width:{}px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
                size,
                size,
            )
        return "—"

    def _move_node(self, request):
        cut_item_id = request.POST.get("cut_item")
        old_parent_id = None
        if cut_item_id:
            old_parent_id = (
                self.get_queryset(request)
                .filter(pk=cut_item_id)
                .values_list("parent_id", flat=True)
                .first()
            )

        response = super()._move_node(request)
        if not response.content.startswith(b"OK") or not cut_item_id:
            return response

        cut_item = self.get_queryset(request).filter(pk=cut_item_id).first()
        if not cut_item:
            return response

        Category.sync_sibling_orders(cut_item.parent_id)
        if old_parent_id is not None and old_parent_id != cut_item.parent_id:
            Category.sync_sibling_orders(old_parent_id)
        return response


@admin.register(CategoryTranslation)
class CategoryTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "category"
    list_display = ("category", "language", "name", "title")
    list_filter = ("language",)
    search_fields = ("name", "title", "description", "category__slug")


class ProductTranslationInline(admin.StackedInline):
    model = ProductTranslation
    form = ProductTranslationForm
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    fields = ("language", "name", "ingredients", "allergens", "description")

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class ProductImageGaleriInline(admin.StackedInline):
    model = ImageGaleri
    fk_name = "product"
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 1
    fields = ("image", "image_preview", "alt_text", "order", "is_active")
    readonly_fields = ("image_preview",)
    ordering = ("order", "pk")
    verbose_name = "Galeri görseli"
    verbose_name_plural = "Ürün galerisi"

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}

    @admin.display(description="Önizleme")
    def image_preview(self, obj):
        return _render_admin_image(obj.image, size=120)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductTranslationInline, ProductImageGaleriInline]
    list_select_related = ("product_currency__currency",)
    list_display = (
        "image_preview",
        "display_name_admin",
        "category",
        "price",
        "is_available",
        "is_popular",
        "order",
        "display_prep_time",
    )
    list_filter = ("category", "is_available", "is_popular")
    list_editable = ("price", "is_available", "is_popular", "order")
    readonly_fields = ("image_preview_detail",)
    search_fields = (
        "slug",
        "translations__name",
        "translations__description",
    )
    fields = (
        "is_popular_choice",
        "category",
        "slug",
        ("price", "currency"),
        "prep_time",
        "image",
        "image_preview_detail",
        "is_available",
        "is_popular",
        "calories",
        "order",
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        currency = form.cleaned_data.get("currency")
        if currency:
            ProductCurrency.objects.update_or_create(
                product=obj,
                defaults={"currency": currency},
            )

    @admin.display(description="Görsel")
    def image_preview(self, obj):
        return self._render_image_preview(obj, size=48)

    @admin.display(description="Görsel önizleme")
    def image_preview_detail(self, obj):
        return self._render_image_preview(obj, size=120)

    def _render_image_preview(self, obj, size):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="height:{}px;width:{}px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
                size,
                size,
            )
        return "—"

    @admin.display(description="Ad")
    def display_name_admin(self, obj):
        return obj.display_name()

    @admin.display(description="Hazırlama Süresi", ordering="prep_time")
    def display_prep_time(self, obj):
        if obj.prep_time is None:
            return "—"
        return f"{obj.prep_time} dk"


@admin.register(ProductTranslation)
class ProductTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "product"
    form = ProductTranslationForm
    list_display = ("product", "language", "name")
    list_filter = ("language",)
    search_fields = ("name", "description", "product__slug")


class SiteSettingsTranslationInline(admin.StackedInline):
    model = SiteSettingsTranslation
    form = SiteSettingsTranslationForm
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    readonly_fields = ("favicon_preview", "logo_preview", "about_image_preview")
    fields = (
        "language",
        "title",
        "keywords",
        "description_title",
        "short_description",
        "description",
        "copyright",
        "hours_label",
        "weekday_days",
        "weekday_hours",
        "weekend_days",
        "weekend_hours",
        "hours_note",
        "favicon",
        "favicon_preview",
        "logo",
        "logo_preview",
        "about_image",
        "about_image_preview",
    )

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}

    @admin.display(description="Favicon önizleme")
    def favicon_preview(self, obj):
        return _render_admin_image(obj.favicon, size=32)

    @admin.display(description="Logo önizleme")
    def logo_preview(self, obj):
        return _render_admin_image(obj.logo, size=120)

    @admin.display(description="Hakkında görseli önizleme")
    def about_image_preview(self, obj):
        return _render_admin_image(obj.about_image, size=160)


class ContactTranslationInline(admin.StackedInline):
    model = ContactTranslation
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    fields = ("language", "label", "link_text", "value")

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class ContactInline(admin.StackedInline):
    model = Contact
    form = ContactInlineForm
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 1
    fields = (
        "contact_type",
        "icon",
        "language",
        "label",
        "link_text",
        "value",
        "priority",
        "is_active",
    )
    ordering = ("contact_type", "priority")
    show_change_link = True
    verbose_name = "İletişim bilgisi"
    verbose_name_plural = "İletişim bilgileri"

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class SiteHighlightTranslationInline(admin.StackedInline):
    model = SiteHighlightTranslation
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    fields = ("language", "title", "description")

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class SiteHighlightInline(admin.TabularInline):
    model = SiteHighlight
    extra = 1
    fields = ("order", "icon", "display_title_admin", "is_active")
    readonly_fields = ("display_title_admin",)
    ordering = ("order", "pk")
    show_change_link = True
    verbose_name = "Öne çıkan özellik"
    verbose_name_plural = "Öne çıkan özellikler"

    @admin.display(description="Başlık")
    def display_title_admin(self, obj):
        if not obj.pk:
            return "—"
        return obj.display_title()


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [SiteSettingsTranslationInline, SiteHighlightInline, ContactInline]
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "is_active", "frontend_public_access"),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        default_language = get_default_language()
        for inline in inline_instances:
            if isinstance(inline, ContactInline):
                if default_language:
                    inline.verbose_name_plural = (
                        f"İletişim bilgileri "
                        f"(varsayılan dil: {default_language.name_native} — {default_language.code})"
                    )
                else:
                    inline.verbose_name_plural = "İletişim bilgileri"
        return inline_instances

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)


@admin.register(SiteHighlight)
class SiteHighlightAdmin(admin.ModelAdmin):
    inlines = [SiteHighlightTranslationInline]
    list_display = ("settings", "display_title_admin", "icon", "order", "is_active")
    list_filter = ("is_active", "settings")
    list_editable = ("order", "is_active")
    search_fields = ("translations__title", "translations__description")
    fields = ("settings", "icon", "order", "is_active")

    @admin.display(description="Başlık")
    def display_title_admin(self, obj):
        return obj.display_title()


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = [ContactTranslationInline]
    list_display = (
        "settings",
        "contact_type",
        "icon",
        "display_label_admin",
        "display_value_admin",
        "priority",
        "is_active",
    )
    list_filter = ("settings", "contact_type", "is_active")
    list_editable = ("priority", "is_active")
    search_fields = (
        "translations__label",
        "translations__value",
    )
    ordering = ("settings", "contact_type", "priority", "pk")
    fields = ("settings", "contact_type", "icon", "priority", "is_active")

    @admin.display(description="Etiket")
    def display_label_admin(self, obj):
        return obj.display_label()

    @admin.display(description="Değer")
    def display_value_admin(self, obj):
        translation = obj.get_translation()
        return translation.value if translation else "—"


@admin.register(ContactTranslation)
class ContactTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "contact"
    list_display = ("contact", "language", "label", "link_text", "value")
    list_filter = ("language", "contact__contact_type")
    search_fields = ("label", "value", "contact__settings__name")


class CampaignTranslationInline(admin.StackedInline):
    model = CampaignTranslation
    form = CampaignTranslationForm
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    fields = ("language", "name", "badge", "description")

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class CampaignRuleInline(admin.StackedInline):
    model = CampaignRule
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 1
    fields = (
        "order",
        "rule_type",
        "discount_percent",
        "discount_amount",
        "buy_quantity",
        "reward_quantity",
        "item_ordinal",
    )
    ordering = ("order", "pk")
    verbose_name = "Kampanya kuralı"
    verbose_name_plural = "Kampanya kuralları"

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    inlines = [CampaignTranslationInline, CampaignRuleInline]
    list_display = (
        "display_name_admin",
        "slug",
        "product_count",
        "rule_count",
        "is_active",
        "starts_at",
        "ends_at",
        "priority",
    )
    list_filter = ("is_active",)
    list_editable = ("is_active", "priority")
    search_fields = ("slug", "translations__name", "translations__description")
    filter_horizontal = ("products",)
    readonly_fields = ("image_preview",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "slug",
                    "image",
                    "image_preview",
                    "is_active",
                    "priority",
                    ("starts_at", "ends_at"),
                    "products",
                ),
            },
        ),
    )

    @admin.display(description="Görsel önizleme")
    def image_preview(self, obj):
        return _render_admin_image(obj.image, size=120)

    @admin.display(description="Ad")
    def display_name_admin(self, obj):
        return obj.display_name()

    @admin.display(description="Ürün sayısı")
    def product_count(self, obj):
        return obj.products.count()

    @admin.display(description="Kural sayısı")
    def rule_count(self, obj):
        return obj.rules.count()


@admin.register(CampaignTranslation)
class CampaignTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "campaign"
    form = CampaignTranslationForm
    list_display = ("campaign", "language", "name", "badge")
    list_filter = ("language",)
    search_fields = ("name", "description", "campaign__slug")


class ChefRecommendationTranslationInline(admin.StackedInline):
    model = ChefRecommendationTranslation
    form = ChefRecommendationTranslationForm
    template = "admin/edit_inline/stacked_collapsible.html"
    extra = 0
    min_num = 1
    fields = ("language", "title", "summary", "description")

    class Media:
        css = {"all": ("admin/api/inline_collapsible.css",)}


class ChefRecommendationProductInline(admin.TabularInline):
    model = ChefRecommendationProduct
    extra = 1
    fields = ("order", "product")
    ordering = ("order", "pk")
    autocomplete_fields = ("product",)
    verbose_name = "Ürün"
    verbose_name_plural = "Ürünler"


@admin.register(ChefRecommendation)
class ChefRecommendationAdmin(admin.ModelAdmin):
    inlines = [ChefRecommendationTranslationInline, ChefRecommendationProductInline]
    list_display = (
        "display_title_admin",
        "slug",
        "status",
        "product_count",
        "image_preview",
    )
    list_filter = ("status", "product_links__product__category")
    list_editable = ("status",)
    search_fields = (
        "slug",
        "translations__title",
        "translations__summary",
        "translations__description",
        "product_links__product__slug",
        "product_links__product__translations__name",
    )
    readonly_fields = ("image_preview_detail",)
    fields = (
        "status",
        "slug",
        "image",
        "image_preview_detail",
    )

    @admin.display(description="Başlık")
    def display_title_admin(self, obj):
        return obj.display_title()

    @admin.display(description="Görsel")
    def image_preview(self, obj):
        return _render_admin_image(obj.image, size=48)

    @admin.display(description="Görsel önizleme")
    def image_preview_detail(self, obj):
        return _render_admin_image(obj.image, size=120)

    @admin.display(description="Ürün sayısı")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(ChefRecommendationTranslation)
class ChefRecommendationTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "chef_recommendation"
    form = ChefRecommendationTranslationForm
    list_display = ("chef_recommendation", "language", "title")
    list_filter = ("language",)
    search_fields = ("title", "summary", "description", "chef_recommendation__slug")


@admin.register(SiteSettingsTranslation)
class SiteSettingsTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "site_settings"
    form = SiteSettingsTranslationForm
    list_display = ("settings", "language", "title", "description_title")
    list_filter = ("language",)
    search_fields = ("title", "keywords", "description", "settings__name")
    readonly_fields = ("favicon_preview", "logo_preview", "about_image_preview")

    @admin.display(description="Favicon önizleme")
    def favicon_preview(self, obj):
        return _render_admin_image(obj.favicon, size=32)

    @admin.display(description="Logo önizleme")
    def logo_preview(self, obj):
        return _render_admin_image(obj.logo, size=120)

    @admin.display(description="Hakkında görseli önizleme")
    def about_image_preview(self, obj):
        return _render_admin_image(obj.about_image, size=160)


@admin.register(SiteHighlightTranslation)
class SiteHighlightTranslationAdmin(GroqTranslateAdminMixin, admin.ModelAdmin):
    groq_translation_handler = "site_highlight"
    list_display = ("highlight", "language", "title")
    list_filter = ("language",)
    search_fields = ("title", "description", "highlight__settings__name")


@admin.register(CampaignRule)
class CampaignRuleAdmin(admin.ModelAdmin):
    list_display = (
        "campaign",
        "rule_type",
        "order",
        "discount_percent",
        "buy_quantity",
        "reward_quantity",
        "item_ordinal",
    )
    list_filter = ("rule_type", "campaign")
    list_editable = ("order",)
    ordering = ("campaign", "order", "pk")
