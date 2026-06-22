from rest_framework import serializers

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
    Product,
    ProductTranslation,
    SiteSettings,
    SiteSettingsTranslation,
    SiteHighlight,
    SiteHighlightTranslation,
)


def _normalize_tag_list(value):
    if isinstance(value, list):
        return [
            item.strip()
            for item in value
            if isinstance(item, str) and item.strip()
        ]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _absolute_media_url(obj, field_name, context):
    image = getattr(obj, field_name, None)
    if not image:
        return None
    request = context.get("request")
    url = image.url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


def _translation_media_with_default_fallback(
    settings_obj,
    field_name: str,
    context,
    language_code: str | None,
):
    translations = list(settings_obj.translations.all())

    def media_url(translation):
        return _absolute_media_url(translation, field_name, context)

    if language_code:
        exact = next(
            (
                translation
                for translation in translations
                if translation.language.code == language_code
                and translation.language.is_active
            ),
            None,
        )
        if exact:
            url = media_url(exact)
            if url:
                return url

    default = next(
        (translation for translation in translations if translation.language.is_default),
        None,
    )
    if default:
        url = media_url(default)
        if url:
            return url

    return None


class CategoryTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = CategoryTranslation
        fields = ["language", "name", "title", "description"]


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )
    children = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    translations = CategoryTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "title",
            "slug",
            "status",
            "description",
            "image_url",
            "parent",
            "children",
            "order",
            "level",
            "translations",
        ]
        read_only_fields = ["level"]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_name(self, obj):
        translation = self._get_translation(obj)
        return translation.name if translation else ""

    def get_title(self, obj):
        translation = self._get_translation(obj)
        return translation.title if translation else ""

    def get_description(self, obj):
        translation = self._get_translation(obj)
        return translation.description if translation else ""

    def get_image_url(self, obj):
        return _absolute_media_url(obj, "image", self.context)


class ProductTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = ProductTranslation
        fields = ["language", "name", "description", "ingredients", "allergens"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    category_name = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    allergens = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    currency_code = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()
    translations = ProductTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "ingredients",
            "allergens",
            "price",
            "prep_time",
            "currency_code",
            "currency_symbol",
            "image_url",
            "is_available",
            "is_popular",
            "is_popular_choice",
            "calories",
            "category",
            "category_name",
            "order",
            "translations",
        ]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_category_name(self, obj):
        if not obj.category_id:
            return ""
        translation = obj.category.get_translation(self.context.get("language_code"))
        return translation.name if translation else ""

    def get_name(self, obj):
        translation = self._get_translation(obj)
        return translation.name if translation else ""

    def get_description(self, obj):
        translation = self._get_translation(obj)
        return translation.description if translation else ""

    def get_ingredients(self, obj):
        translation = self._get_translation(obj)
        if not translation:
            return []
        return _normalize_tag_list(translation.ingredients)

    def get_allergens(self, obj):
        translation = self._get_translation(obj)
        if not translation:
            return []
        return _normalize_tag_list(translation.allergens)

    def _get_product_currency(self, obj):
        return getattr(obj, "product_currency", None)

    def get_currency_code(self, obj):
        product_currency = self._get_product_currency(obj)
        if product_currency:
            return product_currency.currency.code
        return None

    def get_currency_symbol(self, obj):
        product_currency = self._get_product_currency(obj)
        if product_currency:
            return product_currency.currency.symbol
        return None

    def get_image_url(self, obj):
        return _absolute_media_url(obj, "image", self.context)


class CampaignTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = CampaignTranslation
        fields = ["language", "name", "description", "badge"]


class CampaignRuleSerializer(serializers.ModelSerializer):
    rule_type_label = serializers.CharField(source="get_rule_type_display", read_only=True)

    class Meta:
        model = CampaignRule
        fields = [
            "id",
            "rule_type",
            "rule_type_label",
            "order",
            "discount_percent",
            "discount_amount",
            "buy_quantity",
            "reward_quantity",
            "item_ordinal",
        ]


class CampaignSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    product_ids = serializers.PrimaryKeyRelatedField(
        source="products",
        many=True,
        read_only=True,
    )
    products = ProductSerializer(many=True, read_only=True)
    rules = CampaignRuleSerializer(many=True, read_only=True)
    translations = CampaignTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "badge",
            "image_url",
            "is_active",
            "starts_at",
            "ends_at",
            "priority",
            "product_ids",
            "products",
            "rules",
            "translations",
        ]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_name(self, obj):
        translation = self._get_translation(obj)
        return translation.name if translation else ""

    def get_description(self, obj):
        translation = self._get_translation(obj)
        return translation.description if translation else ""

    def get_badge(self, obj):
        translation = self._get_translation(obj)
        return translation.badge if translation else ""

    def get_image_url(self, obj):
        return _absolute_media_url(obj, "image", self.context)


class ChefRecommendationTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = ChefRecommendationTranslation
        fields = ["language", "title", "summary", "description"]


class ChefRecommendationProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ChefRecommendationProduct
        fields = ["id", "order", "product"]


class ChefRecommendationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    product_links = ChefRecommendationProductSerializer(many=True, read_only=True)
    translations = ChefRecommendationTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = ChefRecommendation
        fields = [
            "id",
            "title",
            "summary",
            "slug",
            "description",
            "image_url",
            "product_links",
            "translations",
        ]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_title(self, obj):
        translation = self._get_translation(obj)
        return translation.title if translation else ""

    def get_summary(self, obj):
        translation = self._get_translation(obj)
        return translation.summary if translation else ""

    def get_description(self, obj):
        translation = self._get_translation(obj)
        return translation.description if translation else ""

    def get_image_url(self, obj):
        return _absolute_media_url(obj, "image", self.context)


class SiteSettingsTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)
    favicon_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    about_image_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettingsTranslation
        fields = [
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
            "favicon_url",
            "logo_url",
            "about_image_url",
        ]

    def get_favicon_url(self, obj):
        return _absolute_media_url(obj, "favicon", self.context)

    def get_logo_url(self, obj):
        return _absolute_media_url(obj, "logo", self.context)

    def get_about_image_url(self, obj):
        return _absolute_media_url(obj, "about_image", self.context)


class ContactTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = ContactTranslation
        fields = ["language", "label", "link_text", "value"]


class ContactSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="contact_type")
    icon = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    link_text = serializers.SerializerMethodField()
    display_text = serializers.SerializerMethodField()
    is_link = serializers.SerializerMethodField()
    translations = ContactTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "type",
            "icon",
            "label",
            "link_text",
            "value",
            "display_text",
            "is_link",
            "priority",
            "translations",
        ]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_icon(self, obj):
        return obj.resolve_icon()

    def get_label(self, obj):
        translation = self._get_translation(obj)
        if translation and translation.label:
            return translation.label
        return obj.get_contact_type_display()

    def get_link_text(self, obj):
        translation = self._get_translation(obj)
        return translation.link_text if translation else ""

    def get_value(self, obj):
        translation = self._get_translation(obj)
        return translation.value if translation else ""

    def get_display_text(self, obj):
        return obj.get_display_text(self.context.get("language_code"))

    def get_is_link(self, obj):
        return obj.is_link_contact(self.context.get("language_code"))


class SiteHighlightTranslationSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = SiteHighlightTranslation
        fields = ["language", "title", "description"]


class SiteHighlightSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    translations = SiteHighlightTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = SiteHighlight
        fields = [
            "id",
            "icon",
            "order",
            "title",
            "description",
            "translations",
        ]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_title(self, obj):
        translation = self._get_translation(obj)
        return translation.title if translation else ""

    def get_description(self, obj):
        translation = self._get_translation(obj)
        return translation.description if translation else ""


class SiteSettingsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()
    description_title = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    copyright = serializers.SerializerMethodField()
    hours_label = serializers.SerializerMethodField()
    weekday_days = serializers.SerializerMethodField()
    weekday_hours = serializers.SerializerMethodField()
    weekend_days = serializers.SerializerMethodField()
    weekend_hours = serializers.SerializerMethodField()
    hours_note = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    about_image_url = serializers.SerializerMethodField()
    translations = SiteSettingsTranslationSerializer(many=True, read_only=True)
    contacts = serializers.SerializerMethodField()
    highlights = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = [
            "id",
            "name",
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
            "favicon_url",
            "logo_url",
            "about_image_url",
            "translations",
            "contacts",
            "highlights",
        ]

    def _get_translation(self, obj):
        return obj.get_translation(self.context.get("language_code"))

    def get_title(self, obj):
        translation = self._get_translation(obj)
        return translation.title if translation else ""

    def get_keywords(self, obj):
        translation = self._get_translation(obj)
        return translation.keywords if translation else ""

    def get_description_title(self, obj):
        translation = self._get_translation(obj)
        return translation.description_title if translation else ""

    def get_short_description(self, obj):
        translation = self._get_translation(obj)
        return translation.short_description if translation else ""

    def get_description(self, obj):
        translation = self._get_translation(obj)
        return translation.description if translation else ""

    def get_copyright(self, obj):
        translation = self._get_translation(obj)
        return translation.copyright if translation else ""

    def get_hours_label(self, obj):
        translation = self._get_translation(obj)
        return translation.hours_label if translation else ""

    def get_weekday_days(self, obj):
        translation = self._get_translation(obj)
        return translation.weekday_days if translation else ""

    def get_weekday_hours(self, obj):
        translation = self._get_translation(obj)
        return translation.weekday_hours if translation else ""

    def get_weekend_days(self, obj):
        translation = self._get_translation(obj)
        return translation.weekend_days if translation else ""

    def get_weekend_hours(self, obj):
        translation = self._get_translation(obj)
        return translation.weekend_hours if translation else ""

    def get_hours_note(self, obj):
        translation = self._get_translation(obj)
        return translation.hours_note if translation else ""

    def get_favicon_url(self, obj):
        translation = self._get_translation(obj)
        if translation:
            return _absolute_media_url(translation, "favicon", self.context)
        return None

    def get_logo_url(self, obj):
        translation = self._get_translation(obj)
        if translation:
            return _absolute_media_url(translation, "logo", self.context)
        return None

    def get_about_image_url(self, obj):
        return _translation_media_with_default_fallback(
            obj,
            "about_image",
            self.context,
            self.context.get("language_code"),
        )

    def get_contacts(self, obj):
        contacts = obj.contacts.filter(is_active=True).prefetch_related(
            "translations__language",
        ).order_by(
            "contact_type",
            "priority",
            "pk",
        )
        return ContactSerializer(contacts, many=True, context=self.context).data

    def get_highlights(self, obj):
        highlights = obj.highlights.filter(is_active=True).prefetch_related(
            "translations__language",
        ).order_by("order", "pk")
        return SiteHighlightSerializer(highlights, many=True, context=self.context).data
