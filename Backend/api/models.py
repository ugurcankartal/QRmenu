from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

from core.models import TimeStampedModel


def _build_image_upload_path(code, filename):
    return f"images/{code}/{filename}"


def product_image_upload_to(instance, filename):
    return _build_image_upload_path("products", filename)


def category_image_upload_to(instance, filename):
    return _build_image_upload_path("categories", filename)


def campaign_image_upload_to(instance, filename):
    return f"images/campaigns/{instance.pk or 'new'}/{filename}"


def chef_recommendation_image_upload_to(instance, filename):
    return f"images/chef-recommendations/{instance.pk or 'new'}/{filename}"


def image_galeri_upload_to(instance, filename):
    if instance.product_id:
        return f"images/products/gallery/{instance.product_id}/{filename}"
    if instance.category_id:
        return f"images/categories/gallery/{instance.category_id}/{filename}"
    return f"images/gallery/{filename}"


def image_category_upload_to(instance, filename):
    code = getattr(instance, "code", "gallery")
    return _build_image_upload_path(code, filename)


class Category(MPTTModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktif"
        INACTIVE = "inactive", "Deaktif"

    slug = models.SlugField(max_length=100, unique=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Statü",
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    order = models.PositiveIntegerField(default=0, editable=False)
    image = models.ImageField(
        upload_to=category_image_upload_to,
        blank=True,
        null=True,
        verbose_name="Görsel",
    )

    class MPTTMeta:
        order_insertion_by = ["order"]

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

    @classmethod
    def sync_sibling_orders(cls, parent_id):
        siblings = list(
            cls.objects.filter(parent_id=parent_id)
            .order_by("tree_id", "lft")
            .only("pk", "order")
        )
        updates = []
        for index, category in enumerate(siblings):
            if category.order != index:
                category.order = index
                updates.append(category)
        if updates:
            cls.objects.bulk_update(updates, ["order"])

    @classmethod
    def sync_all_orders(cls):
        parent_ids = cls.objects.values_list("parent_id", flat=True).distinct()
        for parent_id in parent_ids:
            cls.sync_sibling_orders(parent_id)

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def display_name(self, language_code=None):
        translation = self.get_translation(language_code)
        if translation:
            return translation.name
        return f"Category #{self.pk}"

    def save(self, *args, **kwargs):
        old_parent_id = None
        if self.pk:
            old_parent_id = (
                Category.objects.filter(pk=self.pk)
                .values_list("parent_id", flat=True)
                .first()
            )
        if self._state.adding:
            self.order = Category.objects.filter(parent_id=self.parent_id).count()

        super().save(*args, **kwargs)
        if not self.slug:
            translation = self.get_translation()
            if translation and translation.name:
                slug = slugify(translation.name, allow_unicode=True)
                if slug:
                    Category.objects.filter(pk=self.pk).update(slug=slug)
                    self.slug = slug

        Category.sync_sibling_orders(self.parent_id)
        if old_parent_id != self.parent_id:
            Category.sync_sibling_orders(old_parent_id)

    def delete(self, *args, **kwargs):
        parent_id = self.parent_id
        super().delete(*args, **kwargs)
        Category.sync_sibling_orders(parent_id)

    def __str__(self):
        name = self.display_name()
        if self.parent_id:
            return f"{self.parent.display_name()} > {name}"
        return name


class CategoryTranslation(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="Kategori",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="category_translations",
        verbose_name="Dil",
    )
    name = models.CharField(max_length=100, verbose_name="Ad")
    title = models.CharField(max_length=150, blank=True, verbose_name="Başlık")
    description = models.TextField(blank=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Kategori çevirisi"
        verbose_name_plural = "Kategori çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["category", "language"],
                name="unique_category_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.category.slug and self.language.is_default:
            slug = slugify(self.name, allow_unicode=True)
            if slug:
                Category.objects.filter(pk=self.category_id).update(slug=slug)


class Product(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Kategori",
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    prep_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Hazırlama Süresi",
        help_text="Dakika cinsinden.",
    )
    image = models.ImageField(
        upload_to=product_image_upload_to,
        blank=True,
        null=True,
        verbose_name="Görsel",
    )
    is_available = models.BooleanField(default=True, verbose_name="Satışta")
    is_popular_choice = models.BooleanField(
        default=False,
        verbose_name="Popüler Seçim",
        help_text="Ürün detayında popüler seçim rozeti gösterilir.",
    )
    is_popular = models.BooleanField(default=False, verbose_name="Popüler")
    calories = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Kalori",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def display_name(self, language_code=None):
        translation = self.get_translation(language_code)
        if translation:
            return translation.name
        return f"Product #{self.pk}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.order = Product.objects.filter(category_id=self.category_id).count()

        super().save(*args, **kwargs)
        if not self.slug:
            translation = self.get_translation()
            if translation and translation.name:
                slug = slugify(translation.name, allow_unicode=True)
                if slug:
                    Product.objects.filter(pk=self.pk).update(slug=slug)
                    self.slug = slug

    def __str__(self):
        return self.display_name()


class ImageGaleri(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="gallery_images",
        verbose_name="Kategori",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="gallery_images",
        verbose_name="Ürün",
    )
    image = models.ImageField(
        upload_to=image_galeri_upload_to,
        verbose_name="Görsel",
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Alt metin",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Görsel galerisi"
        verbose_name_plural = "Görsel galerileri"
        ordering = ["order", "pk"]

    def __str__(self):
        if self.alt_text:
            return self.alt_text
        if self.pk:
            return f"Görsel #{self.pk}"
        return "Yeni galeri görseli"

    def clean(self):
        super().clean()
        if not self.product_id and not self.category_id:
            raise ValidationError("Ürün veya kategori seçilmelidir.")
        if self.product_id and self.category_id:
            raise ValidationError("Ürün ve kategori aynı anda seçilemez.")

    def save(self, *args, **kwargs):
        if self.product_id:
            self.category = None
        elif self.category_id:
            self.product = None
        super().save(*args, **kwargs)


class ProductTranslation(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="Ürün",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="product_translations",
        verbose_name="Dil",
    )
    name = models.CharField(max_length=150, verbose_name="Ad")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    ingredients = models.JSONField(default=list, blank=True, verbose_name="İçindekiler")
    allergens = models.JSONField(default=list, blank=True, verbose_name="Alerjenler")

    class Meta:
        verbose_name = "Ürün çevirisi"
        verbose_name_plural = "Ürün çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "language"],
                name="unique_product_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.product.slug and self.language.is_default:
            slug = slugify(self.name, allow_unicode=True)
            if slug:
                Product.objects.filter(pk=self.product_id).update(slug=slug)


def settings_favicon_upload_to(instance, filename):
    code = instance.language.code if instance.language_id else "default"
    return f"settings/favicons/{code}/{filename}"


def settings_logo_upload_to(instance, filename):
    code = instance.language.code if instance.language_id else "default"
    return f"settings/logos/{code}/{filename}"


def settings_about_image_upload_to(instance, filename):
    code = instance.language.code if instance.language_id else "default"
    return f"settings/about/{code}/{filename}"


class SiteSettings(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        default="Varsayılan",
        verbose_name="Site adı",
        help_text="Yönetim panelinde ayırt etmek için dahili ad.",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    frontend_public_access = models.BooleanField(
        default=True,
        verbose_name="Ön yüz herkese açık",
        help_text="Kapalıyken yalnızca admin/supervisor grubundaki kullanıcılar giriş yaparak siteyi görüntüleyebilir.",
    )

    class Meta:
        verbose_name = "Site ayarı"
        verbose_name_plural = "Site ayarları"
        ordering = ["-is_active", "name"]

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def __str__(self):
        return self.name


class SiteSettingsTranslation(TimeStampedModel):
    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="Site ayarı",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="site_settings_translations",
        verbose_name="Dil",
    )
    title = models.CharField(max_length=200, verbose_name="Başlık")
    keywords = models.TextField(blank=True, verbose_name="Anahtar kelimeler")
    description_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Açıklama başlığı",
    )
    short_description = models.TextField(blank=True, verbose_name="Kısa açıklama")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    copyright = models.TextField(blank=True, verbose_name="Telif hakkı")
    hours_label = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Çalışma saatleri başlığı",
        help_text="Ön yüzde çalışma saatleri bölümünün başlığı. Örn: Hours, Çalışma Saatleri",
    )
    weekday_days = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Çalışma günleri",
        help_text="Örn: Pazartesi – Cuma",
    )
    weekday_hours = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Çalışma saatleri",
        help_text="Örn: 09:00 – 18:00",
    )
    weekend_days = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Hafta sonu çalışma günleri",
        help_text="Örn: Cumartesi",
    )
    weekend_hours = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Hafta sonu çalışma saatleri",
        help_text="Örn: 10:00 – 16:00",
    )
    hours_note = models.TextField(
        blank=True,
        verbose_name="Çalışma saatleri notu",
        help_text="Örn: Bayram günleri ve resmi tatillerde çalışma zamanı değişiklik gösterebilir.",
    )
    favicon = models.ImageField(
        upload_to=settings_favicon_upload_to,
        blank=True,
        null=True,
        verbose_name="Favicon",
    )
    logo = models.ImageField(
        upload_to=settings_logo_upload_to,
        blank=True,
        null=True,
        verbose_name="Logo",
    )
    about_image = models.ImageField(
        upload_to=settings_about_image_upload_to,
        blank=True,
        null=True,
        verbose_name="Hakkında hero görseli",
        help_text="Hakkında sayfası üst banner görseli. Boş bırakılırsa varsayılan dilin görseli kullanılır.",
    )

    class Meta:
        verbose_name = "Site ayarı çevirisi"
        verbose_name_plural = "Site ayarı çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["settings", "language"],
                name="unique_site_settings_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.title}"


class SiteHighlight(TimeStampedModel):
    class HighlightIcon(models.TextChoices):
        AWARD = "Award", "Ödül"
        CLOCK = "Clock", "Saat"
        MAP_PIN = "MapPin", "Konum"
        PHONE = "Phone", "Telefon"
        MAIL = "Mail", "E-posta"
        GLOBE = "Globe", "Dünya"
        LINK = "Link", "Bağlantı"
        SPARKLES = "Sparkles", "Parıltı"
        HEART = "Heart", "Kalp"
        USERS = "Users", "Kullanıcılar"
        STAR = "Star", "Yıldız"

    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="highlights",
        verbose_name="Site ayarı",
    )
    icon = models.CharField(
        max_length=30,
        choices=HighlightIcon.choices,
        default=HighlightIcon.AWARD,
        verbose_name="İkon",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Öne çıkan özellik"
        verbose_name_plural = "Öne çıkan özellikler"
        ordering = ["order", "pk"]

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def display_title(self, language_code=None):
        translation = self.get_translation(language_code)
        if translation and translation.title:
            return translation.title
        return f"Özellik #{self.pk}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.order = SiteHighlight.objects.filter(
                settings_id=self.settings_id,
            ).count()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_title()


class SiteHighlightTranslation(TimeStampedModel):
    highlight = models.ForeignKey(
        SiteHighlight,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="Öne çıkan özellik",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="site_highlight_translations",
        verbose_name="Dil",
    )
    title = models.CharField(max_length=150, verbose_name="Başlık")
    description = models.TextField(blank=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Öne çıkan özellik çevirisi"
        verbose_name_plural = "Öne çıkan özellik çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["highlight", "language"],
                name="unique_site_highlight_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.title}"


class Contact(TimeStampedModel):
    class ContactType(models.TextChoices):
        PHONE = "phone", "Telefon"
        FAX = "fax", "Faks"
        EMAIL = "email", "E-posta"
        ADDRESS = "address", "Adres"
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"
        TWITTER = "twitter", "X (Twitter)"
        WHATSAPP = "whatsapp", "WhatsApp"
        YOUTUBE = "youtube", "YouTube"
        LINKEDIN = "linkedin", "LinkedIn"
        TIKTOK = "tiktok", "TikTok"
        WEBSITE = "website", "Web sitesi"
        OTHER = "other", "Diğer"

    class ContactIcon(models.TextChoices):
        AUTO = "", "Otomatik (türe göre)"
        PHONE = "Phone", "Telefon"
        PRINTER = "Printer", "Faks"
        MAIL = "Mail", "E-posta"
        MAP_PIN = "MapPin", "Konum"
        INSTAGRAM = "Instagram", "Instagram"
        FACEBOOK = "Facebook", "Facebook"
        TWITTER = "Twitter", "X (Twitter)"
        MESSAGE_CIRCLE = "MessageCircle", "WhatsApp"
        YOUTUBE = "Youtube", "YouTube"
        LINKEDIN = "Linkedin", "LinkedIn"
        MUSIC = "Music", "TikTok"
        GLOBE = "Globe", "Web sitesi"
        LINK = "Link", "Diğer"

    CONTACT_TYPE_DEFAULT_ICONS = {
        ContactType.PHONE: ContactIcon.PHONE,
        ContactType.FAX: ContactIcon.PRINTER,
        ContactType.EMAIL: ContactIcon.MAIL,
        ContactType.ADDRESS: ContactIcon.MAP_PIN,
        ContactType.INSTAGRAM: ContactIcon.INSTAGRAM,
        ContactType.FACEBOOK: ContactIcon.FACEBOOK,
        ContactType.TWITTER: ContactIcon.TWITTER,
        ContactType.WHATSAPP: ContactIcon.MESSAGE_CIRCLE,
        ContactType.YOUTUBE: ContactIcon.YOUTUBE,
        ContactType.LINKEDIN: ContactIcon.LINKEDIN,
        ContactType.TIKTOK: ContactIcon.MUSIC,
        ContactType.WEBSITE: ContactIcon.GLOBE,
        ContactType.OTHER: ContactIcon.LINK,
    }

    settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Site ayarı",
    )
    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        verbose_name="Tür",
    )
    icon = models.CharField(
        max_length=30,
        choices=ContactIcon.choices,
        blank=True,
        verbose_name="İkon",
        help_text="Boş bırakılırsa türe göre otomatik seçilir.",
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Öncelik",
        help_text="Aynı türde birden fazla kayıt varsa düşük değer önce gelir.",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    NON_LINKABLE_CONTACT_TYPES = frozenset(
        {
            ContactType.PHONE,
            ContactType.EMAIL,
            ContactType.FAX,
            ContactType.ADDRESS,
        }
    )

    class Meta:
        verbose_name = "İletişim"
        verbose_name_plural = "İletişim bilgileri"
        ordering = ["contact_type", "priority", "pk"]

    def resolve_icon(self):
        if self.icon:
            return self.icon
        return self.CONTACT_TYPE_DEFAULT_ICONS.get(
            self.contact_type,
            self.ContactIcon.LINK,
        )

    @staticmethod
    def looks_like_url(value):
        if not value:
            return False
        normalized = value.strip().lower()
        return normalized.startswith(("http://", "https://", "www."))

    def get_display_text(self, language_code=None):
        translation = self.get_translation(language_code)
        if not translation:
            return ""
        if self.contact_type == self.ContactType.ADDRESS:
            return translation.value or ""
        link_text = (translation.link_text or "").strip()
        if link_text:
            return link_text
        return translation.value or ""

    def is_link_contact(self, language_code=None):
        if self.contact_type in self.NON_LINKABLE_CONTACT_TYPES:
            return False
        translation = self.get_translation(language_code)
        if not translation:
            return False
        return self.looks_like_url(translation.value)

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def display_label(self, language_code=None):
        translation = self.get_translation(language_code)
        if translation and translation.label:
            return translation.label
        return self.get_contact_type_display()

    def save(self, *args, **kwargs):
        if self._state.adding and self.priority == 0:
            self.priority = Contact.objects.filter(
                settings_id=self.settings_id,
                contact_type=self.contact_type,
            ).count()
        super().save(*args, **kwargs)

    def __str__(self):
        translation = self.get_translation()
        label = ""
        value = ""
        if translation:
            label = f"{translation.label}: " if translation.label else ""
            value = translation.value
        return f"{self.get_contact_type_display()} — {label}{value}"


class ContactTranslation(TimeStampedModel):
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="İletişim",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="contact_translations",
        verbose_name="Dil",
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Etiket",
        help_text="Örn: Ana hat, Şube, Destek",
    )
    link_text = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Görünen ad",
        help_text="URL için bağlantı metni (örn: @alt_fila). Boş bırakılırsa değer gösterilir.",
    )
    value = models.TextField(verbose_name="Değer")

    class Meta:
        verbose_name = "İletişim çevirisi"
        verbose_name_plural = "İletişim çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["contact", "language"],
                name="unique_contact_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.label or self.contact.get_contact_type_display()}"


class Campaign(TimeStampedModel):
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(
        upload_to=campaign_image_upload_to,
        blank=True,
        null=True,
        verbose_name="Görsel",
    )
    products = models.ManyToManyField(
        Product,
        related_name="campaigns",
        blank=True,
        verbose_name="Kapsanan ürünler",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    starts_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Başlangıç",
        help_text="Boş bırakılırsa hemen geçerli sayılır.",
    )
    ends_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Bitiş",
        help_text="Boş bırakılırsa süresiz geçerlidir.",
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Öncelik",
        help_text="Birden fazla kampanya çakışırsa yüksek değer önce değerlendirilir.",
    )

    class Meta:
        verbose_name = "Kampanya"
        verbose_name_plural = "Kampanyalar"
        ordering = ["-priority", "pk"]

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def display_name(self, language_code=None):
        translation = self.get_translation(language_code)
        if translation:
            return translation.name
        return f"Kampanya #{self.pk}"

    def clean(self):
        super().clean()
        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValidationError({"ends_at": "Bitiş, başlangıçtan sonra olmalıdır."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            translation = self.get_translation()
            if translation and translation.name:
                slug = slugify(translation.name, allow_unicode=True)
                if slug:
                    Campaign.objects.filter(pk=self.pk).update(slug=slug)
                    self.slug = slug

    def __str__(self):
        return self.display_name()


class CampaignTranslation(TimeStampedModel):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="Kampanya",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="campaign_translations",
        verbose_name="Dil",
    )
    name = models.CharField(max_length=150, verbose_name="Ad")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    badge = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Rozet metni",
        help_text="Örn: 1+1, %50",
    )

    class Meta:
        verbose_name = "Kampanya çevirisi"
        verbose_name_plural = "Kampanya çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "language"],
                name="unique_campaign_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.campaign.slug and self.language.is_default:
            slug = slugify(self.name, allow_unicode=True)
            if slug:
                Campaign.objects.filter(pk=self.campaign_id).update(slug=slug)


class CampaignRule(TimeStampedModel):
    class RuleType(models.TextChoices):
        PERCENTAGE = "percentage", "Ürün indirimi (%)"
        FIXED_AMOUNT = "fixed_amount", "Sabit tutar indirimi"
        BUY_X_GET_Y = "buy_x_get_y", "X al Y indirimli / bedava"
        NTH_ITEM = "nth_item", "N. ürün indirimi"

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="rules",
        verbose_name="Kampanya",
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RuleType.choices,
        verbose_name="Kural türü",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="İndirim (%)",
        help_text="Yüzde indirim, N. ürün veya bedava/indirimli ürün için kullanılır.",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="İndirim tutarı",
        help_text="Sabit tutar indirimi için.",
    )
    buy_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Alınacak adet (X)",
        help_text="X al Y kuralları için. Örn: 1 alana 1 bedava → 1",
    )
    reward_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Kazanılacak adet (Y)",
        help_text="X al Y kuralları için. Genelde 1.",
    )
    item_ordinal = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Ürün sırası (N)",
        help_text="N. ürün indirimi için. Örn: 2 → ikinci ürün, 3 → üçüncü ürün.",
    )

    class Meta:
        verbose_name = "Kampanya kuralı"
        verbose_name_plural = "Kampanya kuralları"
        ordering = ["order", "pk"]

    def __str__(self):
        return f"{self.get_rule_type_display()} ({self.order})"

    def clean(self):
        super().clean()
        errors = {}

        if self.rule_type == self.RuleType.PERCENTAGE:
            if self.discount_percent is None:
                errors["discount_percent"] = "Yüzde indirim değeri gerekli."
            elif self.discount_percent <= 0 or self.discount_percent > 100:
                errors["discount_percent"] = "İndirim %1 ile %100 arasında olmalıdır."

        elif self.rule_type == self.RuleType.FIXED_AMOUNT:
            if self.discount_amount is None:
                errors["discount_amount"] = "İndirim tutarı gerekli."
            elif self.discount_amount <= 0:
                errors["discount_amount"] = "İndirim tutarı sıfırdan büyük olmalıdır."

        elif self.rule_type == self.RuleType.BUY_X_GET_Y:
            if not self.buy_quantity or self.buy_quantity < 1:
                errors["buy_quantity"] = "Alınacak adet en az 1 olmalıdır."
            if not self.reward_quantity or self.reward_quantity < 1:
                errors["reward_quantity"] = "Kazanılacak adet en az 1 olmalıdır."
            if self.discount_percent is None:
                errors["discount_percent"] = (
                    "Bedava veya indirimli ürün için yüzde girin (100 = bedava)."
                )
            elif self.discount_percent < 0 or self.discount_percent > 100:
                errors["discount_percent"] = "İndirim %0 ile %100 arasında olmalıdır."

        elif self.rule_type == self.RuleType.NTH_ITEM:
            if not self.item_ordinal or self.item_ordinal < 2:
                errors["item_ordinal"] = "Ürün sırası en az 2 olmalıdır (2., 3. ürün …)."
            if self.discount_percent is None:
                errors["discount_percent"] = "N. ürün indirim yüzdesi gerekli."
            elif self.discount_percent <= 0 or self.discount_percent > 100:
                errors["discount_percent"] = "İndirim %1 ile %100 arasında olmalıdır."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self._state.adding and self.order == 0:
            self.order = CampaignRule.objects.filter(campaign_id=self.campaign_id).count()
        super().save(*args, **kwargs)


class ChefRecommendationProduct(TimeStampedModel):
    chef_recommendation = models.ForeignKey(
        "ChefRecommendation",
        on_delete=models.CASCADE,
        related_name="product_links",
        verbose_name="Şefin önerisi",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="chef_recommendation_links",
        verbose_name="Ürün",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Öncelik",
        help_text="Küçük değer ön yüzde önce gösterilir.",
    )

    class Meta:
        verbose_name = "Şefin önerisi ürünü"
        verbose_name_plural = "Şefin önerisi ürünleri"
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["chef_recommendation", "product"],
                name="unique_chef_recommendation_product",
            ),
        ]

    def __str__(self):
        return f"{self.chef_recommendation_id} → {self.product_id}"

    def save(self, *args, **kwargs):
        if self._state.adding and self.order == 0:
            self.order = ChefRecommendationProduct.objects.filter(
                chef_recommendation_id=self.chef_recommendation_id,
            ).count()
        super().save(*args, **kwargs)


class ChefRecommendation(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktif"
        INACTIVE = "inactive", "Deaktif"

    products = models.ManyToManyField(
        Product,
        through="ChefRecommendationProduct",
        related_name="chef_recommendations",
        blank=True,
        verbose_name="Ürünler",
    )
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Statü",
    )
    image = models.ImageField(
        upload_to=chef_recommendation_image_upload_to,
        blank=True,
        null=True,
        verbose_name="Görsel",
    )

    class Meta:
        verbose_name = "Şefin önerisi"
        verbose_name_plural = "Şefin önerileri"
        ordering = ["-pk"]

    def get_translation(self, language_code=None):
        from localization.services.language_resolver import resolve_active_language

        translations = self.translations.select_related("language")
        if language_code:
            translation = translations.filter(
                language__code=language_code,
                language__is_active=True,
            ).first()
            if translation:
                return translation

        language = resolve_active_language(language_code)
        if language:
            translation = translations.filter(language_id=language.pk).first()
            if translation:
                return translation

        return (
            translations.filter(language__is_default=True).first()
            or translations.order_by("language__sort_order", "language__code").first()
        )

    def display_title(self, language_code=None):
        translation = self.get_translation(language_code)
        if translation and translation.title:
            return translation.title
        return f"Şefin önerisi #{self.pk}"

    def __str__(self):
        return self.display_title()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            translation = self.get_translation()
            if translation and translation.title:
                slug = slugify(translation.title, allow_unicode=True)
                if slug:
                    ChefRecommendation.objects.filter(pk=self.pk).update(slug=slug)
                    self.slug = slug


class ChefRecommendationTranslation(TimeStampedModel):
    chef_recommendation = models.ForeignKey(
        ChefRecommendation,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="Şefin önerisi",
    )
    language = models.ForeignKey(
        "localization.Language",
        on_delete=models.CASCADE,
        related_name="chef_recommendation_translations",
        verbose_name="Dil",
    )
    title = models.CharField(max_length=150, verbose_name="Başlık")
    summary = models.TextField(blank=True, verbose_name="Ön açıklama")
    description = models.TextField(blank=True, verbose_name="Açıklama")

    class Meta:
        verbose_name = "Şefin önerisi çevirisi"
        verbose_name_plural = "Şefin önerisi çevirileri"
        constraints = [
            models.UniqueConstraint(
                fields=["chef_recommendation", "language"],
                name="unique_chef_recommendation_translation_per_language",
            ),
        ]

    def __str__(self):
        return f"{self.language.code}: {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.chef_recommendation.slug and self.language.is_default:
            slug = slugify(self.title, allow_unicode=True)
            if slug:
                ChefRecommendation.objects.filter(
                    pk=self.chef_recommendation_id,
                ).update(slug=slug)


class AdminModelMenuOrder(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_model_menu_orders",
        verbose_name="Kullanıcı",
    )
    app_label = models.CharField(max_length=100, verbose_name="Uygulama")
    model_name = models.CharField(max_length=100, verbose_name="Model")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Admin menü sırası"
        verbose_name_plural = "Admin menü sıraları"
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "app_label", "model_name"],
                name="unique_admin_model_menu_order",
            ),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.app_label}.{self.model_name} ({self.order})"


class AdminAppMenuOrder(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_app_menu_orders",
        verbose_name="Kullanıcı",
    )
    app_label = models.CharField(max_length=100, verbose_name="Uygulama")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Admin uygulama sırası"
        verbose_name_plural = "Admin uygulama sıraları"
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "app_label"],
                name="unique_admin_app_menu_order",
            ),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.app_label} ({self.order})"

