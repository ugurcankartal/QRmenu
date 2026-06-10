from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from mptt.forms import MPTTAdminForm

from currency.models import Currency

from .models import (
    CampaignTranslation,
    Category,
    ChefRecommendation,
    ChefRecommendationTranslation,
    Contact,
    ContactTranslation,
    ImageGaleri,
    SiteSettings,
    SiteSettingsTranslation,
    Product,
    ProductTranslation,
)
from .widgets import TagListFormField


def get_default_language():
    from localization.models import Language

    return (
        Language.objects.filter(is_active=True, is_default=True).first()
        or Language.objects.filter(is_active=True, code="tr").first()
        or Language.objects.filter(is_active=True).order_by("sort_order", "code").first()
    )


def get_contact_display_translation(contact, default_language=None):
    if not contact.pk:
        return None

    default_language = default_language or get_default_language()
    translations = list(
        contact.translations.select_related("language")
        .filter(language__is_active=True)
        .order_by("language__sort_order", "language__code")
    )
    if not translations:
        return None
    if len(translations) == 1:
        return translations[0]
    if default_language:
        for translation in translations:
            if translation.language_id == default_language.pk:
                return translation
    return translations[0]


class ImageGaleriAdminForm(forms.ModelForm):
    class Meta:
        model = ImageGaleri
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        product = cleaned_data.get("product")

        if not category and not product:
            raise forms.ValidationError("Ürün veya kategori seçilmelidir.")
        if category and product:
            raise forms.ValidationError("Ürün ve kategori aynı anda seçilemez.")

        return cleaned_data


class CategoryAdminForm(MPTTAdminForm):
    class Meta:
        model = Category
        fields = "__all__"


class ProductAdminForm(forms.ModelForm):
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.filter(is_active=True).order_by("order", "code"),
        required=True,
        label="Para Birimi",
        help_text="Ürün fiyatının para birimi.",
    )

    class Meta:
        model = Product
        fields = (
            "is_popular_choice",
            "category",
            "slug",
            "price",
            "prep_time",
            "image",
            "is_available",
            "is_popular",
            "calories",
            "order",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            product_currency = getattr(self.instance, "product_currency", None)
            if product_currency:
                self.fields["currency"].initial = product_currency.currency_id
        else:
            default_currency = Currency.objects.filter(
                code="TRY",
                is_active=True,
            ).first()
            if default_currency:
                self.fields["currency"].initial = default_currency.pk


class SiteSettingsTranslationForm(forms.ModelForm):
    class Meta:
        model = SiteSettingsTranslation
        fields = "__all__"
        widgets = {
            "description": CKEditor5Widget(config_name="campaign_description"),
        }


class ProductTranslationForm(forms.ModelForm):
    ingredients = TagListFormField(label="İçindekiler")
    allergens = TagListFormField(label="Alerjenler")

    class Meta:
        model = ProductTranslation
        fields = "__all__"


class CampaignTranslationForm(forms.ModelForm):
    class Meta:
        model = CampaignTranslation
        fields = "__all__"
        widgets = {
            "description": CKEditor5Widget(config_name="campaign_description"),
        }


class ChefRecommendationTranslationForm(forms.ModelForm):
    class Meta:
        model = ChefRecommendationTranslation
        fields = "__all__"
        widgets = {
            "description": CKEditor5Widget(config_name="campaign_description"),
        }


class ContactInlineForm(forms.ModelForm):
    language = forms.CharField(
        required=False,
        disabled=True,
        label="Dil",
        help_text="Etiket ve değer bu dile kaydedilir.",
    )
    label = forms.CharField(
        max_length=100,
        required=False,
        label="Etiket",
        help_text="Varsayılan dil için görünen etiket.",
    )
    link_text = forms.CharField(
        max_length=150,
        required=False,
        label="Görünen ad",
        help_text="URL için bağlantı metni (örn: @alt_fila).",
    )
    value = forms.CharField(
        required=False,
        label="Değer",
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Telefon, e-posta veya tam URL (örn: https://www.instagram.com/alt_fila/).",
    )

    class Meta:
        model = Contact
        fields = ("contact_type", "icon", "priority", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_new_contact = self.instance.pk is None
        self.default_language = get_default_language()
        if self.default_language:
            language_hint = f" ({self.default_language.code})"
            self.fields["label"].label = f"Etiket{language_hint}"
            self.fields["link_text"].label = f"Görünen ad{language_hint}"
            self.fields["value"].label = f"Değer{language_hint}"
        else:
            self.fields["language"].initial = "—"

        if self.is_new_contact:
            if self.default_language:
                self.fields["language"].initial = (
                    f"{self.default_language.name_native} — {self.default_language.code}"
                )
            self.fields["language"].help_text = (
                "Yeni kayıt varsayılan dil ile oluşturulur."
            )
        else:
            display_translation = get_contact_display_translation(
                self.instance,
                self.default_language,
            )
            if display_translation:
                display_language = display_translation.language
                language_hint = f" ({display_language.code})"
                self.fields["language"].initial = (
                    f"{display_language.name_native} — {display_language.code}"
                )
                self.fields["label"].label = f"Etiket{language_hint}"
                self.fields["link_text"].label = f"Görünen ad{language_hint}"
                self.fields["value"].label = f"Değer{language_hint}"
                self.fields["label"].initial = display_translation.label
                self.fields["link_text"].initial = display_translation.link_text
                self.fields["value"].initial = display_translation.value
            else:
                self.fields["language"].initial = "—"

            self.fields["language"].help_text = (
                "Mevcut çeviriler korunur. Düzenlemek için Değiştir linkini kullanın."
            )
            for field_name in ("label", "link_text", "value"):
                self.fields[field_name].disabled = True
                self.fields[field_name].required = False

    def save_default_language_translation(self, contact):
        if not self.is_new_contact:
            return
        if not contact.pk or not self.default_language:
            return
        if not hasattr(self, "cleaned_data"):
            return

        ContactTranslation.objects.update_or_create(
            contact=contact,
            language=self.default_language,
            defaults={
                "label": self.cleaned_data.get("label", ""),
                "link_text": self.cleaned_data.get("link_text", ""),
                "value": self.cleaned_data.get("value", ""),
            },
        )

    def save(self, commit=True):
        contact = super().save(commit=commit)
        if commit and self.is_new_contact:
            self.save_default_language_translation(contact)
        return contact
